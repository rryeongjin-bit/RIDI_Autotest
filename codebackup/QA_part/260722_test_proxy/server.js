// 순수 Node.js(http)로 만든 상품 카운트 프록시 + 컨트롤 패널. 외부 의존성 없음 (Node 18+ 필요).
// 좋아요/리뷰수/별점/별점수/상품문의수를 상품ID별로 조작해서 내려준다.
// 값 설정은 브라우저 컨트롤 패널(/__qa)에서 버튼으로. overrides.json 에 저장되어 재시작해도 유지.
"use strict";

const http = require("node:http");
const fs = require("node:fs");
const path = require("node:path");

const UPSTREAM_ORIGIN = "https://dev.ridi.io";
const PORT = process.env.PORT ? Number(process.env.PORT) : 3000;
const STORE_PATH = path.join(__dirname, "overrides.json");

// 조작 필드 정의. UI 라벨/타입도 여기서 관리.
//   likeCount     : 좋아요(위시리스트) 수                    (GET /goods/api/products/{id})
//   reviewCount   : 리뷰 수 = 별점 수 (업스트림이 같은 count 필드 하나로 씀)  (.../reviews/stats)
//   averageRating : 별점 평균                               (.../reviews/stats)
//   inquiryCount  : 상품문의 수                              (.../inquiries)
const FIELDS = [
  { key: "likeCount", label: "좋아요 수", step: "1", placeholder: "예: 999" },
  { key: "reviewCount", label: "리뷰/별점 수", step: "1", placeholder: "예: 5000" },
  { key: "averageRating", label: "별점 평균", step: "0.1", placeholder: "예: 4.9" },
  { key: "inquiryCount", label: "상품문의 수", step: "1", placeholder: "예: 5000" },
];
const FIELD_KEYS = FIELDS.map((f) => f.key);

// 상품ID별 조작 값. 파일에서 로드(없으면 기본 시드). 필드는 전부 선택 — 없으면 실제값 통과.
let FAKE_OVERRIDES = loadOverrides();

function loadOverrides() {
  try {
    const raw = fs.readFileSync(STORE_PATH, "utf8");
    const parsed = JSON.parse(raw);
    if (parsed && typeof parsed === "object") return parsed;
  } catch (_) {
    /* 파일 없거나 깨짐 → 기본 시드 사용 */
  }
  return {
    "14945803200236627896": {
      likeCount: 999,
      reviewCount: 5000,
      averageRating: 4.9,
      inquiryCount: 5000,
    },
  };
}

function saveOverrides() {
  fs.writeFileSync(STORE_PATH, JSON.stringify(FAKE_OVERRIDES, null, 2), "utf8");
}

function getOverride(productId, field) {
  const o = FAKE_OVERRIDES[productId];
  return o && o[field] !== undefined ? o[field] : undefined;
}

// 상품 상세: /shop/api/products/{productId} (하위 경로 아님, 쿼리스트링은 허용)
const PRODUCT_DETAIL_RE = /^\/shop\/api\/products\/([^/?]+)(?:\?|$)/;
// 리뷰 통계: /shop/api/products/{productId}/reviews/stats
const PRODUCT_REVIEWS_STATS_RE = /^\/shop\/api\/products\/([^/?]+)\/reviews\/stats(?:\?|$)/;
// 상품문의: /shop/api/products/{productId}/inquiries
const PRODUCT_INQUIRIES_RE = /^\/shop\/api\/products\/([^/?]+)\/inquiries(?:\?|$)/;
// SSR 페이지: /shop/products/{productId}
const PRODUCT_PAGE_RE = /^\/shop\/products\/([^/?]+)(?:\?|$)/;

function escapeRegExp(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

// SSR HTML/RSC payload는 <script> 안 JS 문자열로 한 번 이스케이프되어 있어
// 실제로는 \"id\":\"...\", ... ,\"likeCount\":N 형태로 박혀있다. 그 이스케이프된 따옴표까지 맞춰서 치환.
function patchLikeCountInHtml(html, productId, fakeCount) {
  const re = new RegExp(
    `(\\\\?"id\\\\?":\\\\?"${escapeRegExp(productId)}\\\\?"[\\s\\S]{0,2000}?\\\\?"likeCount\\\\?":)(\\d+)`,
    "g"
  );
  return html.replace(re, (_, prefix) => `${prefix}${fakeCount}`);
}

// 리뷰 평점/개수는 페이지당 한 번(대상 상품 하나)만 dehydrate 되어 있으므로 productId 스코핑 없이 패치.
function patchReviewStatsInHtml(html, fakeRating, fakeCount) {
  const re = /(\\?"averageRating\\?":)(\d+(?:\.\d+)?)(,\\?"count\\?":)(\d+)/g;
  return html.replace(re, (_, p1, origRating, p3, origCount) => {
    const rating = fakeRating !== undefined ? fakeRating : origRating;
    const count = fakeCount !== undefined ? fakeCount : origCount;
    return `${p1}${rating}${p3}${count}`;
  });
}

async function proxyPassthrough(upstreamRes, res) {
  const contentType = upstreamRes.headers.get("content-type") || "";
  res.writeHead(upstreamRes.status, { "content-type": contentType });
  res.end(Buffer.from(await upstreamRes.arrayBuffer()));
}

// ─── 컨트롤 패널 ────────────────────────────────────────────────────────
function sendJson(res, status, obj) {
  const payload = JSON.stringify(obj);
  res.writeHead(status, {
    "content-type": "application/json; charset=utf-8",
    "content-length": Buffer.byteLength(payload),
  });
  res.end(payload);
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    let data = "";
    req.on("data", (c) => {
      data += c;
      if (data.length > 1e6) reject(new Error("body too large"));
    });
    req.on("end", () => resolve(data));
    req.on("error", reject);
  });
}

// 입력 정규화: 빈값/null → 필드 제거(실제값 통과), 값 있으면 숫자로.
function normalizeOverride(input) {
  const out = {};
  for (const key of FIELD_KEYS) {
    const v = input[key];
    if (v === undefined || v === null || v === "") continue;
    const n = Number(v);
    if (Number.isFinite(n)) out[key] = n;
  }
  return out;
}

async function handlePanelApi(req, res, pathname) {
  // 전체 상태 조회
  if (req.method === "GET" && pathname === "/__qa/api/state") {
    return sendJson(res, 200, {
      upstream: UPSTREAM_ORIGIN,
      port: PORT,
      fields: FIELDS,
      overrides: FAKE_OVERRIDES,
    });
  }
  // 작품 추가/수정 (upsert)
  if (req.method === "POST" && pathname === "/__qa/api/overrides") {
    let input;
    try {
      input = JSON.parse(await readBody(req));
    } catch (_) {
      return sendJson(res, 400, { error: "invalid_json" });
    }
    const id = String(input.productId || "").trim();
    if (!id) return sendJson(res, 400, { error: "productId_required" });
    FAKE_OVERRIDES[id] = normalizeOverride(input);
    saveOverrides();
    return sendJson(res, 200, { ok: true, id, override: FAKE_OVERRIDES[id] });
  }
  // 작품 삭제
  if (req.method === "DELETE" && pathname === "/__qa/api/overrides") {
    const id = new URL(req.url, "http://x").searchParams.get("id");
    if (id && FAKE_OVERRIDES[id]) {
      delete FAKE_OVERRIDES[id];
      saveOverrides();
    }
    return sendJson(res, 200, { ok: true });
  }
  return sendJson(res, 404, { error: "not_found" });
}

function renderQaPanel() {
  return `<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PDP 프록시 컨트롤 패널</title>
<style>
  :root { --blue:#1f6feb; --blue-d:#1a5fd0; --bg:#f6f7f9; --line:#e3e6ea; --muted:#8b95a1; --text:#1a1d21; }
  * { box-sizing: border-box; }
  body { font-family:-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Segoe UI",sans-serif; margin:0; background:var(--bg); color:var(--text); }
  .wrap { max-width:960px; margin:0 auto; padding:32px 20px 64px; }
  header h1 { font-size:22px; margin:0 0 4px; }
  header .sub { color:var(--muted); font-size:13px; }
  .cards { display:flex; gap:12px; margin:20px 0 28px; flex-wrap:wrap; }
  .card { background:#fff; border:1px solid var(--line); border-radius:12px; padding:14px 18px; flex:1; min-width:160px; }
  .card .k { color:var(--muted); font-size:12px; }
  .card .v { font-size:18px; font-weight:700; margin-top:4px; word-break:break-all; }
  .panel { background:#fff; border:1px solid var(--line); border-radius:14px; padding:22px; margin-bottom:24px; }
  .panel h2 { font-size:15px; margin:0 0 16px; }
  .grid { display:grid; grid-template-columns:1.4fr repeat(4,1fr); gap:10px; align-items:end; }
  .grid.head { color:var(--muted); font-size:12px; font-weight:600; margin-bottom:6px; }
  label.fld { display:flex; flex-direction:column; gap:5px; font-size:12px; color:var(--muted); }
  input { border:1px solid var(--line); border-radius:8px; padding:9px 10px; font-size:14px; width:100%; }
  input:focus { outline:none; border-color:var(--blue); box-shadow:0 0 0 3px rgba(31,111,235,.12); }
  input[readonly] { background:#f0f2f4; color:var(--muted); }
  .btn { border:0; border-radius:8px; padding:9px 16px; font-size:14px; font-weight:600; cursor:pointer; }
  .btn.primary { background:var(--blue); color:#fff; }
  .btn.primary:hover { background:var(--blue-d); }
  .btn.ghost { background:#eef1f4; color:var(--text); }
  .btn.ghost:hover { background:#e3e7ec; }
  .btn.danger { background:#fff; color:#d1242f; border:1px solid #f0c2c5; }
  .btn.danger:hover { background:#fdecee; }
  .btn.sm { padding:6px 10px; font-size:12px; }
  .row-actions { display:flex; gap:6px; }
  table { width:100%; border-collapse:collapse; font-size:14px; }
  th,td { padding:11px 10px; border-bottom:1px solid var(--line); text-align:left; }
  th { color:var(--muted); font-size:12px; font-weight:600; }
  td.id { font-family:ui-monospace,Menlo,monospace; font-size:12px; word-break:break-all; }
  .muted { color:#c2c8cf; }
  .empty { color:var(--muted); text-align:center; padding:28px 0; }
  .hint { color:var(--muted); font-size:12px; margin-top:10px; }
  .formbar { display:flex; gap:10px; margin-top:16px; }
  #toast { position:fixed; left:50%; bottom:28px; transform:translateX(-50%) translateY(20px); background:#1a1d21; color:#fff; padding:11px 18px; border-radius:10px; font-size:14px; opacity:0; pointer-events:none; transition:.25s; }
  #toast.show { opacity:1; transform:translateX(-50%) translateY(0); }
  @media (max-width:640px){ .grid{grid-template-columns:1fr 1fr} }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>PDP 프록시 컨트롤 패널</h1>
    <div class="sub">버튼 클릭만으로 좋아요·리뷰·별점·문의수를 조작합니다. 값은 자동 저장돼 재시작해도 유지됩니다.</div>
  </header>

  <div class="cards">
    <div class="card"><div class="k">업스트림</div><div class="v" id="c-upstream">-</div></div>
    <div class="card"><div class="k">포트</div><div class="v" id="c-port">-</div></div>
    <div class="card"><div class="k">등록된 작품 수</div><div class="v"><span id="c-count">0</span>개</div></div>
  </div>

  <div class="panel">
    <h2 id="form-title">＋ 새 작품 추가</h2>
    <div class="grid head">
      <div>상품 ID</div>${FIELDS.map((f) => `<div>${f.label}</div>`).join("")}
    </div>
    <div class="grid">
      <label class="fld"><input id="in-id" placeholder="상품 ID (숫자)"></label>
      ${FIELDS.map((f) => `<label class="fld"><input id="in-${f.key}" type="number" step="${f.step}" placeholder="${f.placeholder}"></label>`).join("")}
    </div>
    <div class="formbar">
      <button class="btn primary" id="btn-save">저장</button>
      <button class="btn ghost" id="btn-reset">초기화</button>
    </div>
    <div class="hint">각 값을 <b>비워두면</b> 실제값이 그대로 통과합니다. 별점 평균은 소수(예: 4.9) 입력 가능.</div>
  </div>

  <div class="panel">
    <h2>등록된 작품 (<span id="t-count">0</span>)</h2>
    <table>
      <thead><tr><th>상품 ID</th>${FIELDS.map((f) => `<th>${f.label}</th>`).join("")}<th>동작</th></tr></thead>
      <tbody id="tbody"></tbody>
    </table>
    <div class="empty" id="empty" style="display:none">등록된 작품이 없습니다. 위에서 추가하세요.</div>
  </div>
</div>
<div id="toast"></div>

<script>
const FIELDS = ${JSON.stringify(FIELDS)};
const FIELD_KEYS = FIELDS.map(f => f.key);
let STATE = { upstream:"", port:0, overrides:{} };

function toast(msg){ const t=document.getElementById("toast"); t.textContent=msg; t.classList.add("show"); setTimeout(()=>t.classList.remove("show"),1800); }
function esc(s){ return String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c])); }

async function load(){
  const r = await fetch("/__qa/api/state");
  STATE = await r.json();
  document.getElementById("c-upstream").textContent = STATE.upstream;
  document.getElementById("c-port").textContent = STATE.port;
  render();
}

function render(){
  const ids = Object.keys(STATE.overrides);
  document.getElementById("c-count").textContent = ids.length;
  document.getElementById("t-count").textContent = ids.length;
  document.getElementById("empty").style.display = ids.length ? "none" : "block";
  const tbody = document.getElementById("tbody");
  tbody.innerHTML = ids.map(id => {
    const o = STATE.overrides[id];
    const cells = FIELD_KEYS.map(k => o[k]!==undefined ? esc(o[k]) : '<span class="muted">실제값</span>').join("</td><td>");
    const pdp = STATE.port ? \`http://localhost:\${STATE.port}/shop/products/\${encodeURIComponent(id)}?genre=comic\` : "#";
    return \`<tr>
      <td class="id">\${esc(id)}</td>
      <td>\${cells}</td>
      <td><div class="row-actions">
        <a class="btn ghost sm" href="\${pdp}" target="_blank" rel="noopener">미리보기</a>
        <button class="btn ghost sm" data-edit="\${esc(id)}">수정</button>
        <button class="btn danger sm" data-del="\${esc(id)}">삭제</button>
      </div></td>
    </tr>\`;
  }).join("");
}

function resetForm(){
  document.getElementById("in-id").value="";
  document.getElementById("in-id").readOnly=false;
  FIELD_KEYS.forEach(k=>document.getElementById("in-"+k).value="");
  document.getElementById("form-title").textContent="＋ 새 작품 추가";
}

async function save(){
  const id = document.getElementById("in-id").value.trim();
  if(!id){ toast("상품 ID를 입력하세요"); return; }
  const body = { productId:id };
  FIELD_KEYS.forEach(k=>{ body[k]=document.getElementById("in-"+k).value; });
  const r = await fetch("/__qa/api/overrides",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify(body)});
  if(!r.ok){ toast("저장 실패"); return; }
  await load(); resetForm(); toast("저장됨 ✓");
}

async function del(id){
  if(!confirm(id+" 삭제할까요?")) return;
  await fetch("/__qa/api/overrides?id="+encodeURIComponent(id),{method:"DELETE"});
  await load(); toast("삭제됨");
}

function edit(id){
  const o = STATE.overrides[id]||{};
  document.getElementById("in-id").value=id;
  document.getElementById("in-id").readOnly=true;
  FIELD_KEYS.forEach(k=>document.getElementById("in-"+k).value = o[k]!==undefined ? o[k] : "");
  document.getElementById("form-title").textContent="✎ 작품 수정: "+id;
  window.scrollTo({top:0,behavior:"smooth"});
}

document.getElementById("btn-save").addEventListener("click", save);
document.getElementById("btn-reset").addEventListener("click", resetForm);
document.getElementById("tbody").addEventListener("click", e=>{
  const d=e.target.getAttribute("data-del"); if(d){ del(d); return; }
  const ed=e.target.getAttribute("data-edit"); if(ed){ edit(ed); }
});
load();
</script>
</body>
</html>`;
}

const server = http.createServer(async (req, res) => {
  const pathname = req.url.split("?")[0];

  // 컨트롤 패널 (로컬, 업스트림 요청 없음)
  if (pathname === "/__qa") {
    const html = renderQaPanel();
    res.writeHead(200, {
      "content-type": "text/html; charset=utf-8",
      "content-length": Buffer.byteLength(html),
    });
    res.end(html);
    return;
  }
  if (pathname.startsWith("/__qa/api/")) {
    try {
      await handlePanelApi(req, res, pathname);
    } catch (err) {
      sendJson(res, 500, { error: "panel_error", message: err.message });
    }
    return;
  }

  const upstreamUrl = new URL(req.url, UPSTREAM_ORIGIN);

  try {
    const upstreamRes = await fetch(upstreamUrl, {
      method: req.method,
      headers: {
        accept: req.headers.accept || "*/*",
        "user-agent": "Mozilla/5.0",
      },
    });

    const contentType = upstreamRes.headers.get("content-type") || "";
    const isJson = contentType.includes("application/json");

    // 1) 상품 상세 JSON — likeCount 조작
    const detailMatch = req.url.match(PRODUCT_DETAIL_RE);
    if (detailMatch && isJson) {
      const fakeLikeCount = getOverride(detailMatch[1], "likeCount");
      if (fakeLikeCount !== undefined) {
        const body = await upstreamRes.json();
        body.likeCount = fakeLikeCount;
        const payload = JSON.stringify(body);
        res.writeHead(upstreamRes.status, {
          "content-type": "application/json; charset=utf-8",
          "content-length": Buffer.byteLength(payload),
        });
        res.end(payload);
        return;
      }
    }

    // 2) 리뷰 통계 JSON — averageRating(별점) / count(리뷰수=별점수) 조작
    const reviewsStatsMatch = req.url.match(PRODUCT_REVIEWS_STATS_RE);
    if (reviewsStatsMatch && isJson) {
      const fakeRating = getOverride(reviewsStatsMatch[1], "averageRating");
      const fakeCount = getOverride(reviewsStatsMatch[1], "reviewCount");
      if (fakeRating !== undefined || fakeCount !== undefined) {
        const body = await upstreamRes.json();
        if (fakeRating !== undefined) body.averageRating = fakeRating;
        if (fakeCount !== undefined) body.count = fakeCount;
        const payload = JSON.stringify(body);
        res.writeHead(upstreamRes.status, {
          "content-type": "application/json; charset=utf-8",
          "content-length": Buffer.byteLength(payload),
        });
        res.end(payload);
        return;
      }
    }

    // 3) 상품문의 JSON — pagination.total(상품문의 카운트) 조작
    const inquiriesMatch = req.url.match(PRODUCT_INQUIRIES_RE);
    if (inquiriesMatch && isJson) {
      const fakeInquiryCount = getOverride(inquiriesMatch[1], "inquiryCount");
      if (fakeInquiryCount !== undefined) {
        const body = await upstreamRes.json();
        body.pagination = { ...body.pagination, total: fakeInquiryCount };
        const payload = JSON.stringify(body);
        res.writeHead(upstreamRes.status, {
          "content-type": "application/json; charset=utf-8",
          "content-length": Buffer.byteLength(payload),
        });
        res.end(payload);
        return;
      }
    }

    // 4) SSR 페이지 HTML — likeCount / averageRating / reviewCount 텍스트 치환
    const pageMatch = req.url.match(PRODUCT_PAGE_RE);
    if (pageMatch && (contentType.includes("text/html") || contentType.includes("text/x-component"))) {
      const override = FAKE_OVERRIDES[pageMatch[1]];
      if (override) {
        let html = await upstreamRes.text();
        if (override.likeCount !== undefined) {
          html = patchLikeCountInHtml(html, pageMatch[1], override.likeCount);
        }
        if (override.averageRating !== undefined || override.reviewCount !== undefined) {
          html = patchReviewStatsInHtml(html, override.averageRating, override.reviewCount);
        }
        res.writeHead(upstreamRes.status, {
          "content-type": contentType,
          "content-length": Buffer.byteLength(html),
        });
        res.end(html);
        return;
      }
    }

    // 5) 그 외 모든 요청은 그대로 통과
    await proxyPassthrough(upstreamRes, res);
  } catch (err) {
    res.writeHead(502, { "content-type": "application/json" });
    res.end(JSON.stringify({ error: "upstream_fetch_failed", message: err.message }));
  }
});

server.listen(PORT, () => {
  const count = Object.keys(FAKE_OVERRIDES).length;
  console.log(`▶ 컨트롤 패널(설정):  http://localhost:${PORT}/__qa`);
  console.log(`▶ 업스트림:           ${UPSTREAM_ORIGIN}`);
  console.log(`▶ 등록된 작품 수:      ${count}개`);
});
