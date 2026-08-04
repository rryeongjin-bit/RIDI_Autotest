import re
import time
import logging
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config.settings import *

class BasePage:
    def __init__(self, driver, platform: str):
        self.driver   = driver
        self.platform = platform
        self.log      = logging.getLogger(__name__)

    def find_element(self, locator: tuple):
        try:
            return self.driver.find_element(*locator)
        except NoSuchElementException as e:
            self.log.error(f"[find_element] 요소 없음: {locator} | {e}")
            raise

    def find_elements(self, locator: tuple):
        return self.driver.find_elements(*locator)

    def wait_for_element(self, locator: tuple, timeout: int = DEFAULT_TIMEOUT):
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
        except TimeoutException:
            self.log.error(f"[wait_for_element] 타임아웃: {locator} | {timeout}s")
            raise

    def wait_for_element_visible(self, locator: tuple, timeout: int = DEFAULT_TIMEOUT):
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
        except TimeoutException:
            self.log.error(f"[wait_for_element_visible] 타임아웃: {locator} | {timeout}s")
            raise

    def wait_for_element_clickable(self, locator: tuple, timeout: int = DEFAULT_TIMEOUT):
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
        except TimeoutException:
            self.log.error(f"[wait_for_element_clickable] 타임아웃: {locator} | {timeout}s")
            raise

    def click(self, locator: tuple):
        el = self.wait_for_element_clickable(locator)
        el.click()
        self.log.info(f"[click] {locator}")
    
    def click_by_visible(self, locator: tuple):
        el = self.wait_for_element_visible(locator)
        el.click()
        self.log.info(f"[click_by_visible] {locator}")

    def send_keys(self, locator: tuple, value: str):
        el = self.wait_for_element_visible(locator)
        el.clear()
        el.send_keys(value)
        self.log.info(f"[send_keys] {locator} | value: {value}")

    def get_text(self, locator: tuple) -> str:
        el = self.wait_for_element_visible(locator)
        return el.text

    def is_displayed(self, locator: tuple, timeout: int = DEFAULT_TIMEOUT) -> bool:
        try:
            self.wait_for_element_visible(locator, timeout)
            return True
        except TimeoutException:
            return False
    
    def is_present(self, locator: tuple, timeout: int = DEFAULT_TIMEOUT) -> bool:
        try:
            self.wait_for_element_visible(locator, timeout)
            return True
        except (NoSuchElementException, TimeoutException):
            return False
        
    def is_element_present(self, locator: tuple, timeout: int = DEFAULT_TIMEOUT) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except (NoSuchElementException, TimeoutException):
            return False

    def has_webview(self) -> bool:
        if self.platform == "ios":
            return any("WEBVIEW" in c for c in self.driver.contexts)
        try:
            contexts = self.driver.contexts
            webviews = [c for c in contexts if "WEBVIEW" in c]
            if not webviews:
                return False
            
            current_context = self.driver.current_context
            self.driver.switch_to.context(webviews[-1])
            
            for handle in reversed(self.driver.window_handles):
                self.driver.switch_to.window(handle)
                url = self.driver.current_url
                if url and url not in ("about:blank", ""):
                    self.driver.switch_to.context(current_context)
                    return True
            
            self.driver.switch_to.context(current_context)
            return False
        except Exception:
            return False
    
    def switch_to_webview(self, timeout: int = NETWORK_TIMEOUT):
        if self.platform == "ios":
            self.log.info("[switch_to_webview] iOS - 전환 스킵")
            return

        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: len([
                    ctx for ctx in d.contexts
                    if "WEBVIEW" in ctx
                ]) > 0
            )
            contexts = self.driver.contexts
            webviews = [ctx for ctx in contexts if "WEBVIEW" in ctx]

            if not webviews:
                raise RuntimeError("[switch_to_webview] WebView 컨텍스트 없음")

            target = webviews[-1]
            self.driver.switch_to.context(target)
            time.sleep(0.5)

            handles = self.driver.window_handles
            for handle in handles:
                self.driver.switch_to.window(handle)
                url = self.driver.current_url
                self.log.info(f"[switch_to_webview] handle: {handle} | url: {url}")
                if url and url not in ("about:blank", ""):
                    self.log.info(f"[switch_to_webview] 유효한 window 선택: {handle}")
                    break

            self.log.info(f"[switch_to_webview] 전환 완료: {target}")
            self.log.info(f"[switch_to_webview] current_url: {self.driver.current_url}")
            self.log.info(f"[switch_to_webview] title: {self.driver.title}")
            self.log.info(f"[switch_to_webview] window_handles: {self.driver.window_handles}")

        except TimeoutException:
            self.log.error("[switch_to_webview] WebView 전환 타임아웃")
            raise
    
    def switch_to_webview_with_retry(self, timeout: int = NETWORK_TIMEOUT, retries: int = 3):
        if self.platform == "ios":
            self.log.info("[switch_to_webview_with_retry] iOS - 전환 스킵")
            return

        for attempt in range(retries):
            try:
                self.switch_to_webview(timeout)
                self.wait_for_webview(timeout)
                return
            except Exception as e:
                self.log.warning(f"[switch_to_webview_with_retry] 시도 {attempt + 1}/{retries} 실패: {e}")
                self.switch_to_native()
                self.wait_for_native()
                time.sleep(2)

        raise RuntimeError("[switch_to_webview_with_retry] 웹뷰 전환 최종 실패")

    def switch_to_native(self):
        if self.platform == "ios":
            self.log.info("[switch_to_native] iOS - 전환 스킵")
            return

        self.driver.switch_to.context("NATIVE_APP")
        self.log.info("[switch_to_native] 네이티브 전환 완료")

    def wait_for_webview(self, timeout=10):
        if self.platform == "ios":
            self.log.info("[wait_for_webview] iOS - 대기 스킵")
            return

        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: any("WEBVIEW" in c for c in d.contexts)
            )
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )

            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script(
                    "return document.querySelector('button, input, a') !== null"
                )
            )
            self.log.info("[wait_for_webview] 웹뷰 로드 완료")
        except Exception as e:
            self.log.warning(f"[wait_for_webview] 웹뷰 로드 대기 중 예외 발생 - 계속 진행: {e}")
        

    def wait_for_native(self, timeout=10):
        if self.platform == "ios":
            self.log.info("[wait_for_native] iOS - 대기 스킵")
            return

        WebDriverWait(self.driver, timeout).until(
            lambda d: d.current_context == "NATIVE_APP"
        )
     
        WebDriverWait(self.driver, timeout).until(
            lambda d: len(d.find_elements("xpath", "//*")) > 0
        )
        self.log.info("[wait_for_native] 네이티브 전환 완료")

    def open_deeplink(self, url: str):

        if self.platform == "aos":
            self.driver.execute_script("mobile: deepLink", {
                "url":     url,
                "package": APP_PACKAGE
            })
        else:
            self.driver.execute_script("mobile: deepLink", {
                "url": url
            })
        time.sleep(5)

    
    def get_thumbnail_content_desc(self, locator: tuple) -> str:
        xpath = locator[1]
        
        if self.platform == "aos":
            match = re.search(r'@content-desc="([^"]+)"', xpath)
        else:
            match = re.search(r'@name="([^"]+)"', xpath)
        
        if match:
            return match.group(1)
        return ""

    def tap_coordinate(self, x: int, y: int):
        if self.platform == "ios":
            actions = ActionChains(self.driver)
            actions.w3c_actions.pointer_action.move_to_location(x, y)
            actions.w3c_actions.pointer_action.click()
            actions.perform()
        else:
            self.driver.execute_script("mobile: clickGesture", {"x": x, "y": y})

    def scroll_up(self, percent=0.75):
        self._swipe(direction="up", percent=percent)

    def scroll_down(self, percent=0.75):
        self._swipe(direction="down", percent=percent)

    def _swipe(self, direction="up", percent=0.75):
        if self.platform == "ios":
            self.fallback_swipe(direction)
            return
        size = self.driver.get_window_size()
        self.driver.execute_script("mobile: swipeGesture", {
            "left": int(size["width"] * 0.2),
            "top": int(size["height"] * 0.2),
            "width": int(size["width"] * 0.6),
            "height": int(size["height"] * 0.6),
            "direction": direction,
            "percent": percent
        })
        self.log.info(f"[swipe] direction={direction}")
        time.sleep(0.5)
    
    def scroll_until_visible(self, locator, direction="up", max_scroll=7):
        for i in range(max_scroll):
            self.log.info(f"[scroll_until] attempt={i}")
            try:
                if self.is_displayed(locator, timeout=2):
                    self.log.info("[scroll_until] FOUND")
                    return self.find_element(locator)

            except Exception as e:
                self.log.info(f"[scroll_until] not found: {e}")

            if direction == "up":
                self.scroll_up()
            else:
                self.scroll_down()
        raise Exception(f"[scroll_until] 요소 못 찾음: {locator}")

    def fallback_swipe(self, direction="up"):
        size = self.driver.get_window_size()
        start_x = size["width"] // 2

        if direction == "up":
            start_y = int(size["height"] * 0.8)
            end_y   = int(size["height"] * 0.2)
        else:
            start_y = int(size["height"] * 0.2)
            end_y   = int(size["height"] * 0.8)

        self.driver.swipe(start_x, start_y, start_x, end_y, 800)
        self.log.info(f"[fallback_swipe] {direction}")
    
    def safe_scroll_up(self):
        try:
            self.scroll_up()
        except Exception:
            self.fallback_swipe("up")

    def scroll_uiautomator(self, instance=0):
        """UiScrollable로 스크롤 - mobile: swipeGesture가 안 먹히는 중첩 컨테이너용"""
        try:
            self.driver.execute_script("mobile: scroll", {
                "strategy": "uiautomator",
                "selector": f"new UiScrollable(new UiSelector().scrollable(true).instance({instance})).scrollForward()",
            })
            self.log.info(f"[scroll_uiautomator] instance={instance}")
        except Exception as e:
            self.log.info(f"[scroll_uiautomator] 실패, fallback_swipe: {e}")
            self.fallback_swipe("up")