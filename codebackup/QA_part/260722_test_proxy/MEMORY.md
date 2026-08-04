# test_proxy — 실측 로그 & 상세 근거

`CLAUDE.md`(규칙)·`SKILL.md`(워크플로우)를 얇게 유지하기 위해, **실측 사례·구체 근거·기기 정보** 등 로그성 내용을 여기 모은다.
스코프는 `test_proxy/` 내부 한정 — 공용 메모리(`~/.claude/.../memory/`)엔 올리지 않는다.

---

## 🧪 실측 사례

### 1. 마크업 분리로 텍스트 치환 실패 → 규칙 자동 보정 (마이리디 카트 수)
- **지면**: `/account/myridi` (로그인 필요, stage, headerInject ON)
- **증상**: 규칙 `find:"131개" → with:"522개"` 가 화면에 반영 안 됨.
- **원인**: SSR HTML 원문이
  ```html
  <span class="amount museo_sans">131</span>개
  ```
  구조라 **연속 문자열 `131개`가 응답 본문에 존재하지 않음** → 리터럴 치환 미스. 제품 결함 아님(엔진 정상).
- **해결**: 실제 응답 바이트 확인 후 규칙을 `find:"131</span>개" → with:"522</span>개"` 로 재작성 → `/__proxy/reload` → 재진입. **카트 522개** 정상 표시 확인.
- **교훈** → `SKILL.md` 3단계 "마크업 분리 자동 보정" 규칙, `CLAUDE.md` 운영원칙 5.
- **참고**: HTML 전체에 `131`은 이 카트 카운트 1곳뿐이라 숫자만 치환도 안전했던 케이스. 다른 지면은 출현 횟수 먼저 확인.

### 2. 지연 마운트 섹션은 스크롤해야 노출 (웹소설 랭킹)
- **지면**: `/webnovel/recommendation`
- **증상**: "웹소설 실시간 랭킹"의 작가명이 초기 DOM에 없음.
- **원인**: IntersectionObserver 기반 지연 마운트 → 스크롤해야 DOM에 붙음.
- **교훈** → "미반영" 단정 전 **전체 화면 끝까지 스크롤** + 속성(alt/title/aria)까지 탐색.

### 3. 로그인 중 시스템 팝업으로 첫 시도 실패
- **증상**: `/account/myridi` 로그인 클릭 시 실제 `https://ridibooks.com`으로 튕기고 로그인 페이지 재노출.
- **원인**: 시스템 팝업(사용자 확인). 재시도 시 이미 세션 성립 → 로그인 페이지가 `/webnovel/recommendation`으로 리다이렉트되어 로그인 확인됨.
- **참고**: 엔진은 리다이렉트 `Location`·쿠키(Domain 제거)를 localhost로 재작성하므로 **프록시(localhost:3001) 오리진 안에 머무는 한** 인증 세션 유지됨.

---

## 📱 기기 / 환경 정보

- **AOS 테스트 기기**: `SM-S937N`, Android 15, **비루팅**, 직장프로필 `user10` 존재.
  → 비루팅이라 앱(③) HTTPS 복호화하려면 user CA 신뢰 + 피닝 off **디버그/QA 빌드** 필수. 모바일웹(②)은 **Firefox**로 루팅 없이 가능.
- **mitmproxy CA**: `~/.mitmproxy/mitmproxy-ca-cert.cer`(AOS) / `.pem`(iOS) = 동일 CA, 설치법만 다름. 개인키 `mitmproxy-ca.pem`/`.p12`는 기기 설치 금지.
- **Charles**: 기존 수동 세팅 그대로 두고 mitmproxy와 완전 별개 운영.

---

## 🔗 관련 메모 (공용, 참고용)
- [[proxy-working-dir]] · [[qa-conclude-only-when-verified]] · [[canary-vpn-needs-header-injection]] · [[deploy-qa-header-inject-auth-artifact]] · [[ridi-test-env]]
