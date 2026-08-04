
from pages.base_page import *
from locators.cart import *

class CartPage(BasePage):    
    def is_owntab_displayed(self, timeout: int = DEFAULT_TIMEOUT) -> bool:
        if self.platform == "aos":
            try:
                if "WEBVIEW" not in self.driver.current_context:
                    self.switch_to_webview()
                    self.wait_for_webview()
                return self.is_displayed(AOS_CartLocators.OWN_PAY_BTN, timeout)
            except Exception:
                return False
        else:
            return self.is_displayed(IOS_CartLocators.OWN_PAY_BTN, timeout)
    
    def click_owntab(self):
        if self.platform == "aos":
            self.click(AOS_CartLocators.OWN_PAY_BTN)
        else:
            self.click(IOS_CartLocators.OWN_TAB)
    
    def click_checkbox_all(self):
        if self.platform == "aos":
            self.click(AOS_CartLocators.CHECKBOX_ALL)
        else:
            self.click(IOS_CartLocators.CHECKBOX_ALL)

    def click_checkbox_first(self):
        if self.platform == "aos":
            self.click(AOS_CartLocators.CHECKBOX_FIRST)
        else:
            self.tap_coordinate(10, 574)

    def click_own_pay(self):
        if self.platform == "aos":
            self.click(AOS_CartLocators.OWN_PAY_BTN)
        else:
            self.click(IOS_CartLocators.OWN_PAY_BTN)

