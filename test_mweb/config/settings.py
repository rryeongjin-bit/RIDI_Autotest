
# Appium 서버
APPIUM_SERVER_URL = "http://127.0.0.1:4723"

# Target URL
BASE_URL = "https://ridibooks.com"

# Timeout 설정 (초 단위)
TIMEOUT = {
    "implicit":    10,   # 암묵적 대기 - element 탐색 시 최대 대기
    "explicit":    20,   # 명시적 대기 - 특정 조건 만족까지 최대 대기
    "page_load":   30,   # 페이지 로딩 최대 대기
    "new_command": 120,  # Appium 세션 유지 - 명령 간 최대 대기 (느린 환경이면 늘릴 것)
}

# AOS 디바이스 정보
AOS_DEVICE = {
    "real": {
        "device_name": "YOUR_AOS_DEVICE_NAME",  
        "udid":        "YOUR_AOS_DEVICE_UDID",
    },
    "emulator": {
        "device_name": "emulator-5554",          
        "udid":        "emulator-5554",
    },
}

# iOS 디바이스 정보
IOS_DEVICE = {
    "real": {
        "device_name":      "YOUR_IOS_DEVICE_NAME",  # ex) iPhone 15
        "udid":             "YOUR_IOS_DEVICE_UDID",  # Xcode > Devices 에서 확인
        "platform_version": "17.0",                  # 실제 iOS 버전으로 교체
    },
    "simulator": {
        "device_name":      "iPhone 15",
        "udid":             "",                       # 시뮬레이터는 생략 가능
        "platform_version": "17.0",
    },
}

# etc
CHROMEDRIVER_PATH = "/path/to/chromedriver"  # Samsung Browser용 chromedriver 경로