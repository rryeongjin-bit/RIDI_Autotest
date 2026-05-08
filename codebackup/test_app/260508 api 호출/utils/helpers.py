import os
import logging
import requests
from datetime import datetime
from config.settings import *

log = logging.getLogger(__name__)

def get_timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def get_screenshot_path(platform: str, test_name: str) -> str:
    ts  = get_timestamp()
    dir = os.path.join(SCREENSHOT_DIR, platform)
    os.makedirs(dir, exist_ok=True)
    return os.path.join(dir, f"{ts}_{test_name}.png")

def get_log_path(platform: str, timestamp: str) -> str:
    dir = os.path.join(LOG_DIR, platform)
    os.makedirs(dir, exist_ok=True)
    return os.path.join(dir, f"{timestamp}_{platform}.log")

def get_report_path(platform: str, timestamp: str) -> str:
    dir = os.path.join(REPORT_DIR, platform)
    os.makedirs(dir, exist_ok=True)
    return os.path.join(dir, f"{timestamp}_{platform}_report.html")


def init_output_dirs(platform: str):
    dirs = [
        os.path.join(SCREENSHOT_DIR, platform),
        os.path.join(LOG_DIR, platform),
        os.path.join(REPORT_DIR, platform),
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        log.info(f"[init_output_dirs] 디렉토리 확인: {d}")

def check_api_status(url: str, params: dict = None) -> int:
    """API 응답 상태코드 반환"""
    response = requests.get(url, params=params)
    return response.status_code