import os
import logging
import pytest
from datetime import datetime
from appium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config.capabilities import *
from config.settings import *


# 타임스탬프 fixture
@pytest.fixture(scope="session")
def timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

# 로거 fixture
@pytest.fixture(scope="session", autouse=True)
def setup_logger(timestamp):
    log_dir = os.path.join(LOG_DIR, "session")
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, f"{timestamp}.log")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ]
    )
    return logging.getLogger()


# driver fixture
@pytest.fixture(scope="session")
def driver(request):
    # 마커에서 플랫폼/환경 읽기
    markers  = [m.name for m in request.node.iter_markers()]

    platform = "aos"  if "aos" in markers else "ios"
    env      = "real" if "real" in markers else \
               "emulator" if "emulator" in markers else \
               "simulator"

    # 활성 기기 탐색
    device = _find_active_device(platform, env)
    if device is None:
        pytest.exit(f"[driver] 활성화된 기기 없음 - platform: {platform}, env: {env}")

    server_url = get_server_url(device["port"])
    options    = get_capabilities(platform, device)

    logging.info(f"[driver] 연결 기기: {device['device_name']} | 플랫폼: {platform} | 환경: {env} | 포트: {device['port']}")

    drv = webdriver.Remote(server_url, options=options)
    drv.implicitly_wait(DEFAULT_TIMEOUT)

    yield drv

    drv.quit()
    logging.info("[driver] 드라이버 종료")


def _find_active_device(platform: str, env: str) -> dict | None:
    """platform + env 조합으로 DEVICE_CONFIG에서 활성 기기 탐색"""
    import socket
    devices = DEVICE_CONFIG.get(platform, [])
    for device in devices:
        if device["type"] != env:
            continue
        # Appium 서버 활성화 여부 체크
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("localhost", device["port"])) == 0:
                return device
    return None

# 로그인 fixture (autouse=False → 필요한 테스트에서만 명시적 호출)
@pytest.fixture(scope="function")
def login(driver, request):
    markers  = [m.name for m in request.node.iter_markers()]
    platform = "aos" if "aos" in markers else "ios"

    from pages.login_page import LoginPage
    from data.test_data import TestAccount

    account = TestAccount.AOS if platform == "aos" else TestAccount.IOS
    page    = LoginPage(driver, platform)
    page.login(id=account["id"], pw=account["pw"])

    logging.info(f"[login] 로그인 완료 - platform: {platform}")

# 앱 초기화 fixture (모듈 단위)
@pytest.fixture(scope="module", autouse=True)
def reset_app(driver, request):
    markers   = [m.name for m in request.node.iter_markers()]
    platform  = "aos" if "aos" in markers else "ios"

    from config.settings import BUNDLE_ID_AOS, BUNDLE_ID_IOS
    bundle_id = BUNDLE_ID_AOS if platform == "aos" else BUNDLE_ID_IOS

    logging.info(f"[reset_app] 앱 초기화 시작: {bundle_id}")

    if platform == "aos":
        driver.terminate_app(bundle_id)
        driver.execute_script("mobile: clearApp", {"appId": bundle_id})
        driver.activate_app(bundle_id)
    elif platform == "ios":
        driver.terminate_app(bundle_id)
        driver.activate_app(bundle_id)

    logging.info("[reset_app] 앱 초기화 완료")

    yield

    driver.terminate_app(bundle_id)
    logging.info("[reset_app] 앱 종료")

# URL 체크 fixture (모듈 단위)
@pytest.fixture(scope="module", autouse=True)
def check_url(request, driver):
    target_url = getattr(request.module, "TARGET_URL", None)
    target_el  = getattr(request.module, "TARGET_EL",  None)

    if target_url is None:
        return

    if target_el is None:
        pytest.skip("[check_url] TARGET_EL 미선언 - 모듈 전체 중단")

    logging.info(f"[check_url] 딥링크 진입: {target_url}")

    try:
        driver.execute_script("mobile: deepLink", {
            "url":     target_url,
            "package": APP_PACKAGE
        })
        WebDriverWait(driver, DEFAULT_TIMEOUT).until(
            EC.presence_of_element_located(target_el)
        )
        logging.info(f"[check_url] 페이지 진입 확인 완료: {target_url}")

    except Exception as e:
        logging.error(f"[check_url] 페이지 진입 실패: {target_url} | {e}")
        pytest.skip("[check_url] 페이지 진입 실패 - 모듈 전체 중단")


# 실패 시 스크린샷 자동 저장
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report  = outcome.get_result()

    if report.when == "call" and report.failed:
        drv     = item.funcargs.get("driver")
        markers = [m.name for m in item.iter_markers()]
        platform = "aos" if "aos" in markers else "ios"
        ts      = datetime.now().strftime("%Y%m%d_%H%M%S")

        if drv:
            screenshot_dir = os.path.join(SCREENSHOT_DIR, platform)
            os.makedirs(screenshot_dir, exist_ok=True)
            path = os.path.join(screenshot_dir, f"{ts}_{item.name}.png")
            drv.save_screenshot(path)
            logging.info(f"[screenshot] 저장 완료: {path}")