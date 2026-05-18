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

    def has_webview(self) -> bool:
        return any("WEBVIEW" in c for c in self.driver.contexts)

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
            self.log.info(f"[switch_to_webview] 전환 완료: {target}")

        except TimeoutException:
            self.log.error("[switch_to_webview] WebView 전환 타임아웃")
            raise

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
    
    def get_thumbnail_content_desc(self, locator: tuple) -> str:
        xpath = locator[1]
        
        if self.platform == "aos":
            match = re.search(r'@content-desc="([^"]+)"', xpath)
        else:
            match = re.search(r'@name="([^"]+)"', xpath)
        
        if match:
            return match.group(1)
        return ""

    def tap_by_coordinate(self, x: int, y: int):
        self.driver.execute_script("mobile: clickGesture", {"x": x, "y": y})
        self.log.info(f"[tap_by_coordinate] x:{x}, y:{y}")

    def tap_coordinate(self, x: int, y: int):
        if self.platform == "ios":
            # iOS는 mobile: clickGesture 미지원 → tap 액션 사용
            actions = ActionChains(self.driver)
            actions.w3c_actions.pointer_action.move_to_location(x, y)
            actions.w3c_actions.pointer_action.click()
            actions.perform()
        else:
            # Android
            self.driver.execute_script("mobile: clickGesture", {"x": x, "y": y})

    def scroll_up(self, percent=0.75):
        self._swipe(direction="up", percent=percent)

    def scroll_down(self, percent=0.75):
        self._swipe(direction="down", percent=percent)

    def _swipe(self, direction="up", percent=0.75):
        if self.platform == "ios":
            # iOS는 mobile: swipeGesture 미지원 → driver.swipe() 사용
            self.fallback_swipe(direction)
            return

        # Android
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

    # def scroll_to_element_center(self, locator, max_scroll=10):
    #     """
    #     특정 요소가 화면 중앙에 올 때까지 스크롤

    #     :param locator: locator tuple
    #     :param max_scroll: 최대 스크롤 횟수
    #     :return: element
    #     """

    #     screen_size = self.driver.get_window_size()
    #     screen_center_y = screen_size["height"] / 2

    #     for attempt in range(max_scroll):

    #         try:
    #             element = self.find_element(locator)

    #             # 요소 위치/크기
    #             location = element.location
    #             size = element.size

    #             # 요소 중앙 y좌표
    #             element_center_y = location["y"] + (size["height"] / 2)

    #             self.log.info(
    #                 f"[scroll_to_element_center] "
    #                 f"attempt={attempt}, "
    #                 f"element_center_y={element_center_y}, "
    #                 f"screen_center_y={screen_center_y}"
    #             )

    #             # 중앙 허용 범위 (±100)
    #             if abs(element_center_y - screen_center_y) <= 100:
    #                 self.log.info("[scroll_to_element_center] element centered")
    #                 return element

    #             # 요소가 화면 아래쪽 → 아래로 스크롤
    #             if element_center_y > screen_center_y:
    #                 self.scroll_down()

    #             # 요소가 화면 위쪽 → 위로 스크롤
    #             else:
    #                 self.scroll_up()

    #             time.sleep(1)

    #         except Exception as e:
    #             self.log.info(f"[scroll_to_element_center] not found: {e}")

    #             # 요소 못찾으면 아래로 계속 탐색
    #             self.scroll_down()
    #             time.sleep(1)

    #     raise Exception("요소를 화면 중앙으로 이동 실패")


    # def scroll_up_until_element_displayed(self, locator, max_scroll=5):
    #     """
    #     특정 요소가 보일 때까지 위로 스크롤

    #     :param locator: element locator
    #     :param max_scroll: 최대 스크롤 횟수
    #     :return: element
    #     """

    #     for attempt in range(max_scroll):

    #         if self.is_displayed(locator):
    #             self.log.info(
    #                 f"[scroll_up_until_element_displayed] "
    #                 f"element found (attempt={attempt})"
    #             )
    #             return self.find_element(locator)

    #         self.log.info(
    #             f"[scroll_up_until_element_displayed] "
    #             f"scroll_up (attempt={attempt})"
    #         )

    #         self.scroll_up()
    #         time.sleep(1)

    #     raise Exception(
    #         f"요소를 찾지 못했습니다. locator={locator}"
    # )