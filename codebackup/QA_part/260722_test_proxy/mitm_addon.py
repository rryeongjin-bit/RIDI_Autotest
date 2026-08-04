"""RIDI 모바일(AOS/iOS) 프록시 테스트 — mitmproxy 애드온.

웹 엔진(proxy-engine.js)과 **동일한 rules.json** 을 읽어 앱 트래픽에 같은 조작을 적용한다.
실기기 앱은 ridibooks.com 을 직접 때리므로 forward MITM 이 필요 → mitmproxy 로 처리.

사전 준비:
    pip install mitmproxy            # 미설치 상태

실행:
    cd test_proxy
    TARGET_ENV=stage HEADER_INJECT=true mitmdump -s mitm_addon.py --listen-port 8888

기기 셋업:
    1. 기기 Wi-Fi → 프록시 수동 → <맥IP>:8888
    2. 기기 브라우저로 http://mitm.it 접속 → CA 인증서 설치
       - iOS: 프로파일 설치 후 설정→일반→정보→인증서 신뢰 설정에서 신뢰 ON (필수)
       - AOS 실기기: user CA만 설치됨 → 앱이 release 빌드면 앱 트래픽 안 잡힘(debug 빌드/피닝우회 필요)
    3. cert pinning 걸려 있으면 해당 요청 실패 → debug 빌드 또는 objection/Frida 우회

환경변수: RULES_PATH / TARGET_ENV(stage|canary|prod) / HEADER_INJECT(true|false)
"""
import json
import logging
import os
import re
import time

from mitmproxy import http

_HERE = os.path.dirname(os.path.abspath(__file__))
# 기본값: 이 애드온과 같은 폴더(test_proxy/)의 rules.json — 자기완결형
RULES_PATH = os.environ.get("RULES_PATH", os.path.join(_HERE, "rules.json"))
TARGET_ENV = os.environ.get("TARGET_ENV", "prod").lower()
HEADER_INJECT = os.environ.get("HEADER_INJECT", "false") == "true"

# --- 모바일 API 탐색: 앱이 부른 JSON API를 기록해 패널이 목록·구조로 보여줌 ---
MOBILE_APIS_PATH = os.environ.get("MOBILE_APIS_PATH", os.path.join(_HERE, "mobile_apis.json"))
_DISCOVERED = {}      # key -> record
_MAX_APIS = 200       # 저장 상한(최근순)
_MAX_BODY = 2000000   # 응답 본문 캡처 상한(bytes). JSON이 잘려 깨지지 않도록 넉넉히(2MB)
_last_save = 0.0
# 초기화는 패널 🗑(DELETE /__proxy/mobile-apis)로 수행. import 시 파일을 지우지 않는다
# (mitmproxy 스크립트 핫리로드마다 import가 재실행되어 탐색결과가 날아가는 것 방지).


def _save_discovered(force=False):
    global _last_save
    now = time.time()
    if not force and now - _last_save < 1.0:  # 과도한 디스크 쓰기 방지(폴링은 3초)
        return
    _last_save = now
    try:
        apis = sorted(_DISCOVERED.values(), key=lambda r: r.get("lastTs", 0), reverse=True)[:_MAX_APIS]
        tmp = MOBILE_APIS_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"apis": apis}, f, ensure_ascii=False)
        os.replace(tmp, MOBILE_APIS_PATH)
    except Exception:
        pass


def record_api(flow, host, method, pathname, env):
    op = None
    if pathname.endswith("/graphql"):  # graphql은 operationName으로 구분
        try:
            reqj = json.loads(flow.request.get_text() or "{}")
            if isinstance(reqj, dict):
                op = reqj.get("operationName")
        except Exception:
            pass
    key = "%s %s%s%s" % (method, host, pathname, ("#" + op if op else ""))
    try:
        body = flow.response.get_text()
    except Exception:
        body = None
    if body and len(body) > _MAX_BODY:
        body = body[:_MAX_BODY]
    now = time.time()
    rec = _DISCOVERED.get(key)
    if not rec:
        rec = {"key": key, "method": method, "host": host, "path": pathname,
               "op": op, "firstTs": now, "count": 0}
        _DISCOVERED[key] = rec
    rec["count"] += 1
    rec["lastTs"] = now
    rec["env"] = env
    rec["status"] = flow.response.status_code
    rec["contentType"] = flow.response.headers.get("content-type", "")
    rec["body"] = body
    _save_discovered()

# ridi-test-env 정본과 동일
ENV_HEADERS = {
    "stage": {"x-ridi-enforced-env": "stage", "x-ridi-env-overlay": "stage"},
    "canary": {
        "x-ridi-backends-canary-routing": "true",
        "x-ridi-env-overlay": "canary",
    },
    "prod": {},
}


def load_rules():
    try:
        with open(RULES_PATH, encoding="utf-8") as f:
            parsed = json.load(f)
        rules = parsed if isinstance(parsed, list) else parsed.get("rules", [])
        return [r for r in rules if r.get("match", {}).get("path")]
    except Exception:
        return []


RULES = load_rules()
_rules_mtime = None


def maybe_reload_rules():
    # 패널이 rules.json 을 갱신하면(규칙 추가/삭제) 재기동 없이 자동 반영. 웹의 /__proxy/reload 대응.
    global RULES, _rules_mtime
    try:
        m = os.path.getmtime(RULES_PATH)
    except OSError:
        return
    if m != _rules_mtime:
        _rules_mtime = m
        RULES = load_rules()


def parse_path(p):
    tokens = []
    for raw in str(p).split("."):
        m = re.match(r"^([^\[]*)((?:\[\d*\])*)$", raw)
        if not m:
            tokens.append(raw)
            continue
        if m.group(1):
            tokens.append(m.group(1))
        for b in re.findall(r"\[\d*\]", m.group(2)):
            inner = b[1:-1]
            tokens.append("[]" if inner == "" else inner)
    return tokens


def set_at_path(node, tokens, value):
    if node is None:
        return
    tok, rest = tokens[0], tokens[1:]
    if tok == "[]":
        if isinstance(node, list):
            for el in node:
                if rest:
                    set_at_path(el, rest, value)
        return
    key = int(tok) if tok.isdigit() else tok
    try:
        if not rest:
            node[key] = value
        else:
            set_at_path(node[key], rest, value)
    except (KeyError, IndexError, TypeError):
        return


def match_rule(rule, method, pathname):
    m = rule["match"]
    if m.get("method") and m["method"].upper() != method.upper():
        return False
    try:
        return re.search(m["path"], pathname) is not None
    except re.error:
        return False


def apply_text_replaces(text, replaces):
    for r in replaces or []:
        if r.get("pattern"):
            pat = r["pattern"]
        elif r.get("find"):
            pat = re.escape(r["find"])
        else:
            continue
        try:
            text = re.sub(pat, r.get("with", ""), text)
        except re.error:
            pass
    return text


def request(flow: http.HTTPFlow):
    if HEADER_INJECT:
        for k, v in ENV_HEADERS.get(TARGET_ENV, {}).items():
            flow.request.headers[k] = v


def response(flow: http.HTTPFlow):
    global RULES
    maybe_reload_rules()
    pathname = flow.request.path.split("?")[0]
    method = flow.request.method

    # 환경 감지 로깅 — 실제 클라이언트(폰) 트래픽의 x-ridi-environment 를 실시간 확인.
    # 환경별 URL/경로가 동일하므로 "응답 헤더"가 유일한 ground truth. 라벨 대신 이 값을 신뢰한다.
    host = flow.request.pretty_host
    if host.endswith("ridibooks.com"):
        env = flow.response.headers.get("x-ridi-environment", "(none=prod)")
        logging.info("[ENV] %-14s %s %s", env, method, pathname)
        # JSON API면 탐색 목록에 기록(패널 "모바일 API 탐색"이 읽음). 이미지 등 정적리소스는 제외.
        if "application/json" in flow.response.headers.get("content-type", ""):
            record_api(flow, host, method, pathname, env)

    ctype = flow.response.headers.get("content-type", "")
    is_json = "application/json" in ctype
    is_text = is_json or "text/" in ctype

    # 텍스트 치환은 전역(모든 text/json 응답) — 웹 엔진과 동일. 지면 URL만 알아도 어느 엔드포인트가 내려주든 잡는다.
    text_replaces = []
    for r in RULES:
        if r.get("type") == "text":
            text_replaces.extend(r.get("replace", []))
    # JSON 필드 조작은 경로 스코프(dot-path 가 특정 엔드포인트 구조에 종속).
    json_rule = next((r for r in RULES if r.get("type", "json") == "json" and match_rule(r, method, pathname)), None)

    if json_rule and is_json:
        try:
            body = json.loads(flow.response.get_text())
        except Exception:
            body = None
        if body is not None:
            for ov in json_rule.get("overrides", []):
                if "field" in ov:
                    set_at_path(body, parse_path(ov["field"]), ov.get("value"))
            out = json.dumps(body, ensure_ascii=False)
            flow.response.set_text(apply_text_replaces(out, text_replaces))
            return
    if text_replaces and is_text:
        flow.response.set_text(apply_text_replaces(flow.response.get_text(), text_replaces))
