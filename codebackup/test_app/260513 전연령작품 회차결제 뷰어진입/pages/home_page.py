from pages.base_page import *
from pages.locators import *

class Alertnotification(BasePage):
    def click_noti_alert(self):
        self.click(CommonLocators.ALLOW_BTN)

    def close_braze_if_present(self):
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

class ContentshomePage_Allages(BasePage):
    def is_contents_title_displayed(self) -> bool:
        locator = AOS_ContentshomeLocators_AllAges.CONTENTS_TITLE if self.platform == "aos" \
                else IOS_ContentshomeLocators_AllAges.CONTENTS_TITLE
        return self.is_displayed(locator)
    
    def click_episode_tab(self):
        if self.platform == "aos":
            self.click(AOS_ContentshomeLocators_AllAges.CONTENTS_EPISODE_TAB)
        else:
            self.click(IOS_ContentshomeLocators_AllAges.CONTENTS_EPISODE_TAB)

    def is_episode_tab_entered(self) -> bool:
        locator = AOS_ContentshomeLocators_AllAges.CONTENTS_EPISODE_SORT if self.platform == "aos" \
                else IOS_ContentshomeLocators_AllAges.CONTENTS_EPISODE_SORT
        return self.is_displayed(locator)

    def click_episode_sort(self):
        if self.platform == "aos":
            self.click(AOS_ContentshomeLocators_AllAges.CONTENTS_EPISODE_SORT)
        else:
            self.click_by_visible(IOS_ContentshomeLocators_AllAges.CONTENTS_EPISODE_SORT)

    def is_thumbnail_changed(self) -> bool:
        if self.platform == "aos":
            desc1 = self.get_thumbnail_content_desc(AOS_ContentshomeLocators_AllAges.CONTENTS_THUMBNAIL_FIRST)
            desc2 = self.get_thumbnail_content_desc(AOS_ContentshomeLocators_AllAges.CONTENTS_THUMBNAIL_SECOND)
        else:
            desc1 = self.get_thumbnail_content_desc(IOS_ContentshomeLocators_AllAges.CONTENTS_THUMBNAIL_FIRST)
            desc2 = self.get_thumbnail_content_desc(IOS_ContentshomeLocators_AllAges.CONTENTS_THUMBNAIL_SECOND)
        print(f"\ndesc1: {desc1}")
        print(f"\ndesc2: {desc2}")
        return desc1 != desc2
    
    def is_episode_1st_displayed(self) -> bool:
        locator = AOS_ContentshomeLocators_AllAges.CONTENTS_EPISODE_FIRST if self.platform == "aos" \
                else IOS_ContentshomeLocators_AllAges.CONTENTS_EPISODE_FIRST
        return self.is_displayed(locator)
        
    def click_episode_download(self):
        if self.platform == "aos":
            self.click(AOS_ContentshomeLocators_AllAges.CONTENTS_EPISODE_DOWNLOAD)
        else:
            self.click(IOS_ContentshomeLocators_AllAges.CONTENTS_EPISODE_DOWNLOAD)

    def is_paypopup_displayed(self) -> bool:
        locator = AOS_ContentshomeLocators_AllAges.PAY_CASH_BTN if self.platform == "aos" \
                else IOS_ContentshomeLocators_AllAges.PAY_CASH_BTN
        return self.is_displayed(locator)
    
    def click_pay_cash(self):
        if self.platform == "aos":
            self.click(AOS_ContentshomeLocators_AllAges.PAY_CASH_BTN)
        else:
            self.click(IOS_ContentshomeLocators_AllAges.PAY_CASH_BTN)

    def click_pay_rent_tab(self):
        if self.platform == "aos":
            self.click(AOS_ContentshomeLocators_AllAges.PAY_RENT_TAB)
        else:
            self.click(IOS_ContentshomeLocators_AllAges.PAY_RENT_TAB)

    def click_pay_rent_btn(self):
        if self.platform == "aos":
            self.click(AOS_ContentshomeLocators_AllAges.PAY_RENT_BTN)
        else:
            self.click(IOS_ContentshomeLocators_AllAges.PAY_RENT_BTN)

    def click_ownership_label_if_displayed(self):
        if self.platform == "aos":
            if self.is_present(AOS_ContentshomeLocators_AllAges.OWNERSHIP_LABEL):
                self.click(AOS_ContentshomeLocators_AllAges.CONTENTS_EPISODE_ITEM)
        else:
            if self.is_present(IOS_ContentshomeLocators_AllAges.OWNERSHIP_LABEL):
                self.click(IOS_ContentshomeLocators_AllAges.CONTENTS_EPISODE_ITEM)
