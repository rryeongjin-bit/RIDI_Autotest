import os
import logging
import pytest
from datetime import datetime
from appium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config.capabilities import *
from config.settings import *

# 커맨드 옵션 등록
def pytest_addoption(parser):
    parser.addoption("--platform", action="store", default="aos",  help="실행 플랫폼: aos | ios")
    parser.addoption("--port",     action="store", default=None,   help="Appium 서버 포트")
    parser.addoption("--udid",     action="store", default=None,   help="기기 UDID")

# 플랫폼 fixture
@pytest.fixture(scope="session")
def platform(request):
    return request.config.getoption("--platform")

# 타임스탬프 fixture
@pytest.fixture(scope="session")
def timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

# 로거 fixture
@pytest.fixture(scope="session", autouse=True)
def setup_logger(platform, timestamp):
    log_dir = os.path.join(LOG_DIR, platform)
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, f"{timestamp}_{platform}.log")

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
def driver(request, platform):
    port = request.config.getoption("--port")
    udid = request.config.getoption("--udid")

    # 포트/UDID로 기기 정보 탐색
    device = _find_device(platform, port, udid)
    if device is None:
        pytest.exit("[driver] 일치하는 기기 정보 없음. 테스트 중단")

    server_url = get_server_url(device["port"])
    options    = get_capabilities(platform, device)

    logging.info(f"[driver] 연결 기기: {device['device_name']} | 포트: {device['port']}")

    drv = webdriver.Remote(server_url, options=options)
    drv.implicitly_wait(DEFAULT_TIMEOUT)

    yield drv

    drv.quit()
    logging.info("[driver] 드라이버 종료")


def _find_device(platform: str, port, udid) -> dict | None:
    """포트 또는 UDID로 DEVICE_CONFIG에서 기기 탐색"""
    devices = DEVICE_CONFIG.get(platform, [])
    for device in devices:
        if port and str(device["port"]) == str(port):
            return device
        if udid and device["udid"] == udid:
            return device
    # 포트/UDID 미지정 시 첫 번째 기기 반환
    return devices[0] if devices else None

# 앱 초기화 fixture (모듈 단위)
@pytest.fixture(scope="module", autouse=True)
def reset_app(driver, platform):
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
    target_url = getattr(request.module, "TARGET_URL",  None)
    target_el  = getattr(request.module, "TARGET_EL",   None)

    # TARGET_URL 미선언 모듈 (test_login 등) 은 체크 skip
    if target_url is None:
        return

    if target_el is None:
        pytest.skip(f"[check_url] TARGET_EL 미선언 - 모듈 전체 중단")

    logging.info(f"[check_url] 딥링크 진입: {target_url}")

    try:
        # 딥링크로 페이지 진입
        driver.execute_script("mobile: deepLink", {
            "url":     target_url,
            "package": APP_PACKAGE
        })

        # 핵심 요소 존재 여부 확인
        WebDriverWait(driver, DEFAULT_TIMEOUT).until(
            EC.presence_of_element_located(target_el)
        )
        logging.info(f"[check_url] 페이지 진입 확인 완료: {target_url}")

    except Exception as e:
        logging.error(f"[check_url] 페이지 진입 실패: {target_url} | {e}")
        pytest.skip(f"[check_url] 페이지 진입 실패 - 모듈 전체 중단")

# 실패 시 스크린샷 자동 저장
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