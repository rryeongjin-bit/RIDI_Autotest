from pages.base_page import *
from pages.locators import *

class Alertnotification(BasePage):
    def click_noti_alert(self):
        self.click(CommonLocators.ALLOW_BTN)

    def click_braze_alert(self):
        self.switch_to_webview()
        
        if self.platform == "aos":
            if self.is_present(CommonLocators.BRAZEPOPUP_CLOSE_AOS):
                self.click(CommonLocators.BRAZEPOPUP_CLOSE_AOS)
        else:
            if self.is_present(CommonLocators.BRAZEPOPUP_CLOSE_IOS):
                self.click(CommonLocators.BRAZEPOPUP_CLOSE_IOS)
        
        self.switch_to_native()

class MainhomePage(BasePage):
    def is_genrehome_displayed(self) -> bool:
        """장르홈 진입 확인 - 플랫폼별 분기"""
        locator = GenrehomeLocators.WEBTOON_TAB_AOS if self.platform == "aos" \
                  else GenrehomeLocators.GENREHOME_TAB_IOS
        return self.is_displayed(locator)
   
    