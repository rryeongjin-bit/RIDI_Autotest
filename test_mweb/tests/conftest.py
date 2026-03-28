import pytest
from appium import webdriver
from appium.options import AppiumOptions
from config.capabilities import *
from config.settings import *
from utils.helpers import *

# CLI 옵션

CAPS_MAP = {
    ("aos", "real",      "chrome"):  AOS_REAL_CHROME,
    ("aos", "real",      "samsung"): AOS_REAL_SAMSUNG,
    ("aos", "emulator",  "chrome"):  AOS_EMULATOR_CHROME,
    ("ios", "real",      "safari"):  IOS_REAL_SAFARI,
    ("ios", "real",      "chrome"):  IOS_REAL_CHROME,
    ("ios", "simulator", "safari"):  IOS_SIMULATOR_SAFARI,
    ("ios", "simulator", "chrome"):  IOS_SIMULATOR_CHROME,
}

# CLI 옵션 등록
def pytest_addoption(parser):
    parser.addoption(
        "--platform", action="store", default="aos",
        help="Target platform: aos | ios"
    )
    parser.addoption(
        "--env", action="store", default="real",
        help="Device environment: real | emulator | simulator"
    )
    parser.addoption(
        "--browser", action="store", default="chrome",
        help="Browser: chrome | samsung | safari"
    )

# session 범위 fixture : CLI 옵션 값 
@pytest.fixture(scope="session")
def platform(request):
    return request.config.getoption("--platform").lower()


@pytest.fixture(scope="session")
def env(request):
    return request.config.getoption("--env").lower()

@pytest.fixture(scope="session")
def browser(request):
    return request.config.getoption("--browser").lower()

# function 범위 fixture : Appium driver
@pytest.fixture(scope="function")
def driver(platform, env, browser):
    key = (platform, env, browser)
    caps = CAPS_MAP.get(key)

    if caps is None:
        raise ValueError(
            f"지원하지 않는 조합입니다 → platform={platform}, env={env}, browser={browser}\n"
            f"지원 목록: {list(CAPS_MAP.keys())}"
        )

    options = AppiumOptions().load_capabilities(caps)
    _driver = webdriver.Remote(APPIUM_SERVER_URL, options=options)
    _driver.implicitly_wait(TIMEOUT["implicit"])

    yield _driver

    _driver.quit()

# 테스트 실패 시 스크린샷 저장
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


@pytest.fixture(autouse=True)
def capture_on_failure(request, driver):
    yield
    rep = getattr(request.node, "rep_call", None)
    if rep and rep.failed:
        test_name = request.node.nodeid.replace("/", "_").replace("::", "__")
        path = save_screenshot(driver, f"{test_name}.png")
        print(f"\n❗️ 실패 스크린샷 저장: {path}")