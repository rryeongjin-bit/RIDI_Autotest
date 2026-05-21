
from pages.base_page import *
from pages.locators import *

class CartPage(BasePage):    
    def is_owntab_displayed(self) -> bool:
        locator = AOS_CartLocators.OWN_PAY_BTN if self.platform == "aos" \
                  else IOS_CartLocators.OWN_PAY_BTN
        return self.is_displayed(locator)
    
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

