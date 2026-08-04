# Appium MCP Server

Claude Desktop에서 iOS/Android 기기를 직접 제어하기 위한 MCP 서버입니다.

---

## 설치

```bash
# 1. 프로젝트를 원하는 경로에 복사 (예: ~/appium-mcp)
cp -r appium-mcp ~/appium-mcp
cd ~/appium-mcp

# 2. 의존성 설치
pip install -r requirements.txt
```

---

## Claude Desktop 등록

`~/Library/Application Support/Claude/claude_desktop_config.json` 파일을 열어서 아래 내용을 추가하세요.

```json
{
  "mcpServers": {
    "appium-mcp": {
      "command": "/usr/bin/python3",
      "args": ["/Users/sun/appium-mcp/server.py"]
    }
  }
}
```

> `python3` 경로는 `which python3` 로 확인 후 수정하세요.

---

## 사용 전 확인사항

1. **Appium 서버 실행 중** 확인 (`http://127.0.0.1:4723`)
2. **Android**: USB 디버깅 ON, `adb devices`에서 `R3CX20P85PZ` 확인
3. **iOS**: 기기 연결 및 WebDriverAgent 빌드 완료 상태

---

## Claude Desktop 재시작 후 사용 예시

Claude Desktop에서 자연어로 바로 제어 가능합니다:

```
"Android 기기에 연결해줘"
→ appium_connect(platform="android")

"현재 화면 스크린샷 찍어줘"
→ appium_screenshot()

"홈 버튼 탭해줘"
→ appium_tap_by_accessibility_id(accessibility_id="홈")

"아래로 3번 스크롤해줘"
→ appium_scroll_down(times=3)

"현재 화면 UI 구조 보여줘"
→ appium_get_page_source()
```

---

## 파일 구조

```
appium-mcp/
├── server.py                  # MCP 서버 진입점
├── requirements.txt
├── claude_desktop_config.json # Claude Desktop 등록 설정 예시
└── src/
    ├── __init__.py
    ├── appium_controller.py   # Appium 세션/기기 제어 핵심 로직
    └── tools.py               # MCP tool 정의 및 라우팅
```

---

## 지원 툴 목록

| 툴 이름 | 설명 |
|---|---|
| `appium_connect` | iOS/Android 세션 연결 |
| `appium_disconnect` | 세션 종료 |
| `appium_status` | 세션 상태 확인 |
| `appium_screenshot` | 스크린샷 촬영 |
| `appium_tap` | 좌표 탭 |
| `appium_tap_by_accessibility_id` | accessibility_id로 탭 |
| `appium_tap_by_text` | 텍스트로 탭 |
| `appium_tap_by_xpath` | XPath로 탭 |
| `appium_type_text` | 텍스트 입력 |
| `appium_swipe` | 좌표 스와이프 |
| `appium_scroll_down` | 아래로 스크롤 |
| `appium_scroll_up` | 위로 스크롤 |
| `appium_get_page_source` | UI 계층 XML 반환 |
| `appium_find_elements` | 요소 검색 |
| `appium_element_exists` | 요소 존재 확인 |
| `appium_launch_app` | 앱 실행 |
| `appium_terminate_app` | 앱 종료 |
| `appium_background_app` | 앱 백그라운드 전환 |
| `appium_get_window_size` | 화면 크기 확인 |
