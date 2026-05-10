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

class MainhomePage(BasePage):
    def is_genrehome_displayed(self) -> bool:
        locator = AOS_GenrehomeLocators.WEBTOON_TAB if self.platform == "aos" \
                  else IOS_GenrehomeLocators.WEBTOON_NEW_QUICK
        return self.is_displayed(locator)
   
    