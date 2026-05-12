import os
import logging
import pytest
import time
import socket
from datetime import datetime
from appium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config.capabilities import *
from config.settings import *
from pages.login_page import *
from data.test_data import *

_active_device_info: dict = {}

@pytest.fixture(scope="session")
def platform(request) -> str:
    marker_expr = request.config.getoption("-m", default="")
    return "aos" if "aos" in marker_expr else "ios"

@pytest.fixture(scope="session")
def timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

@pytest.fixture(scope="session", autouse=True)
def setup_logger(platform, timestamp):
    log_dir  = os.path.join(LOG_DIR, platform)
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"{timestamp}_{platform}.log")

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger

@pytest.fixture(scope="session")
def driver(request, platform):
    marker_expr = request.config.getoption("-m", default="")
    env = "emulator"  if "emulator"  in marker_expr else \
          "simulator" if "simulator" in marker_expr else \
          "real"

    device = _find_active_device(platform, env)
    if device is None:
        pytest.exit(f"[driver] 활성화된 기기 없음 - platform: {platform}, env: {env}")

    server_url = get_server_url(device["port"])
    options    = get_capabilities(platform, device)

    logging.info(f"[driver] 연결 기기: {device['device_name']} | 플랫폼: {platform} | 환경: {env} | 포트: {device['port']}")
    _active_device_info["device_name"] = device["device_name"]

    drv = webdriver.Remote(server_url, options=options)
    drv.implicitly_wait(DEFAULT_TIMEOUT)

    yield drv

    drv.quit()
    logging.info("[driver] 드라이버 종료")


def _find_active_device(platform: str, env: str) -> dict | None:
    devices = DEVICE_CONFIG.get(platform, [])
    for device in devices:
        if device["type"] != env:
            continue
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("localhost", device["port"])) == 0:
                return device
    return None


@pytest.fixture(scope="module", autouse=True)
def reset_app(driver, platform):
    bundle_id = BUNDLE_ID_AOS if platform == "aos" else BUNDLE_ID_IOS

    logging.info(f"[reset_app] 앱 초기화 시작: {bundle_id}")

    if platform == "aos":
        driver.execute_script("mobile: clearApp", {"appId": bundle_id})
        driver.activate_app(bundle_id)
    elif platform == "ios":
        driver.terminate_app(bundle_id)
        driver.activate_app(bundle_id)

    logging.info("[reset_app] 앱 초기화 완료")

    yield

    driver.terminate_app(bundle_id)
    logging.info("[reset_app] 앱 종료")

@pytest.fixture(scope="function")
def login(driver, platform):

    account = TestAccount.AOS if platform == "aos" else TestAccount.IOS
    page    = LoginPage(driver, platform)
    replace = Replacedevicelist(driver, platform)

    # 이미 로그인된 상태면 스킵
    if page.is_login_success():
        logging.info("[login] 이미 로그인된 상태 - 스킵")
        return

    # 딥링크로 로그인 페이지 진입
    page.open_deeplink(DeepLinks.LOGIN)
    page.switch_to_webview()
    page.wait_for_webview()
    page.login(id=account["id"], pw=account["pw"])
    page.switch_to_native()
    page.wait_for_native()

    if replace.is_replace_device_displayed():
        replace.click_replace_toggle()
        replace.click_replace_btn()

    logging.info(f"[login] 로그인 완료 - platform: {platform}")

def pytest_terminal_summary(terminalreporter, config):
    passed   = len(terminalreporter.stats.get("passed",   []))
    failed   = len(terminalreporter.stats.get("failed",   []))
    skipped  = len(terminalreporter.stats.get("skipped",  []))
    error    = len(terminalreporter.stats.get("error",    []))
    total    = passed + failed + skipped + error 

    elapsed = round(time.time() - terminalreporter._sessionstarttime, 2)

    marker_expr = config.getoption("-m", default="")
    platform    = "aos" if "aos" in marker_expr else "ios"
    log_dir     = os.path.join(LOG_DIR, platform)
    log_files   = sorted([f for f in os.listdir(log_dir) if f.endswith(".log")]) if os.path.exists(log_dir) else []
    log_file    = log_files[-1] if log_files else "로그 파일 없음"

    terminalreporter.write_sep("=", "테스트 결과 요약")
    terminalreporter.write_line(f"테스트 기기 : {_active_device_info.get('device_name', 'unknown')}")
    terminalreporter.write_line(f"총 {total}개 실행")
    terminalreporter.write_line(f"✅ pass     : {passed}개")
    terminalreporter.write_line(f"❌ fail     : {failed}개")
    terminalreporter.write_line(f"🚫 skip     : {skipped}개")
    terminalreporter.write_line(f"🔴 error    : {error}개")
    terminalreporter.write_line(f"⏳ 총 실행시간 : {elapsed}s")
    terminalreporter.write_line(f"🛠️ 로그파일명  : {log_file}")
    terminalreporter.write_sep("=", "")

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report  = outcome.get_result()

    if report.when == "call" and report.failed:
        drv      = item.funcargs.get("driver")
        platform = item.funcargs.get("platform", "unknown")
        ts       = datetime.now().strftime("%Y%m%d_%H%M%S")

        if drv:
            screenshot_dir = os.path.join(SCREENSHOT_DIR, platform)
            os.makedirs(screenshot_dir, exist_ok=True)
            path = os.path.join(screenshot_dir, f"{ts}_{item.name}.png")
            drv.save_screenshot(path)
            logging.info(f"[screenshot] 저장 완료: {path}")