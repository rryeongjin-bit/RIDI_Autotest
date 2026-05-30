
from pages.base_page import *
from locators.checkout import *

class CheckoutPage(BasePage):
    def is_orderlist_section_displayed(self):
        locator = AOS_CheckoutLocators.ORDER_LIST_SECTION if self.platform == "aos" \
                  else IOS_CheckoutLocators.ORDER_LIST_SECTION
        return self.is_displayed(locator)

    def scroll_to_payment_detail_section(self):
        locator = (
            AOS_CheckoutLocators.PAYMENT_AGREE if self.platform == "aos" \
                else IOS_CheckoutLocators.PAYMENT_AGREE
        )

        return self.scroll_until_visible(locator, direction="up")
    
    def click_payment_agree(self):
        locator = AOS_CheckoutLocators.PAYMENT_AGREE if self.platform == "aos" \
                  else IOS_CheckoutLocators.PAYMENT_AGREE
        displayed = self.is_displayed(locator, timeout=3)
        self.log.info(
            f"[click_payment_agree] displayed={displayed}"
        )

        if not displayed:
            raise Exception(
                "결제 동의 토글 미노출"
            )

        self.click(locator)
        
    def click_payment_btn(self):
        if self.platform == "aos":
            self.click(AOS_CheckoutLocators.PAYMENT_BTN)
        else:
            self.click(IOS_CheckoutLocators.PAYMENT_BTN)
    
    def is_payment_complete_displayed(self):
        locator = AOS_CheckoutLocators.PAYMENT_COMPLETE if self.platform == "aos" \
                  else IOS_CheckoutLocators.PAYMENT_COMPLETE
        return self.is_displayed(locator)
    
    def click_move_to_home(self):
        if self.platform == "aos":
            self.click(AOS_CheckoutLocators.MOVE_TO_GENREHOME)
        else:
            self.click(IOS_CheckoutLocators.MOVE_TO_GENREHOME)