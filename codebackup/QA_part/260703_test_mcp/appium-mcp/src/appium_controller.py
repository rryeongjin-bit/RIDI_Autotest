"""
AppiumController: Appium 세션 생성/관리 및 기기 제어 핵심 로직
iOS / Android 동시 세션 지원
"""

import base64
import logging
import subprocess
from typing import Optional

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, WebDriverException
)

logger = logging.getLogger(__name__)

# ── URL ─────────────────────────────────────────────────────
ANDROID_APPIUM_URL = "http://127.0.0.1:4723"
IOS_APPIUM_URL = "http://127.0.0.1:4725"

# ── 번들 ID 목록 ─────────────────────────────────────────────
ANDROID_BUNDLE_IDS = {
    "ridi": "com.initialcoms.ridi",
    "ridi_stage": "com.initialcoms.staging",
    "ridi_dev": "com.initialcoms.dev",
    "ridi_one": "com.ridi.books.onestore",
    "ridi_one_stage": "com.ridi.books.onestore.staging",
    "ridi_one_dev": "com.ridi.books.onestore.dev",
}

IOS_BUNDLE_IDS = {
    "ridi": "com.initialcoms.BOM",
    "ridi_stage": "com.initialcoms.BOM.staging",
    "ridi_dev": "com.initialcoms.BOM.dev",
}

# ── 기기 자동 감지 ────────────────────────────────────────────
def get_android_device_serial() -> str:
    """연결된 Android 기기 시리얼 자동 감지"""
    result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
    lines = result.stdout.strip().splitlines()
    devices = [l.split("\t")[0] for l in lines[1:] if "\tdevice" in l]
    if not devices:
        raise RuntimeError("연결된 Android 기기가 없습니다.")
    return devices[0]

def get_ios_udid() -> str:
    """연결된 iOS 기기 UDID 자동 감지"""
    result = subprocess.run(["idevice_id", "-l"], capture_output=True, text=True)
    udids = [l.strip() for l in result.stdout.strip().splitlines() if l.strip()]
    if not udids:
        raise RuntimeError("연결된 iOS 기기가 없습니다.")
    return udids[0]

# ── Capabilities 기본값 ──────────────────────────────────────
ANDROID_CAPS = {
    "platformName": "Android",
    "appium:automationName": "UiAutomator2",
    "appium:noReset": True,
    "appium:newCommandTimeout": 300,
}

IOS_CAPS = {
    "platformName": "iOS",
    "appium:automationName": "XCUITest",
    "appium:noReset": True,
    "appium:newCommandTimeout": 300,
    "appium:wdaLaunchTimeout": 60000,
}


class AppiumController:
    def __init__(self):
        # 플랫폼별 드라이버 독립 관리
        self.drivers: dict[str, webdriver.Remote] = {}  # {"ios": driver, "android": driver}
        self.active_platform: Optional[str] = None      # 현재 명령 대상 플랫폼

    # ── 세션 관리 ────────────────────────────────────────────

    def connect(self, platform: str, bundle_id: str = None) -> str:
        """Appium 세션 생성. platform: 'ios' | 'android'"""
        platform = platform.lower()
        if platform not in ("ios", "android"):
            raise ValueError("platform must be 'ios' or 'android'")

        # 해당 플랫폼 기존 세션만 종료 (다른 플랫폼 세션 유지)
        self._quit_platform(platform)

        if platform == "android":
            caps = dict(ANDROID_CAPS)
            caps["appium:deviceName"] = get_android_device_serial()
            resolved = ANDROID_BUNDLE_IDS.get(bundle_id) or bundle_id or ANDROID_BUNDLE_IDS["ridi_one"]
            caps["appium:appPackage"] = resolved
            # caps["appium:appActivity"] = ".activity.MainActivity"
            options = UiAutomator2Options().load_capabilities(caps)
            actual_bundle = caps["appium:appPackage"]
            url = ANDROID_APPIUM_URL
        else:  # ios
            caps = dict(IOS_CAPS)
            caps["appium:udid"] = get_ios_udid()
            resolved = IOS_BUNDLE_IDS.get(bundle_id) or bundle_id or IOS_BUNDLE_IDS["ridi"]
            caps["appium:bundleId"] = resolved
            options = XCUITestOptions().load_capabilities(caps)
            actual_bundle = caps["appium:bundleId"]
            url = IOS_APPIUM_URL

        driver = webdriver.Remote(url, options=options)
        self.drivers[platform] = driver
        self.active_platform = platform  # 새로 연결한 플랫폼을 활성으로 설정
        session_id = driver.session_id
        logger.info(f"[{platform}] Session created: {session_id}, bundle: {actual_bundle}")
        return f"✅ {platform.upper()} 세션 연결됨 (session_id: {session_id}, bundle: {actual_bundle})"

    def switch_platform(self, platform: str) -> str:
        """활성 플랫폼 전환 (이미 연결된 세션 간 전환)"""
        platform = platform.lower()
        if platform not in self.drivers:
            connected = list(self.drivers.keys())
            raise RuntimeError(f"'{platform}' 세션이 없습니다. 연결된 플랫폼: {connected}")
        self.active_platform = platform
        return f"✅ 활성 플랫폼 전환: {platform.upper()}"

    def disconnect(self, platform: str = None) -> str:
        """세션 종료. platform 미지정 시 활성 플랫폼 종료"""
        target = (platform or self.active_platform or "").lower()
        if not target:
            raise RuntimeError("종료할 플랫폼을 지정하거나 먼저 connect()를 호출하세요.")
        self._quit_platform(target)
        # 활성 플랫폼이 종료된 경우 남은 세션으로 전환
        if self.active_platform == target:
            remaining = list(self.drivers.keys())
            self.active_platform = remaining[0] if remaining else None
        return f"✅ {target.upper()} 세션 종료됨" + (
            f" (활성 플랫폼 → {self.active_platform.upper()})" if self.active_platform else ""
        )

    def get_status(self) -> str:
        if not self.drivers:
            return "❌ 연결된 세션 없음"
        lines = [f"활성 플랫폼: {(self.active_platform or 'none').upper()}"]
        for platform, driver in self.drivers.items():
            try:
                ctx = driver.current_context
                lines.append(f"  ✅ {platform.upper()} 활성 | context: {ctx}")
            except Exception:
                lines.append(f"  ⚠️ {platform.upper()} 세션 응답 없음")
        return "\n".join(lines)

    # ── 스크린샷 ─────────────────────────────────────────────

    def screenshot(self) -> dict:
        """스크린샷을 찍고 base64로 인코딩하여 반환"""
        driver = self._get_driver()
        import os, time
        from PIL import Image
        import io
        path = os.path.expanduser(f"~/Desktop/appium-mcp/screenshot/ridi_screenshot_{int(time.time())}.png")
        driver.get_screenshot_as_file(path)

        img = Image.open(path)
        img = img.convert("RGB")
        img = img.resize((img.width // 2, img.height // 2), Image.LANCZOS)
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=70)
        image_data = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return {
            "type": "image",
            "data": image_data,
            "mediaType": "image/jpeg",
            "path": path
        }

    # ── 탭 / 클릭 ────────────────────────────────────────────

    def tap(self, x: int, y: int) -> str:
        driver = self._get_driver()
        driver.tap([(x, y)])
        return f"✅ 탭: ({x}, {y})"

    def tap_by_accessibility_id(self, accessibility_id: str, timeout: int = 10) -> str:
        driver = self._get_driver()
        el = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, accessibility_id))
        )
        el.click()
        return f"✅ accessibility_id='{accessibility_id}' 탭 완료"

    def tap_by_xpath(self, xpath: str, timeout: int = 10) -> str:
        driver = self._get_driver()
        el = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((AppiumBy.XPATH, xpath))
        )
        el.click()
        return f"✅ xpath='{xpath}' 탭 완료"

    def tap_by_text(self, text: str, timeout: int = 10) -> str:
        driver = self._get_driver()
        if self.active_platform == "android":
            locator = (AppiumBy.ANDROID_UIAUTOMATOR,
                       f'new UiSelector().text("{text}")')
        else:
            locator = (AppiumBy.ACCESSIBILITY_ID, text)
        el = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(locator)
        )
        el.click()
        return f"✅ text='{text}' 탭 완료"

    # ── 텍스트 입력 ───────────────────────────────────────────

    def type_text(self, accessibility_id: str, text: str, timeout: int = 10) -> str:
        driver = self._get_driver()
        el = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, accessibility_id))
        )
        el.clear()
        el.send_keys(text)
        return f"✅ '{accessibility_id}'에 텍스트 입력: '{text}'"

    def type_text_by_xpath(self, xpath: str, text: str, timeout: int = 10) -> str:
        driver = self._get_driver()
        el = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((AppiumBy.XPATH, xpath))
        )
        el.clear()
        el.send_keys(text)
        return f"✅ xpath='{xpath}'에 텍스트 입력: '{text}'"

    # ── 스와이프 / 스크롤 ─────────────────────────────────────

    def swipe(self, start_x: int, start_y: int,
              end_x: int, end_y: int, duration_ms: int = 500) -> str:
        driver = self._get_driver()
        driver.swipe(start_x, start_y, end_x, end_y, duration_ms)
        return f"✅ 스와이프: ({start_x},{start_y}) → ({end_x},{end_y})"

    def scroll_down(self, times: int = 3) -> str:
        driver = self._get_driver()
        size = driver.get_window_size()
        w, h = size["width"], size["height"]
        cx = w // 2
        for _ in range(times):
            driver.swipe(cx, int(h * 0.7), cx, int(h * 0.3), 600)
        return f"✅ 아래로 {times}회 스크롤"

    def scroll_up(self, times: int = 3) -> str:
        driver = self._get_driver()
        size = driver.get_window_size()
        w, h = size["width"], size["height"]
        cx = w // 2
        for _ in range(times):
            driver.swipe(cx, int(h * 0.3), cx, int(h * 0.7), 600)
        return f"✅ 위로 {times}회 스크롤"

    # ── UI 계층 / 요소 탐색 ───────────────────────────────────

    def get_page_source(self) -> str:
        driver = self._get_driver()
        source = driver.page_source
        if len(source) > 8000:
            return source[:8000] + "\n...(truncated)"
        return source

    def find_elements(self, strategy: str, value: str) -> str:
        driver = self._get_driver()
        by_map = {
            "accessibility_id": AppiumBy.ACCESSIBILITY_ID,
            "xpath": AppiumBy.XPATH,
            "class_name": AppiumBy.CLASS_NAME,
            "id": AppiumBy.ID,
        }
        by = by_map.get(strategy)
        if not by:
            raise ValueError(f"지원하지 않는 strategy: {strategy}")

        elements = driver.find_elements(by, value)
        if not elements:
            return f"❌ 요소 없음: {strategy}='{value}'"

        lines = [f"✅ {len(elements)}개 요소 발견:"]
        for i, el in enumerate(elements[:20]):
            try:
                label = el.get_attribute("label") or el.get_attribute("content-desc") or el.text or "(no label)"
                lines.append(f"  [{i}] {label}")
            except Exception:
                lines.append(f"  [{i}] (읽기 실패)")
        return "\n".join(lines)

    def element_exists(self, accessibility_id: str) -> str:
        driver = self._get_driver()
        try:
            driver.find_element(AppiumBy.ACCESSIBILITY_ID, accessibility_id)
            return f"✅ 요소 존재: '{accessibility_id}'"
        except NoSuchElementException:
            return f"❌ 요소 없음: '{accessibility_id}'"

    # ── 앱 제어 ───────────────────────────────────────────────

    def launch_app(self) -> str:
        driver = self._get_driver()
        if self.active_platform == "android":
            app_id = ANDROID_BUNDLE_IDS["ridi_one"]
        else:
            app_id = IOS_BUNDLE_IDS["ridi"]
        driver.activate_app(app_id)
        return f"✅ 앱 실행: {app_id}"

    def terminate_app(self) -> str:
        driver = self._get_driver()
        app_id = (driver.capabilities.get("appium:bundleId") or
                  driver.capabilities.get("appium:appPackage"))
        driver.terminate_app(app_id)
        return f"✅ 앱 종료: {app_id}"

    def background_app(self, seconds: int = 3) -> str:
        driver = self._get_driver()
        driver.background_app(seconds)
        return f"✅ 앱을 {seconds}초 백그라운드 처리"

    def get_window_size(self) -> str:
        driver = self._get_driver()
        size = driver.get_window_size()
        return f"✅ 화면 크기: {size['width']} x {size['height']}"

    # ── 내부 헬퍼 ────────────────────────────────────────────

    def _get_driver(self) -> webdriver.Remote:
        """활성 플랫폼의 드라이버 반환"""
        if not self.active_platform or self.active_platform not in self.drivers:
            connected = list(self.drivers.keys())
            if not connected:
                raise RuntimeError("연결된 Appium 세션이 없습니다. connect() 먼저 호출하세요.")
            raise RuntimeError(
                f"활성 플랫폼이 설정되지 않았습니다. 연결된 플랫폼: {connected}"
            )
        return self.drivers[self.active_platform]

    def _quit_platform(self, platform: str):
        """특정 플랫폼 세션만 종료"""
        driver = self.drivers.pop(platform, None)
        if driver:
            try:
                driver.quit()
            except Exception:
                pass