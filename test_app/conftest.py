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
from pages.home_page import *
from pages.login_page import *


_active_device_info: dict = {}
_failed_classes = set()

@pytest.fixture(scope="session")
def platform(request) -> str:
    return request.config.getoption("--platform", default="ios")

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
    env = request.config.getoption("--env", default="real")

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
def reset_app(driver, platform, request):
    bundle_id  = BUNDLE_ID_AOS if platform == "aos" else BUNDLE_ID_IOS
    reset_mode = request.config.getoption("--reset", default="full")
    login_mode = request.config.getoption("--login", default="auto")

    if reset_mode == "full":
        logging.info(f"[reset_app] 앱 초기화 시작: {bundle_id}")
        if platform == "aos":
            driver.execute_script("mobile: clearApp", {"appId": bundle_id})
            driver.activate_app(bundle_id)
        elif platform == "ios":
            driver.terminate_app(bundle_id)
            driver.activate_app(bundle_id)
        logging.info("[reset_app] 앱 초기화 완료")

    elif reset_mode == "skip" and login_mode == "auto":
        driver.activate_app(bundle_id)
        logging.info("[reset_app] 앱 실행 (초기화 없음)")

        alert = Alertnotification(driver, platform)
        if alert.is_noti_displayed():
            alert.click_noti_alert()
        else:
            logging.info("[SKIP] 알림 권한 팝업 미노출")

        time.sleep(3)
        alert.close_braze_if_present()

        account = TestAccount.AOS if platform == "aos" else TestAccount.IOS
        page    = LoginPage(driver, platform)
        replace = Replacedevicelist(driver, platform)

        page.open_deeplink(DeepLinks.MYRIDI)

        if not page.is_login_page_displayed():
            logging.info("[reset_app] 로그인 상태 감지 - 로그아웃 처리")
            page.click_logout()
            page.confirm_logout()
            page.click_confirm_logout()
            logging.info("[reset_app] 로그아웃 완료")
        else:
            logging.info("[reset_app] 로그아웃 상태 - 로그아웃 불필요")

    elif reset_mode == "skip" and login_mode == "skip":
        driver.activate_app(bundle_id)
        logging.info("[reset_app] 앱 실행 (초기화 없음 - 로그인 상태 유지)")

    yield

    driver.terminate_app(bundle_id)
    logging.info("[reset_app] 앱 종료")

def pytest_terminal_summary(terminalreporter, config):
    passed   = len(terminalreporter.stats.get("passed",   []))
    failed   = len(terminalreporter.stats.get("failed",   []))
    skipped  = len(terminalreporter.stats.get("skipped",  []))
    error    = len(terminalreporter.stats.get("error",    []))
    total    = passed + failed + skipped + error 

    elapsed = round(time.time() - terminalreporter._sessionstarttime, 2)

    platform = config.getoption("--platform", default="ios")
    log_dir     = os.path.join(LOG_DIR, platform)
    log_files   = sorted([f for f in os.listdir(log_dir) if f.endswith(".log")]) if os.path.exists(log_dir) else []
    log_file    = log_files[-1] if log_files else "로그 파일 없음"

    terminalreporter.write_sep("=", "테스트 결과")
    terminalreporter.write_line(f"테스트 기기 : {_active_device_info.get('device_name', 'unknown')}")
    terminalreporter.write_line(f"총 {total}개 실행")
    terminalreporter.write_line(f"✅ pass     : {passed}개")
    terminalreporter.write_line(f"❌ fail     : {failed}개")
    terminalreporter.write_line(f"🚫 skip     : {skipped}개")
    terminalreporter.write_line(f"⚠️ error    : {error}개")
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

        if drv is None:
            logging.warning("[screenshot] 드라이버 없음 - 스크린샷 스킵")
            return

        try: 
            screenshot_dir = os.path.join(SCREENSHOT_DIR, platform)
            os.makedirs(screenshot_dir, exist_ok=True)
            path = os.path.join(screenshot_dir, f"{ts}_{item.name}.png")
            drv.save_screenshot(path)
            logging.info(f"[screenshot] 저장 완료: {path}")
        except Exception as e:
            logging.warning(f"[screenshot] 저장 실패: {e}")
    
def pytest_addoption(parser):
    parser.addoption("--platform", default="ios",  help="플랫폼: aos | ios")
    parser.addoption("--env",      default="real",  help="환경: real | emulator | simulator")
    parser.addoption("--login",    default="auto",  help="로그인 방식: auto | skip")
    parser.addoption("--reset",    default="full",  help="앱 초기화: full | skip")


@pytest.fixture(scope="session")
def udid(request, platform):
    env    = request.config.getoption("--env", default="real")
    device = _find_active_device(platform, env)
    return device["udid"] if device else None

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_logreport(report):
    if report.failed and report.when == "call":
        class_name = report.nodeid.split("::")[1] if "::" in report.nodeid else None
        if class_name:
            _failed_classes.add(class_name)

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    class_name = item.nodeid.split("::")[1] if "::" in item.nodeid else None
    if class_name and class_name in _failed_classes:
        pytest.skip(f"[SKIP] {class_name} 이전 테스트 실패로 현재 클래스 스킵")


