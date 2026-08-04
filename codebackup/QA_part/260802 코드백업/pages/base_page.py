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

    def dismiss_ios_system_alert(self) -> bool:
        """iOS 알림/앱추적투명성(ATT) 권한 시스템 팝업을 허용 처리한다. 팝업이 없으면 조용히
        False를 반환한다(정상 흐름).

        이 시스템 알림은 WDA의 일반 find_element/xpath 탐색 범위 밖에 있어 로케이터로는 전혀
        잡히지 않고, XCTest의 시스템 알림 전용 API인 mobile: alert만 동작한다(실기기 확인,
        2026-07-23 - Appium MCP로 tap_by_xpath/tap_by_text 둘 다 실패, 좌표 탭만 성공했음).

        중요: 이 팝업이 떠 있는 동안은 WDA가 알럿 창만 보게 되어 뒤에 있는 앱 요소를 아무것도
        찾지 못한다. 그래서 대기시간을 늘려도 해결되지 않고, 팝업을 먼저 치워야 한다
        (2026-07-29 iOS 실기기 확인 - watchdog 재시작 시 로그인 단계에서 "로그아웃"(5초)과
        "로그인"(10초)이 연달아 타임아웃났는데, 실패 스크린샷에는 이미 로그인된 장르홈 위로
        알림 권한 팝업이 덮여 있었다). 장르홈 진입부가 이 처리를 두 번 연달아 호출하는 것도
        알림/ATT 두 팝업이 겹쳐 뜰 수 있기 때문이다.

        BasePage에 두어 로그인 등 장르홈 밖 화면에서도 같은 처리를 쓸 수 있게 한다."""
        if self.platform != "ios":
            return False
        try:
            self.driver.execute_script("mobile: alert", {"action": "accept"})
            self.log.info("[시스템팝업] 알림/ATT 팝업 감지되어 허용 처리")
            time.sleep(1)
            return True
        except Exception:
            return False

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

    def has_webview(self, timeout: int = 30) -> bool:
        if self.platform == "ios":
            return any("WEBVIEW" in c for c in self.driver.contexts)
        else:
            try:
                WebDriverWait(self.driver, timeout).until(
                    lambda d: any("WEBVIEW" in c for c in d.contexts)
                )
                contexts = self.driver.contexts
                webviews = [c for c in contexts if "WEBVIEW" in c]
                if not webviews:
                    return False

                current_context = self.driver.current_context
                self.driver.switch_to.context(webviews[-1])

                for handle in reversed(self.driver.window_handles):
                    self.driver.switch_to.window(handle)
                    url = self.driver.current_url
                    if url and url not in ("about:blank", "") and not url.startswith("file://"):
                        self.driver.switch_to.context(current_context)
                        return True

                self.driver.switch_to.context(current_context)
                return False
            except TimeoutException:
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
        self.log.info(f"[tap_coordinate] x={x}, y={y}")
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
            if self.platform == "ios":
                start_y = int(size["height"] * 0.7)
                end_y   = int(size["height"] * 0.3)
            else:  
                start_y = int(size["height"] * 0.65)
                end_y   = int(size["height"] * 0.35)
        else:
            if self.platform == "ios":
                start_y = int(size["height"] * 0.3)
                end_y   = int(size["height"] * 0.7)
            else:  
                start_y = int(size["height"] * 0.65)
                end_y   = int(size["height"] * 0.35)

        self.driver.swipe(start_x, start_y, start_x, end_y, 800)
        self.log.info(f"[fallback_swipe] {direction}")

    def scroll_uiautomator(self, instance=0):
        """AOS는 mobile: scroll의 selector strategy 문자열이 "uiautomator"가 아니라
        "-android uiautomator"여야 하는데 잘못 지정되어 있어(InvalidSelectorException),
        매번 예외가 나서 의도한 UiScrollable 스크롤 대신 원시 좌표 스와이프(fallback_swipe)로
        계속 떨어지고 있었다. 이 원시 스와이프가 실기기(삼성)에서 딜레이 없이 반복 실행되며
        기기 제스처 인식이 멀티태스킹(최근 앱) 진입으로 오인해 앱이 백그라운드로 빠지는
        문제로 이어짐(실기기 확인, 2026-07-24, TestSelectbuy_Cart 선택가능 회차 탐색 스크롤
        중 재현). selector strategy 문자열을 바로잡아 정상적으로 UiScrollable을 타도록
        수정한다."""
        if self.platform == "ios":
            self.fallback_swipe("up")
            self.log.info(f"[scroll_uiautomator] instance={instance}")
        else:
            try:
                self.driver.execute_script("mobile: scroll", {
                    "strategy": "-android uiautomator",
                    "selector": f"new UiScrollable(new UiSelector().scrollable(true).instance({instance})).scrollForward()",
                })
                self.log.info(f"[scroll_uiautomator] instance={instance}")
            except Exception as e:
                self.log.info(f"[scroll_uiautomator] 실패, fallback_swipe: {e}")
                self.fallback_swipe("up")