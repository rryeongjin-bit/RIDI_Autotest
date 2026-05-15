from pages.base_page import *
from pages.locators import *

class Alertnotification(BasePage):
    def is_noti_displayed(self) -> bool:
        locator = CommonLocators.ALERT_ALLOW_AOS if self.platform == "aos" \
                else CommonLocators.ALERT_ALLOW_IOS
        return self.is_displayed(locator)   
    
    def click_noti_alert(self):
        if self.platform == "aos":
            self.click(CommonLocators.ALLOW_BTN_AOS)
        else:
            self.click(CommonLocators.ALLOW_BTN_IOS)

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

    def close_braze_if_present(self):
            if self.has_webview():
                self.switch_to_webview()
                self.wait_for_webview()
                if self.is_braze_displayed():
                    self.click_braze_alert()
                self.switch_to_native()
                self.wait_for_native()

class MainhomePage(BasePage):
    def is_genrehome_displayed(self) -> bool:
        locator = AOS_GenrehomeLocators.WEBTOON_TAB if self.platform == "aos" \
                  else IOS_GenrehomeLocators.WEBTOON_NEW_QUICK
        return self.is_displayed(locator)

class ContentshomePage(BasePage):
    def is_all_contents_title_displayed(self) -> bool:
        locator = AOS_ContentshomeLocators.ALL_CONTENTS_TITLE if self.platform == "aos" \
                else IOS_ContentshomeLocators.ALL_CONTENTS_TITLE
        return self.is_displayed(locator)
    
    def is_adult_contents_title_displayed(self) -> bool:
        locator = AOS_ContentshomeLocators.ADULT_CONTENTS_TITLE if self.platform == "aos" \
            else IOS_ContentshomeLocators.ADULT_CONTENTS_TITLE
        return self.is_displayed(locator)

    def click_episode_tab(self):
        if self.platform == "aos":
            self.click(AOS_ContentshomeLocators.CONTENTS_EPISODE_TAB)
        else:
            self.click(IOS_ContentshomeLocators.CONTENTS_EPISODE_TAB)

    def is_episode_tab_entered(self) -> bool:
        locator = AOS_ContentshomeLocators.CONTENTS_EPISODE_SORT if self.platform == "aos" \
                else IOS_ContentshomeLocators.CONTENTS_EPISODE_SORT
        return self.is_displayed(locator)

    def click_episode_sort(self):
        if self.platform == "aos":
            self.click(AOS_ContentshomeLocators.CONTENTS_EPISODE_SORT)
        else:
            self.click_by_visible(IOS_ContentshomeLocators.CONTENTS_EPISODE_SORT)

    def is_all_thumbnail_changed(self) -> bool:
        if self.platform == "aos":
            desc1 = self.get_thumbnail_content_desc(AOS_ContentshomeLocators.ALL_CONTENTS_THUMBNAIL_FIRST)
            desc2 = self.get_thumbnail_content_desc(AOS_ContentshomeLocators.ALL_CONTENTS_THUMBNAIL_SECOND)
        else:
            desc1 = self.get_thumbnail_content_desc(IOS_ContentshomeLocators.ALL_CONTENTS_THUMBNAIL_FIRST)
            desc2 = self.get_thumbnail_content_desc(IOS_ContentshomeLocators.ALL_CONTENTS_THUMBNAIL_SECOND)
        print(f"\ndesc1: {desc1}")
        print(f"\ndesc2: {desc2}")
        return desc1 != desc2
    
    def is_episode_1st_displayed(self) -> bool:
        locator = AOS_ContentshomeLocators.CONTENTS_EPISODE_FIRST if self.platform == "aos" \
                else IOS_ContentshomeLocators.CONTENTS_EPISODE_FIRST
        return self.is_displayed(locator)
        
    def click_episode_download(self):
        if self.platform == "aos":
            self.click(AOS_ContentshomeLocators.CONTENTS_EPISODE_DOWNLOAD)
        else:
            self.click(IOS_ContentshomeLocators.CONTENTS_EPISODE_DOWNLOAD)

    def is_download_btn_displayed(self)-> bool:
        locator = AOS_ContentshomeLocators.CONTENTS_EPISODE_DOWNLOAD if self.platform == "aos" \
                else IOS_ContentshomeLocators.CONTENTS_EPISODE_DOWNLOAD
        return self.is_displayed(locator)

    def is_paypopup_displayed(self) -> bool:
        locator = AOS_ContentshomeLocators.PAY_CASH_BTN if self.platform == "aos" \
                else IOS_ContentshomeLocators.PAY_CASH_BTN
        return self.is_displayed(locator)
    
    def click_pay_cash(self):
        if self.platform == "aos":
            self.click(AOS_ContentshomeLocators.PAY_CASH_BTN)
        else:
            self.click(IOS_ContentshomeLocators.PAY_CASH_BTN)

    def click_pay_rent_tab(self):
        if self.platform == "aos":
            self.click(AOS_ContentshomeLocators.PAY_RENT_TAB)
        else:
            self.click(IOS_ContentshomeLocators.PAY_RENT_TAB)

    def click_pay_rent_btn(self):
        if self.platform == "aos":
            self.click(AOS_ContentshomeLocators.PAY_RENT_BTN)
        else:
            self.click(IOS_ContentshomeLocators.PAY_RENT_BTN)

    def click_pay_buy_btn(self):
        if self.platform == "aos":
            self.click(AOS_ContentshomeLocators.PAY_OWN_BTN)
        else:
            self.click(IOS_ContentshomeLocators.PAY_OWN_BTN)

    def click_rent_ownership_displayed(self):
        if self.platform == "aos":
            if self.is_present(AOS_ContentshomeLocators.RENT_OWNERSHIP_LABEL):
                self.click(AOS_ContentshomeLocators.ALL_CONTENTS_EPISODE_ITEM)
        else:
            if self.is_present(IOS_ContentshomeLocators.RENT_OWNERSHIP_LABEL):
                self.click(IOS_ContentshomeLocators.ALL_CONTENTS_EPISODE_ITEM)
    
    def click_own_ownership_displayed(self):
        if self.platform == "aos":
            if self.is_present(AOS_ContentshomeLocators.OWN_OWNERSHIP_LABEL):
                self.click(AOS_ContentshomeLocators.ADULT_CONTENTS_EPISODE_ITEM)
        else:
            if self.is_present(IOS_ContentshomeLocators.OWN_OWNERSHIP_LABEL):
                self.click(IOS_ContentshomeLocators.ADULT_CONTENTS_EPISODE_ITEM)
    
    def get_first_download_episode_desc(self) -> str:
        """첫 번째 다운로드 버튼과 동일선상 회차 TextView text 반환"""
        el = self.find_element((AppiumBy.XPATH,
            '(//android.view.ViewGroup[@resource-id="downloadButton"])[1]/preceding-sibling::android.view.ViewGroup[@content-desc][1]//android.widget.TextView[1]'))
        return el.text
    
   

    def click_ownership_by_desc(self, desc: str):
        """저장된 회차명 TextView 클릭"""
        locator = (AppiumBy.XPATH,
            f'//android.widget.TextView[@text="{desc}"]')
        self.click_by_visible(locator)