// RIDI 웹 프록시 테스트 엔진 + 컨트롤 패널. 순수 Node.js(http), 외부 의존성 없음 (Node 18+).
// 플로우: 사용자가 "proxy" → 패널(/__qa) 실행 → 값 입력 + [테스트 시작] 클릭
//        → 엔진에 start 신호 적재 → Claude가 /__proxy/signal 폴링으로 감지 → 테스트 실행(페이지 열기·조작확인·스샷)
//        → [테스트 종료] 클릭 → stop 신호 + 조작 비활성.
// - 리버스 프록시 + 환경(stage/canary/prod) 헤더 주입 + 응답 x-ridi-environment 검증
// - rules.json 규칙(JSON dot-path / 텍스트 find→with)으로 응답 조작. 모바일 mitm_addon.py 와 공유.
// - 기존 dev.ridi.io 프록시(server.js)와 독립(포트·규칙파일 다름).
"use strict";

const http = require("node:http");
const fs = require("node:fs");
const path = require("node:path");
const os = require("node:os");

const PORT = process.env.PORT ? Number(process.env.PORT) : 3001;
const UPSTREAM_ORIGIN = process.env.UPSTREAM || "https://ridibooks.com";
const RULES_PATH = process.env.RULES_PATH || path.join(__dirname, "rules.json");
const MOBILE_APIS_PATH = process.env.MOBILE_APIS_PATH || path.join(__dirname, "mobile_apis.json"); // mitm_addon 이 기록한 앱 API 탐색 목록
const LOCAL_ORIGIN = `http://localhost:${PORT}`;
const MOBILE_PORT = process.env.MOBILE_PORT ? Number(process.env.MOBILE_PORT) : 8888; // mitmproxy 리슨 포트(모바일 프록시 안내용)

// 맥의 Wi-Fi LAN IP 감지. 휴대폰은 VPN이 아니라 같은 Wi-Fi LAN으로 맥에 붙으므로 en0(Wi-Fi) 우선.
// 와이파이가 바뀌면 IP도 바뀌니 요청마다 새로 계산한다(하드코딩 금지).
function detectLocalWifiIp() {
  const ifaces = os.networkInterfaces();
  const pick = (name) => (ifaces[name] || []).find((a) => a.family === "IPv4" && !a.internal);
  // 1순위: en0(맥 Wi-Fi)
  const en0 = pick("en0");
  if (en0) return en0.address;
  // 2순위: en1 등 다른 en* 유선/무선
  for (const name of Object.keys(ifaces)) {
    if (/^en\d+$/.test(name)) { const a = pick(name); if (a) return a.address; }
  }
  // 3순위: 사설 LAN 대역 아무거나(utun/VPN 터널은 제외)
  for (const name of Object.keys(ifaces)) {
    if (/^(utun|ppp|ipsec|tun)/.test(name)) continue;
    const a = (ifaces[name] || []).find((x) => x.family === "IPv4" && !x.internal && /^(10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.)/.test(x.address));
    if (a) return a.address;
  }
  return "";
}

let targetEnv = (process.env.TARGET_ENV || "prod").toLowerCase();
let headerInject = String(process.env.HEADER_INJECT || "false") === "true";
let manipEnabled = true; // 테스트 시작/종료 = 조작 활성/비활성
let platform = "web"; // web | aos | ios (시작 시 웹=Playwright / 모바일=mitmproxy+appium 분기)
let loginNeeded = false; // 로그인 후 진행 여부 (패널 입력)
let loginId = "", loginPw = ""; // 패널에서 받은 로그인 크리덴셜(메모리만, rules.json/state PW 미노출)
let mobileIpOverride = ""; // 와이파이 변경 등으로 자동감지 IP가 틀릴 때 패널에서 수동 입력(빈값=자동감지 사용)
let mobileTarget = "app"; // 모바일 대상 유형: app(네이티브 앱) | mweb(모바일 웹 브라우저). aos/ios일 때만 의미
let mobileBrowser = ""; // 모바일웹 브라우저: chrome|samsung|firefox|safari 등. mweb일 때만 의미
let lastVerifiedEnv = null;
let pendingSignal = null; // 패널 버튼 → {action:'start'|'stop', target, ts} ; Claude가 폴링 소비
let testStatus = { state: "idle", message: "", verifiedEnv: null, screenshotFile: null, ts: 0 }; // Claude→패널 결과 피드백

const ENV_HEADERS = {
  stage: { "x-ridi-enforced-env": "stage", "x-ridi-env-overlay": "stage" },
  canary: { "x-ridi-backends-canary-routing": "true", "x-ridi-env-overlay": "canary" },
  prod: {},
};

let RULES = loadRules();

function loadRules() {
  try {
    const parsed = JSON.parse(fs.readFileSync(RULES_PATH, "utf8"));
    const rules = Array.isArray(parsed) ? parsed : parsed.rules || [];
    return rules.filter((r) => r && r.match && r.match.path);
  } catch (_) { return []; }
}
function saveRules() { fs.writeFileSync(RULES_PATH, JSON.stringify({ rules: RULES }, null, 2), "utf8"); }

function escapeRegExp(s) { return String(s).replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }
function toPathname(input) {
  let p = String(input || "").trim();
  if (/^https?:\/\//i.test(p)) { try { p = new URL(p).pathname; } catch (_) {} }
  if (!p) return "";
  if (!p.startsWith("/")) p = "/" + p;
  return p;
}

function parsePath(p) {
  const out = [];
  for (const raw of String(p).split(".")) {
    const m = raw.match(/^([^\[]*)((?:\[\d*\])*)$/);
    if (!m) { out.push(raw); continue; }
    if (m[1]) out.push(m[1]);
    for (const b of m[2].match(/\[\d*\]/g) || []) { const inner = b.slice(1, -1); out.push(inner === "" ? "[]" : inner); }
  }
  return out;
}
function setAtPath(node, tokens, value) {
  if (node === null || node === undefined) return;
  const [tok, ...rest] = tokens;
  if (tok === "[]") { if (Array.isArray(node)) for (const el of node) if (rest.length) setAtPath(el, rest, value); return; }
  const key = /^\d+$/.test(tok) ? Number(tok) : tok;
  if (rest.length === 0) { if (typeof node === "object") node[key] = value; return; }
  setAtPath(node[key], rest, value);
}
function applyJsonOverrides(body, overrides) {
  for (const ov of overrides || []) if (ov && ov.field !== undefined) setAtPath(body, parsePath(ov.field), ov.value);
  return body;
}
function applyTextReplaces(text, replaces) {
  let out = text;
  for (const r of replaces || []) {
    let re;
    if (r.pattern) { try { re = new RegExp(r.pattern, r.flags || "g"); } catch (_) { continue; } }
    else if (r.find) re = new RegExp(escapeRegExp(r.find), r.flags || "g");
    else continue;
    out = out.replace(re, r.with ?? "");
  }
  return out;
}
function matchRule(rule, method, pathname) {
  const m = rule.match;
  if (m.method && m.method.toUpperCase() !== method.toUpperCase()) return false;
  try { return new RegExp(m.path).test(pathname); } catch (_) { return false; }
}
function rewriteLocation(loc) {
  try { const u = new URL(loc, UPSTREAM_ORIGIN); if (u.hostname.endsWith("ridibooks.com")) return LOCAL_ORIGIN + u.pathname + u.search + u.hash; return loc; }
  catch (_) { return loc; }
}
function sanitizeCookie(c) { return c.replace(/;\s*Domain=[^;]*/gi, "").replace(/;\s*Secure/gi, "").replace(/;\s*SameSite=[^;]*/gi, "; SameSite=Lax"); }
function buildUpstreamHeaders(req) {
  const h = { accept: req.headers["accept"] || "*/*", "accept-language": req.headers["accept-language"] || "ko-KR,ko;q=0.9", "user-agent": req.headers["user-agent"] || "Mozilla/5.0" };
  if (req.headers["content-type"]) h["content-type"] = req.headers["content-type"];
  if (req.headers["cookie"]) h["cookie"] = req.headers["cookie"];
  if (req.headers["authorization"]) h["authorization"] = req.headers["authorization"];
  if (headerInject) Object.assign(h, ENV_HEADERS[targetEnv] || {});
  return h;
}

function sendJson(res, status, obj) {
  const payload = JSON.stringify(obj, null, 2);
  res.writeHead(status, { "content-type": "application/json; charset=utf-8", "content-length": Buffer.byteLength(payload) });
  res.end(payload);
}
function readJson(req) {
  return new Promise((resolve) => { let d = ""; req.on("data", (c) => { d += c; if (d.length > 2e6) resolve({}); }); req.on("end", () => { try { resolve(JSON.parse(d || "{}")); } catch (_) { resolve({}); } }); req.on("error", () => resolve({})); });
}
function readRawBody(req) {
  return new Promise((resolve) => { const chunks = []; req.on("data", (c) => chunks.push(c)); req.on("end", () => resolve(Buffer.concat(chunks))); req.on("error", () => resolve(Buffer.alloc(0))); });
}
function coerce(v) { if (typeof v !== "string") return v; const t = v.trim(); if (t === "") return ""; try { return JSON.parse(t); } catch (_) { return v; } }
function ruleTargetUrl(r) { const p = r.target || String(r.match.path).replace(/^\^/, "").replace(/\\(.)/g, "$1"); return LOCAL_ORIGIN + p; }

function stateObj() {
  const localIpAuto = detectLocalWifiIp();
  const mobileIp = mobileIpOverride || localIpAuto;
  return { upstream: UPSTREAM_ORIGIN, port: PORT, rulesPath: RULES_PATH, platform, targetEnv, headerInject, manipEnabled, injectedHeaders: headerInject ? ENV_HEADERS[targetEnv] || {} : {}, loginNeeded, loginId, hasLoginPw: !!loginPw, lastVerifiedEnv, ruleCount: RULES.length, rules: RULES, testStatus,
    // 모바일 프록시(mitmproxy) 연결 정보 — Claude·사용자 공유
    localIpAuto, mobileIpOverride, mobileIp, mobilePort: MOBILE_PORT, mobileProxy: mobileIp ? `${mobileIp}:${MOBILE_PORT}` : "",
    // 테스트 대상 유형: platform(web/aos/ios) + mobileTarget(app/mweb) + mobileBrowser
    mobileTarget, mobileBrowser };
}

async function handleApi(req, res, pathname) {
  if (req.method === "GET" && pathname === "/__proxy/state") return sendJson(res, 200, stateObj());
  if (req.method === "GET" && pathname === "/__proxy/reload") { RULES = loadRules(); return sendJson(res, 200, stateObj()); }

  // Claude 폴링용 신호 소비(읽으면 비움)
  if (req.method === "GET" && pathname === "/__proxy/signal") { const s = pendingSignal; pendingSignal = null; return sendJson(res, 200, { signal: s }); }

  if (req.method === "POST" && pathname === "/__proxy/config") {
    const b = await readJson(req);
    if (b.targetEnv && ENV_HEADERS[b.targetEnv]) targetEnv = b.targetEnv;
    if (typeof b.headerInject === "boolean") headerInject = b.headerInject;
    if (["web", "aos", "ios"].includes(b.platform)) platform = b.platform;
    if (typeof b.loginNeeded === "boolean") loginNeeded = b.loginNeeded;
    if (b.loginId !== undefined) loginId = String(b.loginId);
    if (b.loginPw !== undefined) loginPw = String(b.loginPw);
    if (b.mobileIpOverride !== undefined) mobileIpOverride = String(b.mobileIpOverride).trim(); // 빈 문자열 = 자동감지로 복귀
    if (["app", "mweb"].includes(b.mobileTarget)) mobileTarget = b.mobileTarget;
    if (b.mobileBrowser !== undefined) mobileBrowser = String(b.mobileBrowser);
    return sendJson(res, 200, stateObj());
  }
  // 테스트 시작/종료 버튼 → 신호 적재 + 조작 활성 토글
  if (req.method === "POST" && pathname === "/__proxy/run") {
    const b = await readJson(req);
    const action = b.action === "stop" ? "stop" : "start";
    manipEnabled = action === "start";
    let target = b.target || "";
    if (!target && RULES.length) target = ruleTargetUrl(RULES[RULES.length - 1]);
    pendingSignal = { action, platform, mobileTarget, mobileBrowser, mobileProxy: (mobileIpOverride || detectLocalWifiIp()) ? `${mobileIpOverride || detectLocalWifiIp()}:${MOBILE_PORT}` : "", target, targetEnv, headerInject, loginNeeded, loginId, loginPw, ts: Date.now() };
    if (action === "start") testStatus = { state: "running", message: "Claude가 테스트를 실행 중입니다…", verifiedEnv: null, screenshotFile: null, ts: Date.now() };
    else testStatus = { state: "idle", message: "테스트 종료 — 조작 OFF(원본)", verifiedEnv: null, screenshotFile: testStatus.screenshotFile, ts: Date.now() };
    return sendJson(res, 200, { ok: true, action, target, manipEnabled });
  }
  // Claude → 패널 결과 피드백
  if (req.method === "POST" && pathname === "/__proxy/result") {
    const b = await readJson(req);
    testStatus = { state: b.state || "done", message: b.message || "", verifiedEnv: b.verifiedEnv || null, screenshotFile: b.screenshotFile || testStatus.screenshotFile, ts: Date.now() };
    return sendJson(res, 200, { ok: true });
  }
  // 최신 결과 스크린샷 서빙 (패널 <img>)
  if (req.method === "GET" && pathname === "/__proxy/screenshot") {
    try {
      if (testStatus.screenshotFile && fs.existsSync(testStatus.screenshotFile)) {
        const img = fs.readFileSync(testStatus.screenshotFile);
        res.writeHead(200, { "content-type": "image/png", "content-length": img.length, "cache-control": "no-store" });
        res.end(img); return;
      }
    } catch (_) {}
    res.writeHead(404, { "content-type": "text/plain" }); res.end("no screenshot"); return;
  }
  if (req.method === "POST" && pathname === "/__proxy/rules") {
    const b = await readJson(req);
    const id = String(b.id || "").trim() || "rule-" + (RULES.length + 1);
    const pn = toPathname(b.path);
    if (!pn) return sendJson(res, 400, { error: "path_required" });
    const rule = { id, desc: b.desc || "", target: pn, match: { method: (b.method || "GET").toUpperCase(), path: "^" + escapeRegExp(pn) } };
    if (b.type === "json") { rule.type = "json"; rule.overrides = [{ field: b.field, value: coerce(b.value) }]; }
    else { rule.type = "text"; rule.replace = [{ find: b.find, with: b.with ?? "" }]; }
    const idx = RULES.findIndex((r) => r.id === id);
    if (idx >= 0) RULES[idx] = rule; else RULES.push(rule);
    saveRules();
    return sendJson(res, 200, stateObj());
  }
  if (req.method === "DELETE" && pathname === "/__proxy/rules") {
    const id = new URL(req.url, "http://x").searchParams.get("id");
    RULES = RULES.filter((r) => r.id !== id); saveRules();
    return sendJson(res, 200, stateObj());
  }
  // 모바일 앱 API 탐색 목록 (mitm_addon.py 가 mobile_apis.json 에 기록) — 패널 "📱 모바일 API 탐색"이 폴링
  if (req.method === "GET" && pathname === "/__proxy/mobile-apis") {
    try {
      if (fs.existsSync(MOBILE_APIS_PATH)) return sendJson(res, 200, JSON.parse(fs.readFileSync(MOBILE_APIS_PATH, "utf8")));
    } catch (_) {}
    return sendJson(res, 200, { apis: [] });
  }
  if (req.method === "DELETE" && pathname === "/__proxy/mobile-apis") {
    try { fs.writeFileSync(MOBILE_APIS_PATH, JSON.stringify({ apis: [] })); } catch (_) {}
    return sendJson(res, 200, { apis: [] });
  }
  return sendJson(res, 404, { error: "not_found" });
}

function renderPanel() {
  return `<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>RIDI 프록시 컨트롤 패널</title>
<style>
*{box-sizing:border-box}body{font-family:-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Segoe UI",sans-serif;margin:0;background:#f6f7f9;color:#1a1d21}
.wrap{max-width:1000px;margin:0 auto;padding:28px 20px 80px}h1{font-size:21px;margin:0 0 4px}.sub{color:#8b95a1;font-size:13px}
.panel{background:#fff;border:1px solid #e3e6ea;border-radius:14px;padding:20px;margin:18px 0}.panel h2{font-size:14px;margin:0 0 14px}
.row{display:flex;gap:12px;flex-wrap:wrap;align-items:end}
label{display:flex;flex-direction:column;gap:5px;font-size:12px;color:#8b95a1;flex:1;min-width:140px}
input,select{border:1px solid #e3e6ea;border-radius:8px;padding:9px 10px;font-size:14px;width:100%;background:#fff}
input:focus,select:focus{outline:none;border-color:#1f6feb;box-shadow:0 0 0 3px rgba(31,111,235,.12)}
.btn{border:0;border-radius:8px;padding:9px 16px;font-size:14px;font-weight:600;cursor:pointer}
.btn.primary{background:#1f6feb;color:#fff}.btn.ghost{background:#eef1f4;color:#1a1d21}.btn.danger{background:#fff;color:#d1242f;border:1px solid #f0c2c5}
.btn.start{background:#1a7f37;color:#fff;font-size:16px;padding:12px 26px}.btn.stop{background:#d1242f;color:#fff;font-size:16px;padding:12px 26px}
.btn.sm{padding:6px 10px;font-size:12px}
.cards{display:flex;gap:12px;flex-wrap:wrap}.card{background:#fff;border:1px solid #e3e6ea;border-radius:12px;padding:12px 16px;flex:1;min-width:150px}
.card .k{color:#8b95a1;font-size:12px}.card .v{font-size:16px;font-weight:700;margin-top:3px;word-break:break-all}
.envbadge{display:inline-block;padding:2px 8px;border-radius:6px;font-size:12px;font-weight:700}
.env-canary{background:#fff4d6;color:#8a6d00}.env-stage{background:#ffe0e0;color:#c0392b}.env-prod{background:#e5f0ff;color:#1a5fd0}
.run-state{font-weight:700}.on{color:#1a7f37}.off{color:#8b95a1}
table{width:100%;border-collapse:collapse;font-size:13px;margin-top:6px}th,td{padding:9px 8px;border-bottom:1px solid #eef1f4;text-align:left;vertical-align:top}
th{color:#8b95a1;font-size:12px}td.mono{font-family:ui-monospace,Menlo,monospace;font-size:12px;word-break:break-all}
.hint{color:#8b95a1;font-size:12px;margin-top:8px}.hide{display:none}
.mode-banner{border-radius:10px;padding:10px 14px;font-size:13px;margin:14px 0}
.mode-banner.mode-web{background:#e5f0ff;color:#1a5fd0;border:1px solid #bcd4ff}
.mode-banner.mode-mobile{background:#e9f9ee;color:#1a7f37;border:1px solid #b6e6c4}
.only-web,.only-mobile{display:none}
body.m-web .only-web{display:block}body.m-mobile .only-mobile{display:block}
.hint.only-web,.hint.only-mobile{margin-top:8px}
#toast{position:fixed;left:50%;bottom:26px;transform:translateX(-50%) translateY(20px);background:#1a1d21;color:#fff;padding:10px 18px;border-radius:10px;font-size:14px;opacity:0;pointer-events:none;transition:.25s}#toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
</style></head><body><div class="wrap">
<h1>RIDI 프록시 컨트롤 패널</h1>
<div class="sub">값 입력 후 [테스트 시작]을 누르면 Claude가 감지해 조작 테스트를 실행합니다. 규칙은 rules.json 에 저장되어 웹·모바일(mitmproxy)이 공유합니다.</div>

<div id="mode-banner" class="mode-banner mode-web">현재 모드: <b id="mode-label">웹 (Playwright)</b> <span id="mode-desc"></span></div>

<div class="panel"><h2>① 플랫폼 &amp; 환경</h2>
<div class="cards" style="margin-bottom:14px">
<div class="card"><div class="k">업스트림</div><div class="v" id="c-up">-</div></div>
<div class="card"><div class="k">검증된 환경 (응답헤더)</div><div class="v" id="c-verified">-</div></div>
<div class="card"><div class="k">조작 상태</div><div class="v"><span id="c-manip" class="run-state">-</span></div></div>
</div>
<div class="row">
<label>테스트 대상<select id="in-target"><option value="pcweb">PC 웹 (Playwright)</option><option value="mweb">모바일 웹 (브라우저)</option><option value="app">모바일 앱</option></select></label>
<label id="lbl-os" class="hide">OS<select id="in-os"><option value="aos">AOS</option><option value="ios">iOS</option></select></label>
<label id="lbl-browser" class="hide">브라우저<select id="in-browser"></select></label>
<label>테스트 환경<select id="in-env"><option value="prod">prod</option><option value="stage">stage</option><option value="canary">canary</option></select></label>
<label style="flex:0 0 auto;min-width:auto">헤더 주입<select id="in-inject"><option value="true">ON (헤더 주입)</option><option value="false">OFF (VPN 전환)</option></select></label>
<button class="btn ghost" id="btn-env">적용</button>
</div>
<div class="hint">대상을 바꾸면 아래 구성이 그에 맞게 정리됩니다(웹=브라우저 자동화 / 모바일=휴대폰 프록시·CA). stage/canary 는 보통 헤더주입 ON. 적용 후 대상 새로고침 → 좌상단 띠지 + 위 "검증된 환경"으로 확인.</div>
</div>

<div class="panel only-mobile" id="panel-mobile"><h2>② 모바일 프록시 연결 (mitmproxy)</h2>
<div class="cards" style="margin-bottom:14px">
<div class="card" style="flex:2"><div class="k">📱 휴대폰 Wi-Fi 프록시에 입력할 주소</div><div class="v" id="c-mobileproxy" style="color:#1a7f37">-</div></div>
<div class="card"><div class="k">자동 감지된 맥 IP (en0)</div><div class="v" id="c-localip">-</div></div>
<div class="card"><div class="k">mitmproxy 포트</div><div class="v" id="c-mport">-</div></div>
</div>
<div class="row">
<label style="flex:1">IP 수동 입력 (와이파이 변경 시)<input id="in-mobileip" placeholder="비우면 자동 감지값 사용 (예: 10.10.104.79)"></label>
<button class="btn ghost" id="btn-mobileip">IP 적용</button>
</div>
<div class="hint">PC와 휴대폰을 <b>같은 Wi-Fi</b>에 두세요. 자동 감지가 틀리면 위에 수동 입력 → [IP 적용]. 이 값은 Claude도 <code>/__proxy/state</code>로 함께 읽습니다.</div>
<div class="hint" id="mobile-note"></div>
</div>

<div class="panel only-web"><h2>③ 로그인 (웹 전용, 필요 시)</h2>
<div class="row">
<label style="flex:0 0 auto;min-width:auto">로그인 사용<select id="in-login-needed"><option value="false">OFF (비로그인)</option><option value="true">ON (로그인 후 진행)</option></select></label>
<label style="flex:1">아이디<input id="in-login-id" autocomplete="off" placeholder="리디 아이디"></label>
<label style="flex:1">비밀번호<input id="in-login-pw" type="password" autocomplete="new-password" placeholder="비밀번호"></label>
<button class="btn ghost" id="btn-login">저장</button>
</div>
<div class="hint">로그인 사용 ON + 계정 입력 후 저장 → [테스트 시작] 시 Claude가 프록시 경유로 직접 로그인한 뒤 조작 테스트를 진행합니다. (개인화·소장 지면 검증용) 비밀번호는 엔진 메모리에만 두고 파일/상태로 노출하지 않습니다. <b>모바일 앱은 앱에서 직접 로그인</b>하세요(이 패널 불필요).</div>
</div>

<div class="panel" id="panel-mapi"><h2>📱 모바일 API 탐색 (앱 트래픽)</h2>
<div class="row" style="margin-bottom:6px;align-items:center">
<button class="btn ghost sm" id="btn-mapi-refresh">🔄 새로고침</button>
<button class="btn ghost sm" id="btn-mapi-mark">🕒 여기부터 (진입 후 호출만)</button>
<button class="btn ghost sm" id="btn-mapi-all">전체 보기</button>
<button class="btn danger sm" id="btn-mapi-clear">🗑 초기화</button>
<span class="hint" id="mapi-status" style="margin:0 0 0 auto"></span>
</div>
<table><thead><tr><th>메서드</th><th>경로 / operation</th><th>환경</th><th>상태</th><th>횟수</th><th></th></tr></thead><tbody id="mapi-tbody"></tbody></table>
<div class="hint" id="mapi-empty">앱을 실행하고 지면을 이동하면, 호출된 <b>JSON API</b>가 여기에 뜹니다(이미지 등 정적 리소스 제외). <b>구조 보기</b>로 응답 필드를 펼쳐 클릭하면 아래 ④ 규칙 입력이 자동 채워져 <b>모르는 API도 바로 조작 테스트</b>할 수 있어요.</div>
<div id="mapi-inspect" style="margin-top:10px"></div>
</div>

<div class="panel"><h2>④ 조작 규칙 추가 (웹·모바일 공용)</h2>
<div class="row">
<label style="flex:2">URL 또는 경로<input id="in-path" placeholder="https://ridibooks.com/webnovel/recommendation"></label>
<label style="flex:0 0 auto;min-width:auto">메서드<select id="in-method"><option>GET</option><option>POST</option><option>PUT</option><option>DELETE</option></select></label>
<label style="flex:0 0 auto;min-width:auto">방식<select id="in-type"><option value="text">텍스트 치환</option><option value="json">JSON 필드</option></select></label>
</div>
<div class="row" id="row-text" style="margin-top:10px">
<label style="flex:1">찾을 값 (원본 텍스트)<input id="in-find" placeholder="피치핑크 #2791 (15세 개정판)"></label>
<label style="flex:1">바꿀 값<input id="in-with" placeholder="테스트조작 타이틀"></label>
</div>
<div class="row hide" id="row-json" style="margin-top:10px">
<label style="flex:1">필드 경로 (dot-path)<input id="in-field" placeholder="books[].likeCount"></label>
<label style="flex:1">바꿀 값<input id="in-value" placeholder="999"></label>
</div>
<div class="row" style="margin-top:12px">
<label style="flex:1">규칙 이름(선택)<input id="in-id" placeholder="비우면 자동"></label>
<button class="btn primary" id="btn-add">규칙 저장</button>
<button class="btn ghost" id="btn-reset">입력 초기화</button>
</div>
<div class="hint">텍스트 치환: 화면 원본 텍스트를 그대로 붙여넣으면 됩니다(정규식 자동 처리). JSON 필드: 배열 전체는 <code>[]</code> (예: <code>books[].likeCount</code>).</div>
<div class="row" style="margin-top:12px"><button class="btn ghost" id="btn-inspect">🔍 위 URL 응답 구조 보기 (JSON)</button></div>
<div id="inspect-result" style="margin-top:10px"></div>
</div>

<div class="panel"><h2>⑤ 등록된 규칙 (<span id="t-count">0</span>)</h2>
<table><thead><tr><th>이름</th><th>메서드</th><th>경로</th><th>방식</th><th>내용</th><th></th></tr></thead><tbody id="tbody"></tbody></table>
<div class="hint" id="empty">등록된 규칙이 없습니다.</div>
</div>

<div class="panel" style="text-align:center"><h2>⑥ 테스트 실행</h2>
<button class="btn start" id="btn-start">▶ 테스트 시작</button>
<button class="btn stop" id="btn-stop" style="margin-left:10px">■ 테스트 종료</button>
<div class="hint only-web">[웹] 시작 → Claude가 대상 페이지를 열고 완전 로딩 대기 후 조작 결과 확인·스크린샷. 종료 → 조작 OFF(원본).</div>
<div class="hint only-mobile">[모바일] 시작 전 체크: 휴대폰 프록시=위 주소, CA 설치됨, (Android)디버그 빌드. 시작 → Claude가 mitmproxy 경유 응답 조작을 확인. 종료 → 조작 OFF(원본).</div>
</div>

<div class="panel"><h2>⑦ 테스트 결과 (실시간)</h2>
<div id="result-box"><div class="hint">아직 실행된 테스트가 없습니다. [테스트 시작]을 누르면 여기에 상태·스크린샷이 표시됩니다.</div></div>
</div>
</div><div id="toast"></div>
<script>
function toast(m){var t=document.getElementById("toast");t.textContent=m;t.classList.add("show");setTimeout(function(){t.classList.remove("show")},1900)}
function esc(s){return String(s).replace(/[&<>"']/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]})}
var STATE={};
function envClass(e){return e&&e.indexOf("canary")>=0?"env-canary":e&&e.indexOf("stage")>=0?"env-stage":"env-prod"}
function updateDisplay(s){
  document.getElementById("c-up").textContent=s.upstream;
  var ve=s.lastVerifiedEnv||"(아직 요청 없음)";
  document.getElementById("c-verified").innerHTML='<span class="envbadge '+envClass(ve)+'">'+esc(ve)+'</span>';
  var cm=document.getElementById("c-manip");cm.textContent=s.manipEnabled?"조작 ON":"조작 OFF";cm.className="run-state "+(s.manipEnabled?"on":"off");
  // 모바일 연결 정보(자동감지/수동 공유값) — 매 폴링 갱신
  document.getElementById("c-mobileproxy").textContent=s.mobileProxy||"(IP 미감지 — 수동 입력)";
  document.getElementById("c-localip").textContent=s.localIpAuto||"(감지 실패)";
  document.getElementById("c-mport").textContent=s.mobilePort||"-";
  renderResult(s.testStatus||{});render()}
function browserOpts(os){return os==="ios"?[["safari","Safari"],["chrome","Chrome"]]:[["firefox","Firefox (권장·비루팅 가능)"],["chrome","Chrome"],["samsung","삼성 인터넷"]]}
function populateBrowsers(os,want){var opts=browserOpts(os);var sel=document.getElementById("in-browser");var cur=want||sel.value;
  sel.innerHTML=opts.map(function(o){return "<option value='"+o[0]+"'>"+o[1]+"</option>"}).join("");
  sel.value=opts.some(function(o){return o[0]===cur})?cur:opts[0][0]}
function applyMode(){
  var t=document.getElementById("in-target").value,os=document.getElementById("in-os").value,mobile=(t!=="pcweb");
  document.getElementById("lbl-os").classList.toggle("hide",!mobile);
  document.getElementById("lbl-browser").classList.toggle("hide",t!=="mweb");
  if(t==="mweb")populateBrowsers(os);
  var br=document.getElementById("in-browser").value;
  document.body.classList.toggle("m-mobile",mobile);document.body.classList.toggle("m-web",!mobile);
  document.getElementById("mode-banner").className="mode-banner "+(mobile?"mode-mobile":"mode-web");
  var label=t==="pcweb"?"PC 웹 (Playwright)":(os==="aos"?"AOS":"iOS")+(t==="mweb"?" 모바일웹 · "+br:" 앱");
  document.getElementById("mode-label").textContent=label;
  document.getElementById("mode-desc").textContent=mobile?"— 휴대폰 프록시·CA 설치 필요. 아래 ② 참고.":"— 브라우저(Playwright)로 진행.";
  var note=document.getElementById("mobile-note");if(note){
    if(!mobile)note.innerHTML="";
    else if(t==="app")note.innerHTML='<b>CA(1회):</b> 프록시 설정 후 <code>mit.it</code>에서 mitmproxy CA 설치.<br><b>⚠️ 앱 사전조건(AOS):</b> Android 7+ 는 앱이 user CA 무시 → 비루팅 Android는 <b>user CA 신뢰+피닝 off 디버그/QA 빌드</b> 필요. 프로덕션만 있으면 Claude에게 "디버그 빌드 필요" 요청. iOS는 CA 신뢰 ON(피닝 없으면 가능).';
    else note.innerHTML=(os==="ios")?'<b>iOS 모바일웹:</b> CA 프로파일 설치 후 <i>설정&gt;일반&gt;정보&gt;인증서 신뢰 설정</i>에서 신뢰 ON → Safari·Chrome 등 <b>브라우저 무관</b> 복호화. <b>피닝·디버그빌드 불필요</b>.':(br==="firefox")?'<b>AOS 모바일웹 · Firefox:</b> Firefox는 자체 인증서 저장소 → 설정에서 CA 직접 import 하면 <b>루팅 없이</b> 복호화 가능. 피닝·디버그빌드 불필요.':'<b>AOS 모바일웹 · '+(br==="samsung"?"삼성 인터넷":"Chrome")+':</b> Android 7+ 는 이 브라우저가 user CA 무시 → <b>루팅 없으면 복호화 실패</b>. 비루팅이면 <b>Firefox</b>로 변경 권장.';
  }}
function syncForm(s){
  var plt=s.platform||"web";
  document.getElementById("in-target").value=plt==="web"?"pcweb":(s.mobileTarget==="mweb"?"mweb":"app");
  document.getElementById("in-os").value=(plt==="aos"||plt==="ios")?plt:"aos";
  populateBrowsers(document.getElementById("in-os").value,s.mobileBrowser);
  document.getElementById("in-env").value=s.targetEnv;
  document.getElementById("in-inject").value=String(s.headerInject);
  document.getElementById("in-login-needed").value=String(s.loginNeeded);
  if(s.loginId!==undefined)document.getElementById("in-login-id").value=s.loginId;
  if(s.hasLoginPw&&!document.getElementById("in-login-pw").value)document.getElementById("in-login-pw").placeholder="●●●●●● (저장됨)";
  if(document.activeElement!==document.getElementById("in-mobileip"))document.getElementById("in-mobileip").value=s.mobileIpOverride||"";
  applyMode()}
// load: 폼+표시 모두 세팅(초기 1회·명시적 저장 후). poll: 표시만 갱신(입력 중 폼 안 건드림)
function load(){return fetch("/__proxy/state").then(function(r){return r.json()}).then(function(s){STATE=s;syncForm(s);updateDisplay(s)})}
function poll(){return fetch("/__proxy/state").then(function(r){return r.json()}).then(function(s){STATE=s;updateDisplay(s)})}
function renderResult(ts){var rb=document.getElementById("result-box");if(!ts.state){return}
  var col=ts.state==="done"?"#1a7f37":ts.state==="running"?"#1f6feb":ts.state==="error"?"#d1242f":"#8b95a1";
  var h='<div style="font-weight:700;font-size:15px;color:'+col+'">'+esc(ts.state==="running"?"● 실행 중":ts.state==="done"?"✓ 완료":ts.state==="error"?"✗ 오류":"○ "+ts.state)+'</div>';
  if(ts.message)h+='<div class="hint" style="margin-top:5px">'+esc(ts.message)+'</div>';
  if(ts.verifiedEnv)h+='<div class="hint">검증된 환경: <b>'+esc(ts.verifiedEnv)+'</b></div>';
  if(ts.screenshotFile)h+='<div style="margin-top:10px"><img src="/__proxy/screenshot?t='+ts.ts+'" style="max-width:100%;border:1px solid #e3e6ea;border-radius:10px"></div>';
  rb.innerHTML=h}
function flatten(obj,prefix,out,depth){if(depth>7||out.length>300)return;if(Array.isArray(obj)){if(obj.length)flatten(obj[0],prefix+"[]",out,depth+1)}else if(obj&&typeof obj==="object"){for(var k in obj){flatten(obj[k],prefix?prefix+"."+k:k,out,depth+1)}}else{out.push({path:prefix,value:obj})}}
document.getElementById("btn-inspect").addEventListener("click",function(){
  var p=document.getElementById("in-path").value.trim();if(!p){toast("URL/경로를 먼저 입력하세요");return}
  try{if(p.slice(0,4).toLowerCase()==="http")p=new URL(p).pathname}catch(e){}if(p[0]!=="/")p="/"+p;
  var box=document.getElementById("inspect-result");box.innerHTML='<div class="hint">불러오는 중…</div>';
  fetch(p,{credentials:"include"}).then(function(r){var ct=r.headers.get("content-type")||"";return r.text().then(function(t){return {ct:ct,t:t}})}).then(function(o){
    if(o.ct.indexOf("application/json")<0){box.innerHTML='<div class="hint">JSON 응답이 아니에요(content-type: '+esc(o.ct)+'). 이 지면은 <b>텍스트 치환</b> 방식을 쓰세요.</div>';return}
    var data;try{data=JSON.parse(o.t)}catch(e){box.innerHTML='<div class="hint">JSON 파싱 실패</div>';return}
    var out=[];flatten(data,"",out,0);
    box.innerHTML='<div class="hint">필드를 클릭하면 JSON 조작 입력칸에 자동 입력됩니다.</div><table><thead><tr><th>필드 (dot-path)</th><th>현재 값</th></tr></thead><tbody>'+out.map(function(f){return "<tr style='cursor:pointer' data-field='"+esc(f.path)+"' data-val='"+esc(JSON.stringify(f.value))+"'><td class='mono'>"+esc(f.path)+"</td><td class='mono'>"+esc(String(JSON.stringify(f.value)).slice(0,80))+"</td></tr>"}).join("")+"</tbody></table>"
  }).catch(function(e){box.innerHTML='<div class="hint">불러오기 실패: '+esc(String(e))+'</div>'})});
document.getElementById("inspect-result").addEventListener("click",function(e){var tr=e.target.closest?e.target.closest("tr"):null;if(!tr||!tr.getAttribute("data-field"))return;
  document.getElementById("in-type").value="json";document.getElementById("in-type").dispatchEvent(new Event("change"));
  document.getElementById("in-field").value=tr.getAttribute("data-field");
  var v=tr.getAttribute("data-val");try{document.getElementById("in-value").value=JSON.parse(v)}catch(x){document.getElementById("in-value").value=v}
  toast("필드 선택됨: "+tr.getAttribute("data-field"))});
function render(){var ids=STATE.rules||[];document.getElementById("t-count").textContent=ids.length;
  document.getElementById("empty").style.display=ids.length?"none":"block";
  document.getElementById("tbody").innerHTML=ids.map(function(r){
    var detail=r.type==="json"?(r.overrides||[]).map(function(o){return esc(o.field)+" = "+esc(JSON.stringify(o.value))}).join("<br>"):(r.replace||[]).map(function(o){return "찾음: "+esc(o.find)+"<br>바꿈: "+esc(o.with)}).join("<br>");
    return "<tr><td>"+esc(r.id)+"</td><td>"+esc(r.match.method||"GET")+"</td><td class='mono'>"+esc(r.match.path)+"</td><td>"+esc(r.type)+"</td><td>"+detail+"</td><td><button class='btn danger sm' data-del='"+esc(r.id)+"'>삭제</button></td></tr>"
  }).join("")}
document.getElementById("in-type").addEventListener("change",function(){var j=this.value==="json";document.getElementById("row-json").classList.toggle("hide",!j);document.getElementById("row-text").classList.toggle("hide",j)});
document.getElementById("in-target").addEventListener("change",applyMode);
document.getElementById("in-os").addEventListener("change",applyMode);
document.getElementById("in-browser").addEventListener("change",applyMode);
document.getElementById("btn-mobileip").addEventListener("click",function(){
  var ip=document.getElementById("in-mobileip").value.trim();
  fetch("/__proxy/config",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({mobileIpOverride:ip})}).then(function(r){return r.json()}).then(function(s){STATE=s;updateDisplay(s);toast(ip?("모바일 IP 수동 지정: "+s.mobileProxy):("자동 감지로 복귀: "+(s.mobileProxy||"미감지")))})});
document.getElementById("btn-env").addEventListener("click",function(){
  var t=document.getElementById("in-target").value,os=document.getElementById("in-os").value;
  var platform=t==="pcweb"?"web":os,mobileTarget=t==="app"?"app":"mweb",mobileBrowser=document.getElementById("in-browser").value;
  fetch("/__proxy/config",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({platform:platform,mobileTarget:mobileTarget,mobileBrowser:mobileBrowser,targetEnv:document.getElementById("in-env").value,headerInject:document.getElementById("in-inject").value==="true"})}).then(function(r){return r.json()}).then(function(s){STATE=s;load();var d=t==="pcweb"?"PC 웹":(os.toUpperCase()+(t==="mweb"?" 모바일웹/"+mobileBrowser:" 앱"));toast("적용됨: "+d+" / "+s.targetEnv+(s.headerInject?" (헤더 ON)":" (헤더 OFF)"))})});
document.getElementById("btn-add").addEventListener("click",function(){
  var type=document.getElementById("in-type").value;
  var body={id:document.getElementById("in-id").value,path:document.getElementById("in-path").value,method:document.getElementById("in-method").value,type:type};
  if(type==="json"){body.field=document.getElementById("in-field").value;body.value=document.getElementById("in-value").value}
  else{body.find=document.getElementById("in-find").value;body.with=document.getElementById("in-with").value}
  if(!body.path){toast("URL/경로를 입력하세요");return}
  fetch("/__proxy/rules",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify(body)}).then(function(r){return r.json()}).then(function(s){STATE=s;render();toast("규칙 저장됨 ✓")})});
document.getElementById("btn-reset").addEventListener("click",function(){["in-path","in-find","in-with","in-field","in-value","in-id"].forEach(function(i){document.getElementById(i).value=""})});
document.getElementById("btn-login").addEventListener("click",function(){
  var body={loginNeeded:document.getElementById("in-login-needed").value==="true",loginId:document.getElementById("in-login-id").value};
  var pw=document.getElementById("in-login-pw").value;if(pw)body.loginPw=pw;
  fetch("/__proxy/config",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify(body)}).then(function(r){return r.json()}).then(function(s){STATE=s;document.getElementById("in-login-pw").value="";load();toast("로그인 정보 저장됨"+(s.loginNeeded?" (로그인 사용 ON)":""))})});
document.getElementById("tbody").addEventListener("click",function(e){var id=e.target.getAttribute("data-del");if(id){fetch("/__proxy/rules?id="+encodeURIComponent(id),{method:"DELETE"}).then(function(r){return r.json()}).then(function(s){STATE=s;render();toast("삭제됨")})}});
document.getElementById("btn-start").addEventListener("click",function(){
  fetch("/__proxy/run",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({action:"start"})}).then(function(r){return r.json()}).then(function(s){load();toast("▶ 테스트 시작 요청됨 — Claude가 실행합니다")})});
document.getElementById("btn-stop").addEventListener("click",function(){
  fetch("/__proxy/run",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({action:"stop"})}).then(function(r){return r.json()}).then(function(s){load();toast("■ 테스트 종료 — 조작 OFF(원본)")})});
// ---- 📱 모바일 API 탐색 (mitm_addon 이 기록한 mobile_apis.json 을 폴링) ----
var MAPI={apis:[],markTs:0,curRec:null};
function mapiRow(r){
  var label=esc(r.path)+(r.op?' <b style="color:#1a5fd0">#'+esc(r.op)+'</b>':'');
  return '<tr><td>'+esc(r.method)+'</td><td class="mono">'+label+'</td><td><span class="envbadge '+envClass(r.env||"")+'">'+esc(r.env||"-")+'</span></td><td>'+esc(String(r.status||''))+'</td><td>'+esc(String(r.count||1))+'</td>'
    +'<td style="white-space:nowrap"><button class="btn ghost sm" data-mapi-inspect="'+esc(r.key)+'">구조</button> <button class="btn primary sm" data-mapi-rule="'+esc(r.key)+'">규칙</button></td></tr>';
}
function mapiRender(){
  var list=MAPI.apis.slice();
  if(MAPI.markTs)list=list.filter(function(r){return (r.lastTs||0)>=MAPI.markTs});
  document.getElementById("mapi-empty").style.display=list.length?"none":"block";
  document.getElementById("mapi-tbody").innerHTML=list.map(mapiRow).join("");
  document.getElementById("mapi-status").textContent=(MAPI.markTs?"마크 이후 ":"전체 ")+list.length+"개"+(MAPI.apis.length?(" / 누적 "+MAPI.apis.length):"");
}
function mapiFetch(){return fetch("/__proxy/mobile-apis").then(function(r){return r.json()}).then(function(j){MAPI.apis=j.apis||[];mapiRender()}).catch(function(){})}
function mapiFind(key){return MAPI.apis.filter(function(r){return r.key===key})[0]}
function mapiInspect(key){
  var r=mapiFind(key);var box=document.getElementById("mapi-inspect");if(!r){return}
  MAPI.curRec=r;
  if(!r.body){box.innerHTML='<div class="hint">응답 본문이 캡처되지 않았어요.</div>';return}
  var data;try{data=JSON.parse(r.body)}catch(e){box.innerHTML='<div class="hint">JSON 파싱 실패 (content-type: '+esc(r.contentType||'')+')</div>';return}
  var out=[];flatten(data,"",out,0);
  box.innerHTML='<div class="hint">📍 <b>'+esc(r.method+" "+r.path+(r.op?" #"+r.op:""))+'</b> — 필드를 클릭하면 아래 ④ 규칙(경로·필드·값)이 자동 입력됩니다.</div>'
    +'<table><thead><tr><th>필드 (dot-path)</th><th>현재 값</th></tr></thead><tbody>'
    +out.map(function(f){return "<tr style='cursor:pointer' data-field='"+esc(f.path)+"' data-val='"+esc(JSON.stringify(f.value))+"'><td class='mono'>"+esc(f.path)+"</td><td class='mono'>"+esc(String(JSON.stringify(f.value)).slice(0,80))+"</td></tr>"}).join("")
    +"</tbody></table>";
}
function mapiToRule(key){
  var r=mapiFind(key);if(!r)return;
  document.getElementById("in-path").value="https://"+r.host+r.path;
  document.getElementById("in-method").value=r.method;
  document.getElementById("in-type").value="json";document.getElementById("in-type").dispatchEvent(new Event("change"));
  document.getElementById("panel-mapi").scrollIntoView({behavior:"smooth",block:"end"});
  toast("④ 규칙에 채워짐: "+r.method+" "+r.path+" — 구조 보기로 필드를 고르세요");
}
document.getElementById("btn-mapi-refresh").addEventListener("click",mapiFetch);
document.getElementById("btn-mapi-all").addEventListener("click",function(){MAPI.markTs=0;mapiRender()});
document.getElementById("btn-mapi-mark").addEventListener("click",function(){MAPI.markTs=Date.now()/1000;mapiRender();toast("여기부터 새 호출만 표시 — 앱에서 지면 진입하세요")});
document.getElementById("btn-mapi-clear").addEventListener("click",function(){fetch("/__proxy/mobile-apis",{method:"DELETE"}).then(function(){MAPI.apis=[];MAPI.markTs=0;document.getElementById("mapi-inspect").innerHTML="";mapiRender();toast("탐색 목록 초기화")})});
document.getElementById("mapi-tbody").addEventListener("click",function(e){var b=e.target.closest?e.target.closest("button"):null;if(!b)return;
  var ik=b.getAttribute("data-mapi-inspect");if(ik){mapiInspect(ik);return}
  var rk=b.getAttribute("data-mapi-rule");if(rk){mapiToRule(rk)}});
document.getElementById("mapi-inspect").addEventListener("click",function(e){var tr=e.target.closest?e.target.closest("tr"):null;if(!tr||!tr.getAttribute("data-field"))return;
  var r=MAPI.curRec;if(r){document.getElementById("in-path").value="https://"+r.host+r.path;document.getElementById("in-method").value=r.method}
  document.getElementById("in-type").value="json";document.getElementById("in-type").dispatchEvent(new Event("change"));
  document.getElementById("in-field").value=tr.getAttribute("data-field");
  var v=tr.getAttribute("data-val");try{document.getElementById("in-value").value=JSON.parse(v)}catch(x){document.getElementById("in-value").value=v}
  toast("필드 선택 → ④에 입력됨: "+tr.getAttribute("data-field"))});
load();setInterval(poll,4000);
mapiFetch();setInterval(mapiFetch,3000);
</script></body></html>`;
}

const server = http.createServer(async (req, res) => {
  const pathname = req.url.split("?")[0];
  if (pathname === "/__qa") { const html = renderPanel(); res.writeHead(200, { "content-type": "text/html; charset=utf-8", "content-length": Buffer.byteLength(html) }); res.end(html); return; }
  if (pathname.startsWith("/__proxy/")) { try { await handleApi(req, res, pathname); } catch (err) { sendJson(res, 500, { error: "panel_error", message: err.message }); } return; }

  const upstreamUrl = new URL(req.url, UPSTREAM_ORIGIN);
  const method = req.method || "GET";
  const hasBody = !["GET", "HEAD"].includes(method.toUpperCase());
  const reqBody = hasBody ? await readRawBody(req) : undefined;

  try {
    const upstreamRes = await fetch(upstreamUrl, { method, headers: buildUpstreamHeaders(req), body: reqBody && reqBody.length ? reqBody : undefined, redirect: "manual" });
    const envHeader = upstreamRes.headers.get("x-ridi-environment");
    lastVerifiedEnv = envHeader || "prod";
    const contentType = upstreamRes.headers.get("content-type") || "";
    const isJson = contentType.includes("application/json");
    const isText = contentType.includes("text/html") || contentType.includes("text/x-component") || contentType.includes("text/plain");

    const outHeaders = {};
    if (contentType) outHeaders["content-type"] = contentType;
    const loc = upstreamRes.headers.get("location");
    if (loc) outHeaders["location"] = rewriteLocation(loc);
    const setCookie = upstreamRes.headers.getSetCookie?.() || [];
    if (setCookie.length) outHeaders["set-cookie"] = setCookie.map(sanitizeCookie);
    outHeaders["x-ridi-environment"] = envHeader || "(none=prod)";
    outHeaders["x-proxy-target-env"] = targetEnv;

    // 텍스트 치환은 전역(모든 text/json 응답) — 지면 URL만 알아도 어느 엔드포인트가 내려주든 잡는다.
    const textReplaces = manipEnabled ? RULES.filter((r) => r.type === "text").flatMap((r) => r.replace || []) : [];
    // JSON 필드 조작은 경로 스코프(dot-path가 특정 엔드포인트 구조에 종속).
    const jsonRule = manipEnabled ? RULES.find((r) => r.type === "json" && matchRule(r, method, pathname)) : null;

    if (jsonRule && isJson) {
      let payload = JSON.stringify(applyJsonOverrides(await upstreamRes.json(), jsonRule.overrides));
      if (textReplaces.length) payload = applyTextReplaces(payload, textReplaces);
      outHeaders["content-length"] = Buffer.byteLength(payload);
      res.writeHead(upstreamRes.status, outHeaders); res.end(payload); return;
    }
    if (textReplaces.length && (isText || isJson)) {
      const patched = applyTextReplaces(await upstreamRes.text(), textReplaces);
      outHeaders["content-length"] = Buffer.byteLength(patched);
      res.writeHead(upstreamRes.status, outHeaders); res.end(patched); return;
    }
    const buf = Buffer.from(await upstreamRes.arrayBuffer());
    outHeaders["content-length"] = buf.length;
    res.writeHead(upstreamRes.status, outHeaders); res.end(buf);
  } catch (err) {
    res.writeHead(502, { "content-type": "application/json" });
    res.end(JSON.stringify({ error: "upstream_fetch_failed", message: err.message }));
  }
});

server.listen(PORT, () => {
  console.log(`▶ RIDI 웹 프록시 엔진 + 컨트롤 패널`);
  console.log(`  컨트롤 패널:  ${LOCAL_ORIGIN}/__qa`);
  console.log(`  업스트림:     ${UPSTREAM_ORIGIN}`);
  console.log(`  대상 환경:    ${targetEnv}${headerInject ? " (헤더 주입 ON)" : " (VPN 전환)"}`);
  console.log(`  규칙:        ${RULES.length}개  (${RULES_PATH})`);
});
