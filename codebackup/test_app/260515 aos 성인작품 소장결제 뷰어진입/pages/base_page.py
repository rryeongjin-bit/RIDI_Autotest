import re
import logging
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

