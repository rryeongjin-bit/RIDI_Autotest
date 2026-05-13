import os
from dotenv import load_dotenv

load_dotenv()

def _get_env(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise ValueError(f"[settings] {key} 가 .env에 선언되지 않았습니다.")
    return value

APP_PACKAGE   = _get_env("APP_PACKAGE")
APP_ACTIVITY  = _get_env("APP_ACTIVITY")
BUNDLE_ID_AOS = _get_env("BUNDLE_ID_AOS")
BUNDLE_ID_IOS = _get_env("BUNDLE_ID_IOS")
AOS_TEST_ID = _get_env("AOS_TEST_ID")
AOS_TEST_PW = _get_env("AOS_TEST_PW")
IOS_TEST_ID = _get_env("IOS_TEST_ID")
IOS_TEST_PW = _get_env("IOS_TEST_PW")
APPIUM_HOST = os.getenv("APPIUM_HOST", "localhost")

DEFAULT_TIMEOUT = 10  
NETWORK_TIMEOUT = 20   
LONG_TIMEOUT    = 60   

REPORT_DIR     = "reports"
SCREENSHOT_DIR = "screenshots"
LOG_DIR        = "logs"