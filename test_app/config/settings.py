import os
from dotenv import load_dotenv

load_dotenv()

# 앱 정보
APP_PACKAGE   = os.getenv("APP_PACKAGE",  "com.your.package")   # AOS 패키지명
APP_ACTIVITY  = os.getenv("APP_ACTIVITY", "com.your.MainActivity")  # AOS 시작 액티비티
BUNDLE_ID_AOS = os.getenv("BUNDLE_ID_AOS", "com.your.package")  # AOS 번들 ID
BUNDLE_ID_IOS = os.getenv("BUNDLE_ID_IOS", "com.your.bundleid") # iOS 번들 ID

# Appium Server
APPIUM_HOST = os.getenv("APPIUM_HOST", "localhost")

# Timeout 기준값
DEFAULT_TIMEOUT = 10   # 기본 요소 대기 (초)
NETWORK_TIMEOUT = 30   # 네트워크 응답 대기 (초)
LONG_TIMEOUT    = 60   # 앱 초기화 등 긴 대기 (초)

# 테스트 계정
AOS_TEST_ID = os.getenv("AOS_TEST_ID")
AOS_TEST_PW = os.getenv("AOS_TEST_PW")
IOS_TEST_ID = os.getenv("IOS_TEST_ID")
IOS_TEST_PW = os.getenv("IOS_TEST_PW")

# 산출물 저장 경로
REPORT_DIR     = "reports"
SCREENSHOT_DIR = "screenshots"
LOG_DIR        = "logs"