# 대화 메모리

## 환경 정보
- 작업 디렉토리: `/Users/ridi/Desktop/RIDI-QA-Auto/RIDI-QA-Auto`
- 주요 작업 폴더: `test_app/`
- Python 가상환경: `.venv/bin/python3.13`
- 테스트 프레임워크: pytest + Appium
- 플랫폼: iOS / Android 앱 자동화

## PC 환경 변경
- 기존 PC에서 새 PC로 변경함 (2026-06-25)
- 새 PC 셋업 후 Appium iOS 테스트 실행 시 `xcodebuild failed with code 65` 오류 발생했으나 직접 해결함

## VS Code 설정
- `.vscode/settings.json` 생성: 폴더 열 때 `.venv` 가상환경 자동 활성화되도록 설정

## 프로젝트 구조
- `test_app/config/capabilities.py`: iOS/AOS 디바이스 설정 및 Appium capabilities
- `test_app/conftest.py`: pytest 픽스처 (driver, reset_app 등)
- `test_app/config/settings.py`: 설정값 (BUNDLE_ID 등)
- `test_app/tests/`: 테스트 파일 위치
- 디바이스 UDID는 자동 감지 (`xcrun xctrace` / `adb devices`)
