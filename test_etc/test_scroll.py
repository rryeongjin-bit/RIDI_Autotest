import time
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
from appium.webdriver.common.appiumby import AppiumBy

# ============================================================
# 설정값
# ============================================================
PLATFORM              = "android"
IS_EMULATOR           = True
CONFIGURED_PX_PER_SEC = 175
WAIT_DURATION         = 5.0   # 자동스크롤 대기 시간 (길수록 정확)
THRESHOLD_PX_PER_SEC  = 3.0   # 허용 오차 (물리px 기준)

APPIUM_SERVER = "http://127.0.0.1:4723"

# ============================================================
# Capabilities
# ============================================================
def get_android_caps():
    options = UiAutomator2Options()
    caps = {
        "platformName": "Android",
        "appPackage":  "com.initialcoms.ridi.staging",  
        "appActivity": "com.ridi.books.viewer.main.activity.SplashActivity",
        "noReset": True,
        "automationName": "UiAutomator2"
    }
    caps["deviceName"] = "emulator-5554" if IS_EMULATOR else "galaxy s25"
    options.load_capabilities(caps)
    return options

def get_ios_caps():
    options = XCUITestOptions()
    caps = {
        "platformName":   "iOS",
        "bundleId":       "com.your.app",
        "noReset":        True,
        "automationName": "XCUITest",
    }
    if IS_EMULATOR:
        caps["deviceName"] = "iPhone 15 Pro"
        caps["udid"]       = "your-simulator-uuid"
    else:
        caps["deviceName"] = "your_device_name"
        caps["udid"]       = "your-real-device-udid"
    options.load_capabilities(caps)
    return options



# ============================================================
# DPR 조회
# ============================================================
def get_dpr(driver):
    info    = driver.execute_script("mobile: deviceInfo")
    density = info.get("displayDensity", 160) if PLATFORM == "android" else 1
    dpr     = density / 160 if PLATFORM == "android" else info.get("pixelRatio", 2)
    print(f"[DPR] {dpr}")
    return dpr

# ============================================================
# 현재 화면에 보이는 첫번째 요소의 Y 위치 조회
# ============================================================
import re

# ============================================================
# uiautomator dump으로 reader_view 첫번째 자식 Y위치 조회
# ============================================================
def get_scroll_position_from_dump(driver):
    xml      = driver.page_source
    reader_idx = xml.find('id/reader_view')
    if reader_idx == -1:
        print("  ❌ reader_view를 찾지 못했어요")
        return None

    reader_section = xml[reader_idx:]
    children = re.findall(
        r'class="android\.widget\.FrameLayout"[^>]*bounds="\[0,(-?\d+)\]\[1080,(-?\d+)\]"',
        reader_section
    )
    if not children:
        print("  ❌ reader_view 자식 요소를 찾지 못했어요")
        return None

    # 마지막 자식의 y1 추적
    # → 스크롤할수록 새 자식이 아래서 올라오며 y1이 줄어듦
    last_y1 = int(children[-1][0])
    print(f"  [bounds] 마지막 자식 y1={last_y1}px (자식 수: {len(children)}개)")
    return float(last_y1)

# ============================================================
# 자동스크롤 속도 측정 (2점 측정)
# ============================================================
def measure_auto_scroll_speed(driver):
    dpr = get_dpr(driver)

    print(f"\n{'='*50}")
    print(f"[Step 1] 자동스크롤 시작 전 위치 측정")
    print(f"{'='*50}")

    # page_source 호출 후 타이머 시작 (호출 시간 제외)
    print(f"\n[Step 1] 자동스크롤 시작 전 위치 측정")
    print(f"{'='*50}")
    pos1 = get_scroll_position_from_dump(driver)
    if pos1 is None:
        print("❌ 위치 측정 실패")
        return

    print(f"  시작 위치: {pos1}px")
    print(f"\n[Step 2] 지금 자동스크롤을 시작하세요! {WAIT_DURATION}초 대기 중...")
    time.sleep(WAIT_DURATION)

    print(f"\n[Step 3] 자동스크롤 후 위치 측정")
    print(f"{'='*50}")
    pos2 = get_scroll_position_from_dump(driver)
    if pos2 is None:
        print("❌ 위치 측정 실패")
        return

    print(f"  종료 위치: {pos2}px")

    # 시간은 WAIT_DURATION 고정 (page_source 호출 시간 제외)
    elapsed        = WAIT_DURATION
    delta_logical  = abs(pos1 - pos2)
    delta_physical = delta_logical * dpr
    speed_logical  = delta_logical  / elapsed
    speed_physical = delta_physical / elapsed
    conf_physical  = CONFIGURED_PX_PER_SEC * dpr
    error_px       = abs(conf_physical - speed_physical)
    error_rate     = (error_px / conf_physical * 100) if conf_physical else 0

    print(f"\n{'='*50}")
    print(f"[측정 결과]")
    print(f"{'='*50}")
    print(f"측정 구간                : {elapsed:.2f}초")
    print(f"이동 거리 (CSS px)       : {delta_logical:.1f}px")
    print(f"이동 거리 (물리px)       : {delta_physical:.1f}px")
    print(f"configuredPxPerSec      : {CONFIGURED_PX_PER_SEC} (CSS px)")
    print(f"configuredPhysPxPerSec  : {conf_physical:.1f} (물리px)")
    print(f"avgMeasuredPxPerSec     : {speed_logical:.1f} (CSS px/s)")
    print(f"avgMeasuredPhysPxPerSec : {speed_physical:.1f} (물리px/s)")
    print(f"DPR                     : {dpr}")
    print(f"{'='*50}")
    print(f"오차 (물리px)           : {error_px:.1f} px/s")
    print(f"오차율                  : {error_rate:.1f}%")
    print(f"{'='*50}")
    result = "✅ PASS" if error_px <= THRESHOLD_PX_PER_SEC else "❌ FAIL"
    print(f"판정 (허용오차 {THRESHOLD_PX_PER_SEC}px/s) : {result}")
    print(f"{'='*50}\n")

# ============================================================
# 실행
# ============================================================
def test_auto_scroll_speed():
    if PLATFORM == "android":
        driver = webdriver.Remote(APPIUM_SERVER, options=get_android_caps())
    else:
        driver = webdriver.Remote(APPIUM_SERVER, options=get_ios_caps())

    try:
        info = driver.execute_script("mobile: deviceInfo")
        size = driver.get_window_size()
        dpr  = info.get("displayDensity", 160) / 160
        print(f"[해상도] 논리px: {size['width']} × {size['height']}")
        print(f"[해상도] 물리px: {size['width']*dpr:.0f} × {size['height']*dpr:.0f}")
        print(f"[해상도] DPR: {dpr}")

        print(f"\n콘텐츠 화면으로 이동 후 엔터를 눌러주세요...")
        input()

        measure_auto_scroll_speed(driver)
    finally:
        driver.quit()

if __name__ == "__main__":
    test_auto_scroll_speed()