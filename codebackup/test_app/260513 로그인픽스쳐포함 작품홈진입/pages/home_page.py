from pages.base_page import *
from pages.locators import *

class Alertnotification(BasePage):
    def click_noti_alert(self):
        self.click(CommonLocators.ALLOW_BTN)

    def close_braze_if_present(self):
            """브레이즈 팝업 노출 시 닫기"""
            if self.has_webview():
                self.switch_to_webview()
                self.wait_for_webview()
                if self.is_braze_displayed():
                    self.click_braze_alert()
                self.switch_to_native()
                self.wait_for_native()

    def is_braze_displayed(self) -> bool:
        locator = CommonLocators.BRAZEPOPUP_CLOSE_AOS if self.platform == "aos" \
            else CommonLocators.BRAZEPOPUP_CLOSE_IOS
        return self.is_present(locator)

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

class ContentshomePage(BasePage):
    def click_episode_tab(self):
        self.click(AOS_ContentshomeLocators.CONTENTS_EPISODE_TAB)

    def click_episode_sort(self):
        self.click(AOS_ContentshomeLocators.CONTENTS_EPISODE_SORT)

    def click_4th_episode(self):
        self.click(AOS_ContentshomeLocators.CONTENTS_4TH_EPISODE)

   
    