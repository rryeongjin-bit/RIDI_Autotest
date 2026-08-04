---
name: proxy
description: RIDI 프록시 테스트 실행 워크플로우. 사용자가 "proxy"라고 언급하면 트리거된다. 프록시로 리디 응답(좋아요/리뷰/별점/가격/배지 등 임의 필드)을 조작해 웹(ridibooks.com) 또는 모바일 앱(AOS/iOS) 지면을 검증한다. proxy 입력 시 엔진을 기동하고 컨트롤패널(/__qa)을 곧바로 연다. 설정(매체·환경·엔드포인트·조작값·로그인)은 패널에서 받고, 사용자가 [테스트 시작]을 누르면 Claude는 질문 없이 신호를 폴링·소비해 실행한다. 모든 프록시 코드/설정/규칙은 test_proxy 프로젝트에서 관리한다. 체크리스트 생성 등 산출물 작성에는 사용하지 않는다.
---

# 🔁 RIDI 프록시 테스트 워크플로우

> 프록시로 리디 응답 필드를 조작해, 각 지면(웹/앱)이 조작값을 올바르게 표시하는지 검증한다.

## ⚡ 3줄 요약

1. **`proxy` 입력** → 엔진 기동 + 컨트롤패널(`/__qa`) 오픈 + 신호 폴링 자동 시작. **나는 질문하지 않는다.**
2. 사용자가 **패널에서 설정 입력 → [테스트 시작]** 클릭 → 엔진이 신호 적재 → 내가 폴링·소비해 그 설정대로 실행.
3. 실행 → **환경·조작값 검증** → **결과를 패널(`/__proxy/result`)에 게시** → 다시 폴링(세션 내내 반복).

> ⛔ **옛 흐름 폐기**: Q1~Q4(매체·대상·환경·조작값)를 대화로 묻던 방식은 쓰지 않는다. 설정은 전부 패널에서 받는다.

---

## 📁 위치 & 구성 (전부 `test_proxy/`)

- **작업경로**: `/Users/ridi/Desktop/RIDI-QA-Auto/RIDI-QA-Auto/test_proxy` (gitignored, [[proxy-working-dir]])
- **스킬 스코프**: 이 스킬은 `test_proxy/`에 스코프되어 다른 프로젝트와 독립.

| 파일 | 역할 |
|---|---|
| `proxy-engine.js` | **웹** rule-engine 프록시 + **컨트롤패널**(`/__qa`). Node 무의존. 포트 **3001**, 업스트림 `ridibooks.com` |
| `mitm_addon.py` | **모바일**(AOS/iOS) mitmproxy 애드온. 같은 `rules.json` 재사용. 포트 **8888** |
| `rules.json` | 조작 규칙 (웹·모바일 공유). 패널의 "규칙 추가/삭제"가 직접 갱신 |
| `server.js` + `overrides.json` | 기존 dev.ridi.io 프록시(포트 3000). **이 스킬과 무관 — 건드리지 않는다** |

> 엔진 코드·설정·규칙은 전부 `test_proxy/`에서만 다룬다.

---

## 진입 절차 (질문 금지)

### 1️⃣ 기동 + 패널 오픈 + 폴링 시작 (한 번에)

```bash
# ① 엔진 떠 있는지 확인
curl -s localhost:3001/__proxy/state

# ② 안 떠 있으면 백그라운드 기동 (플래그 불필요 — 설정은 패널에서)
cd test_proxy && PORT=3001 node proxy-engine.js

# ③ 컨트롤패널 오픈
open http://localhost:3001/__qa
```

- 기본값 `prod / headerInject=false`로 뜨고 **패널이 덮어쓴다**.
- `open` 직후 **신호 폴링을 백그라운드로 자동 시작**한다. "누르셨나요?"라고 되묻지 않는다.
- 이 시점부터 사용자는 **패널만** 본다(개인화 의존 조작 테스트 제외). 결과 소통도 대화가 아니라 패널로.
- 사용자가 패널에서 설정하는 것: **매체 · 환경 · 헤더주입 · 조작 규칙 · (필요 시) 로그인** → **[테스트 시작]**.

### 2️⃣ 시작/종료 신호 자동 감지 (기다리지 말고 내가 폴링)

```bash
# 백그라운드(run_in_background): 신호 하나 감지되면 출력하고 종료
for i in $(seq 1 300); do
  sig=$(curl -s -m 3 localhost:3001/__proxy/signal)
  act=$(echo "$sig" | python3 -c "import sys,json;d=json.load(sys.stdin);s=d.get('signal');print(s.get('action') if s else '')" 2>/dev/null)
  [ -n "$act" ] && { echo "SIGNAL:$act"; echo "$sig"; exit 0; }
  sleep 3
done; echo "TIMEOUT"
```

- **`start`** → 신호 설정대로 곧바로 3단계 실행. 신호 필드: `platform, mobileTarget, mobileBrowser, mobileProxy, target, targetEnv, headerInject, loginNeeded, loginId, loginPw`. *(PW는 신호에만 있고 state엔 없음)*
- **`stop`** → 검증 중단, 조작 OFF(원본). 패널에 종료 알림.
- **연속 감지** → 한 테스트를 끝내면(또는 stop 후) **폴링 루프를 다시 띄운다**. "시작→실행→결과게시→재폴링"을 세션 내내 자동 반복. 사용자가 그만하라 할 때까지 되묻지 않는다.
- 현재 전체 설정·규칙은 `GET /__proxy/state`로 확인.

> **🎯 선택된 대상만 테스트 (엄수).** 신호의 `platform`/`mobileTarget`이 가리키는 **그 대상만** 검증한다. `platform=web` → **PC 웹 지면(URL)만**. 앱·모바일웹·API를 곁다리로 확인하지 않는다. 조작값이 안 보여도 다른 매체로 넘어가지 말고, 선택 대상 안에서 아래 "미반영 단정 금지" 절차(전체 스크롤·속성 탐색)를 밟는다.

**대상 3종 판별 (신호값 기준)**

| 신호값 | 대상 | 실행 방식 |
|---|---|---|
| `platform=web` | **PC 웹** | Playwright로 `localhost:3001` 접속 |
| `platform=aos/ios` + `mobileTarget=mweb` | **모바일 웹** | 휴대폰 브라우저(`mobileBrowser`) + mitmproxy |
| `mobileTarget=app` | **모바일 앱** | appium + mitmproxy |

### 3️⃣ 실행 (신호 설정대로, 추가 질문 없이)

#### ① PC 웹 (`platform=web`)
Playwright로 `http://localhost:3001/<지면경로>` 진입. 프록시가 업스트림 응답을 규칙대로 조작해 서빙.

> **URL 지면만 본다.** 텍스트 치환은 전역이라 SSR HTML에 이미 반영된다 — `/v2/views/48` 같은 앱 API를 직접 호출·검증할 필요 없음(그 데이터는 서버가 SSR에 인라인). 렌더된 화면에서 조작값을 찾으면 끝. (실측: `/webnovel/recommendation` "웹소설 실시간 랭킹" 작가명 `원누리`→조작문구가 SSR HTML·화면에 반영, API 미접근으로 확인.)

> **✅ 완전 로딩 대기 (필수)** — 스켈레톤 상태에서 찍으면 "미반영" 오탐.
> 스켈레톤 셀렉터(`[class*="skeleton"],[class*="shimmer"],[class*="placeholder"]`)가 0이 될 때까지 폴링 + **3~5초(최대 5초) 안전 대기** 후 검증 시작.

**⚠️ 조작값이 화면에 안 보일 때 — "미반영" 단정 금지.** 사용자는 분명 존재하는 원본을 조작 요청한 것이다.

- **(a) 개인화 의존 섹션** → 사용자가 그렇다고 알려준다. 그 때만 개인화/로그인 계정 요인 고려.
- **(b) 그 외** → **내가 전체 화면을 끝까지 스크롤하며 탐색**. 지연 마운트(랭킹/캐러셀/IntersectionObserver)는 스크롤해야 DOM에 붙는다. 가시 텍스트 + 속성(alt/title/aria-label)까지 훑고, 찾으면 그 위치로 스크롤해 스샷.
  *(실측: `/webnovel/recommendation` "웹소설 실시간 랭킹" 작가명은 스크롤 후에야 노출)*

**🔧 마크업 분리로 텍스트 규칙이 안 먹을 때 — 내가 감지·자동 보정 (사용자에게 마크업 되묻지 말 것)**

사용자가 넣은 `find`는 **화면에 보이는 텍스트**(예 `131개`)지만, 실제 응답 본문은 숫자·단위가 태그로 분리돼 있을 수 있다.
> 실측: 마이리디 카트 수 `<span class="amount">131</span>개` → 연속 문자열 `131개`가 본문에 없어 치환 실패.

사용자는 지면 구조를 모르는 게 정상이므로, 미반영이 확인되면 **내가 직접** 다음을 수행한다:

1. **실제 응답 바이트 확인** — 지면 HTML: 브라우저 same-origin `fetch('<경로>',{credentials:'include'}).then(r=>r.text())`로 소스 받아 대상 값 주변 구조 확인(예 `131` 주변 윈도우). API JSON: `curl … | jq`.
2. **매칭되는 연속형으로 규칙 재작성** — 태그 포함형(`131</span>개` → `522</span>개`) 또는 그 지면에서 **유일하게 잡히는** 최소형(숫자만 `131`→`522`, 본문 출현 횟수로 오검치환 없음 확인). `with`도 동일 구조 유지해 태그 안 깨지게.
3. **재검증** — `POST /__proxy/rules`(같은 `id`로 upsert) → `GET /__proxy/reload` → 재진입 → 스샷·결과 게시.

> **경계**: 값이 응답 어디에도 없으면(개인화/지연/부재) 자동 보정 말고 [[qa-conclude-only-when-verified]]대로 **보류·사용자 확인**. 자동 보정은 "원본은 응답에 있는데 태그/구분자 때문에 find가 안 맞는" 경우에 한한다.

#### 앱 조작값이 여러 엔드포인트에 걸쳐 있을 때 — 전역 치환 + 실기기 대조 (내가 감지)
- **텍스트 치환은 전역**(모든 text/json 응답)으로 적용된다 — 웹 엔진과 동일하게 `mitm_addon.py`도 그렇게 동작(경로 스코프 아님). **JSON 필드 조작만 경로 스코프.** 그래서 같은 값(예 작가명 `원누리`)이 `/v2/views/48`·`/v2/exp-sections/related-features` 등 **여러 API에 걸쳐 있어도 한 번에** 바뀐다.
- **조작값이 화면에 안 보여도 "미반영" 단정 금지** (웹과 동일 규율). 내가 직접: ① **탐색 본문들에서 그 값이 어느 엔드포인트에 있는지 감지**(`mobile_apis.json` 검색), ② **실기기 화면을 스크롤/캐러셀 넘기며 대조**(uiautomator dump 텍스트 검색 or 스크린샷) — 지연 마운트·캐러셀·개인화 섹션(`방금 본 작품과 비슷한`=related-features)은 노출돼야 DOM/hierarchy에 뜬다, ③ 올바른 값으로 반영됐는지 확인.
- **캐시 주의**: 큰 지면(예 `/v2/views/48` 386KB)은 클라이언트 캐시라 재진입만으론 재요청이 없다 → **앱 강제종료 후 재실행**(`am force-stop` + 재런치)으로 캐시 우회해 재요청을 일으킨 뒤 검증.

#### ② 모바일 웹 (`platform=aos/ios` + `mobileTarget=mweb`)
휴대폰 **브라우저**로 ridibooks.com 접속 → 휴대폰 Wi-Fi 프록시(`mobileProxy`) 경유 mitmproxy가 조작. 앱이 아니라 **피닝·디버그빌드 불필요**, CA 신뢰만 관건.

| 브라우저 | 결과 |
|---|---|
| **iOS** (Safari·Chrome 등) | CA 신뢰 ON → 브라우저 무관 복호화 **O** |
| **AOS · Firefox** | Firefox 자체 저장소에 CA import → 루팅 없이 **O** ✅ *(AOS 권장 경로)* |
| **AOS · Chrome/삼성인터넷** | Android 7+ user CA 무시 → 루팅 없으면 **실패** → Firefox로 안내 |

#### ③ 모바일 앱 (`mobileTarget=app`)
mitmproxy(맥 로컬, `brew install mitmproxy`) + appium.
```bash
cd test_proxy && TARGET_ENV=<env> HEADER_INJECT=<t/f> mitmdump -s mitm_addon.py --listen-port 8888
```
> **⚠️ AOS 사전조건**: Android 7+ 앱은 user CA 무시 → **비루팅 Android에선 user CA 신뢰 + 피닝 off 디버그/QA 빌드** 필요. 프로덕션만 있으면 사용자에게 "디버그 빌드 필요"로 요청. *(iOS는 CA 신뢰 ON, 피닝 없으면 가능)*

#### 모바일 환경(env) 확정 — 사용자가 mac VPN으로 사전 설정, 나는 응답 헤더로 검증
- **환경별 URL/API 경로는 전부 동일**하다. 환경 구분자는 경로가 아니라 **응답이 실토하는 값**: 응답헤더 `x-ridi-environment`(stage/canary=값, prod=없음) + 화면 마커(`[STAGE]` 타이틀·띠지).
- **역할 분담(표준)**: 사용자가 **테스트 전에 mac VPN으로 환경을 세팅**하고 **패널 라벨(`targetEnv`)로 선언**한다. 나는 **매번 "VPN 켜세요"라고 요구하지 않고** 라벨을 접수해 바로 진행하되, **실제 응답 헤더/마커가 라벨과 어긋날 때만** 알린다(라벨 맹신 금지 = 안전망).
- **헤더주입은 OFF**로 둔다(`HEADER_INJECT=false`). 환경은 mac VPN이 정하므로 헤더주입은 이중이고, 앱 실로그인 시 **인증 오염(거짓 로그아웃)** 위험([[deploy-qa-header-inject-auth-artifact]]). → mitmdump는 환경 안 가리고 통과, 환경 전환 시 **재기동 불필요**(사용자가 mac VPN + 패널 라벨만 갱신).
- **감지 방법**: mac 합성 curl은 Cloudflare 403에 막혀 부정확 → **실제 폰 트래픽**을 봐야 한다. `mitm_addon.py`가 ridibooks.com 응답마다 `logging.info("[ENV] …")`로 `x-ridi-environment`를 콘솔에 찍으므로, 폰이 요청을 흘리는 순간 그 로그로 실환경 확정.

#### 모바일 공통 (②③)
- mitmproxy는 **맥 로컬**에서 구동. **기기 프록시 IP는 패널이 공유** — 엔진이 맥 en0(Wi-Fi) LAN IP 자동 감지 → `mobileProxy`(`<ip>:8888`)로 노출(패널 ②).
- **와이파이 바뀌면 IP도 바뀜** → 자동감지 틀리면 패널에서 수동 입력(`mobileIpOverride`, 빈값=자동복귀). **하드코딩 말고 매번 `/__proxy/state`에서 읽기.**
- PC·기기 **동일 Wi-Fi 필수**(사용자 보장). 기본 라우트가 VPN(utun*)이어도 LAN 도달은 en0 기준이라 무관.
- **CA(1회)**: 기기 프록시 설정 후 **`http://mitm.it`**(‼️ `mit.it` 아님 — mitm.it) → mitmproxy 공개 CA 설치. 프록시가 활성일 때만 이 페이지가 뜬다. 안 뜨면 폰 Wi-Fi 프록시(`<ip>:8888`) 확인. **대안: 맥에서 `adb push ~/.mitmproxy/mitmproxy-ca-cert.cer /sdcard/Download/` 후 설정에서 설치**(mitm.it 불안정 시). **Charles와 별개**(전용 CA `~/.mitmproxy/mitmproxy-ca-cert.*`). 개인키 `mitmproxy-ca.pem/.p12`는 기기 설치 금지.

#### 로그인
- **PC 웹**: `loginNeeded` 시 신호의 `loginId/loginPw`로 Playwright 로그인.
- **모바일(웹/앱)**: 사용자가 기기에서 **직접 로그인**(자동화 안 함).
- PW는 메모리만 사용, `state`·`rules.json`에 미노출.

### 4️⃣ 검증 (결함 선언 전 규율 — [[qa-conclude-only-when-verified]])

**🥇 환경 확정 (1순위)** — 응답 헤더 `x-ridi-environment`: `stage/canary`=해당 환경, 없음=`prod`. 띠지(리본)는 보조.
```bash
curl -si "http://localhost:3001/<경로>" | grep -i x-ridi-environment
```
- 헤더 주입은 **헤더 존중 노드에서만** 유효. canary는 `x-ridi-backends-canary-routing` 주입해야 확정될 수 있음([[canary-vpn-needs-header-injection]]).
- 동적검증 시 헤더 주입이 account 인증을 오염시켜 **거짓 로그아웃**을 일으킬 수 있음([[deploy-qa-header-inject-auth-artifact]]) — 인증 오탐과 제품 결함 혼동 금지.
- **불일치·불확실 시 → 중단하고 사용자 확인.**

**조작값 확정** — 프록시 응답에서 해당 필드가 조작값인지 확인(JSON=`curl … | jq`, 지면=브라우저/appium 표시).

**상태변경**(결제·충전·가입/탈퇴 등)은 환경을 `x-ridi-environment`로 **재확인한 뒤에만**.

### 5️⃣ 결과 회신

```bash
curl -s -X POST localhost:3001/__proxy/result -H 'content-type: application/json' \
  -d '{"state":"done","message":"<요약>","verifiedEnv":"<stage|canary|prod>","screenshotFile":"<절대경로.png>"}'
```
- **결과 스샷은 `test_proxy/results/`에 저장**하고 그 절대경로를 `screenshotFile`로 게시. 이름은 목적이 드러나게 `<YYYYMMDD-HHMMSS>_<매체>_<env>_<지면>_<조작요약>.png`. (Playwright 스샷은 프로젝트 루트 하위만 허용 → `test_proxy/results/`로 저장.)
- `screenshotFile`은 엔진이 `/__proxy/screenshot`으로 패널 `<img>`에 서빙.
- **대화에도 요약 보고**: 검증된 환경 라벨 · 조작 필드/값 · 지면 반영 여부.

---

## 🔌 패널 API 요약 (필요 시 curl로 직접)

| 메서드 · 경로 | 용도 |
|---|---|
| `GET /__qa` | 컨트롤패널 HTML |
| `GET /__proxy/state` | 현재 설정·규칙·testStatus 조회 |
| `GET /__proxy/signal` | start/stop 신호 소비(읽으면 비움) — **폴링 대상** |
| `GET /__proxy/reload` | rules.json 재로딩(재시작 불필요) |
| `POST /__proxy/config` | 매체·env·헤더주입·로그인 설정(주로 패널) |
| `POST /__proxy/run` | `{action:'start'\|'stop'}` 테스트 토글(주로 패널 버튼) |
| `POST /__proxy/result` | Claude→패널 결과 피드백 |
| `POST/DELETE /__proxy/rules` | 조작 규칙 추가/삭제(주로 패널) |
| `GET /__proxy/screenshot` | 최신 결과 스크린샷 |

---

## ⚠️ 주의

- **스코프 = test_proxy 전용.** 모든 작업(문서·규칙·설정·엔진 코드·노트)은 `test_proxy/` 안에서만. 루트나 다른 프로젝트 파일·공용 메모리는 **건드리지 않는다.** proxy 규칙·교훈은 이 SKILL.md에 자체 보관.
- **질문하지 않는다.** proxy 입력 → 기동 → 패널 오픈이 전부. 신호가 없으면 "패널에서 [테스트 시작]을 누르라"고 안내만.
- 전 환경 `ridibooks.com` 공유 → **prod를 stage로 착각 위험 상존.** 환경은 "가정"이 아니라 응답헤더 "확인".
- 나는 VPN·FF를 직접 못 바꾼다 → 실제 환경 전환(VPN) 필요 시 사용자에게 요청.
- 기존 `server.js`(dev.ridi.io, 3000)는 별개. 신규 엔진은 3001(포트 충돌 회피).
- 상세 환경/헤더/크리덴셜 규칙은 [[ridi-test-env]] 참조.
