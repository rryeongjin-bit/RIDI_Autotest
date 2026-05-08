from pages.base_page import *
from pages.locators import *

class Alertnotification(BasePage):
    def click_noti_alert(self):
        self.click(CommonLocators.ALLOW_BTN)

    def click_braze_alert(self):
        if self.platform == "aos":
            if self.is_present(CommonLocators.BRAZEPOPUP_CLOSE_AOS):
                self.click(CommonLocators.BRAZEPOPUP_CLOSE_AOS)
        else:
            if self.is_present(CommonLocators.BRAZEPOPUP_CLOSE_IOS):
                self.click(CommonLocators.BRAZEPOPUP_CLOSE_IOS)

# class MainhomePage(BasePage):
#     def click_my_btn(self):
#         self.click(MainhomeLocators.MY_BTN)
    