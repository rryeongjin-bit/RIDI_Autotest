from pages.base_page import *
from pages.locators import *
from data.test_data import *

class Alertnotification(BasePage):
    def is_noti_displayed(self) -> bool:
        if self.platform == "ios":
            try:
                def check_alert(d):
                    try:
                        d.execute_script("mobile: alert", {"action": "getButtons"})
                        return True
                    except:
                        return False  

                WebDriverWait(self.driver, 10).until(check_alert)
                return True
            except:
                return False
        return self.is_displayed(CommonLocators.ALERT_ALLOW_AOS)

    def click_noti_alert(self):
        if self.platform == "ios":
            try:
                self.driver.execute_script("mobile: alert", {"action": "accept"})
                try:
                    self.driver.execute_script("mobile: alert", {"action": "accept"})
                except:
                    print("[SKIP] 트래킹 팝업 미노출")
            except:
                print("[SKIP] 알림 권한 팝업 미노출")
        else:
            self.click(CommonLocators.ALLOW_BTN_AOS)

    def is_braze_displayed(self) -> bool:
        locator = CommonLocators.BRAZEPOPUP_AOS if self.platform == "aos" \
                  else CommonLocators.BRAZEPOPUP_CLOSE_IOS
        return self.is_present(locator)

    def click_braze_alert(self):
        if self.platform == "aos":
            if self.is_present(CommonLocators.BRAZEPOPUP_CLOSE_AOS):
                self.click(CommonLocators.BRAZEPOPUP_CLOSE_AOS)
        else:
            if self.is_present(CommonLocators.BRAZEPOPUP_CLOSE_IOS):
                self.click(CommonLocators.BRAZEPOPUP_CLOSE_IOS)
    
    def close_braze_if_present(self) -> bool:
        if self.platform == "aos":
            if self.has_webview():
                self.switch_to_webview()
                self.wait_for_webview()
                if self.is_braze_displayed():
                    self.click_braze_alert()
                    self.switch_to_native()
                    self.wait_for_native()
                    return True
                self.switch_to_native()
                self.wait_for_native()
        else:
            try:
                WebDriverWait(self.driver, 10).until(
                    lambda d: self.is_braze_displayed()
                )
                self.click_braze_alert()
                return True
            except:
                pass

        print("[SKIP] Braze 팝업 미노출")
        return False

class MainhomePage(BasePage):
    def is_genrehome_displayed(self) -> bool:
        locator = AOS_GenrehomeLocators.WEBTOON_TAB if self.platform == "aos" \
                  else IOS_GenrehomeLocators.WEBTOON_NEW_QUICK
        return self.is_displayed(locator)
    
    def click_cart_icon(self):
        if self.platform == "aos":
            self.tap_coordinate(1006, 156)
        else:
            self.tap_coordinate(363, 69)

class ContentshomePage(BasePage):
    def is_all_contents_title_displayed(self) -> bool:
        locator = AOS_ContentshomeLocators.ALL_CONTENTS_TITLE if self.platform == "aos" \
                else IOS_ContentshomeLocators.ALL_CONTENTS_TITLE
        return self.is_displayed(locator)
    
    def is_adult_contents_title_displayed(self) -> bool:
        locator = AOS_ContentshomeLocators.ADULT_CONTENTS_TITLE if self.platform == "aos" \
            else IOS_ContentshomeLocators.ADULT_CONTENTS_TITLE
        return self.is_displayed(locator)

    def is_cart_contents_title_displayed(self) -> bool:
            locator = AOS_ContentshomeLocators.CART_CONTENTS_TITLE if self.platform == "aos" \
                    else IOS_ContentshomeLocators.CART_CONTENTS_TITLE
            return self.is_displayed(locator)

    def is_contents_title_displayed(self, locator: tuple, title: str) -> bool:
        el = self.find_element(locator)
        text = el.text if self.platform == "aos" else el.get_attribute("name")
        print(f"\n요소 텍스트: {text}")
        print(f"\n작품명: {title}")
        return title in text
    
    def is_selectbuy_cart_entered(self) -> bool:
        locator = AOS_ContentshomeLocators.SELECTBUY_CART_TITLE if self.platform == "aos" \
                else IOS_ContentshomeLocators.SELECTBUY_CART_TITLE
        return self.is_contents_title_displayed(locator, TestContent.CART["title"])

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
    
    def click_episode_all_btn(self):
        if self.platform == "aos":
            self.click(AOS_ContentshomeLocators.CONTENTS_EPISODE_ALL)
        else:
            self.click(IOS_ContentshomeLocators.CONTENTS_EPISODE_ALL)

    def click_episode_download_with_fallback(self) -> str:
        if not self.is_download_btn_displayed():
            print("[FALLBACK] 선택가능한 다운로드 버튼 미노출_총 회차목록 진입 후 재시도")
            self.click_episode_all_btn()
            time.sleep(2)
            if not self.is_download_btn_displayed():
                raise Exception("❌ 총 회차목록 내 선택가능한 다운로드 버튼 미노출")
            
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
    
    def get_first_download_episode_desc(self) -> str:
        if self.platform == "aos":
            el = self.find_element(AOS_ContentshomeLocators.EPISODE_TITLE_BEFORE_DOWNLOAD)
            return el.text
        else:
            el = self.find_element(IOS_ContentshomeLocators.EPISODE_TITLE_BEFORE_DOWNLOAD)
            return el.get_attribute("name")

    def click_ownership_by_desc(self, desc: str):
        if self.platform == "aos":
            locator = (AppiumBy.ANDROID_UIAUTOMATOR,
                f'new UiSelector().text("{desc}")')
            self.click(locator)
        else:
            locator = (AppiumBy.IOS_CLASS_CHAIN,
                f'**/XCUIElementTypeOther[`name == "{desc}"`]')
            self.click_by_visible(locator)

    def click_pay_cash_viewer(self):
        if self.platform == "aos":
            self.tap_coordinate(294, 2175)
        else:
            self.click(IOS_ContentshomeLocators.PAY_CASH_BTN)

    def click_pay_rent_viewer(self):
        if self.platform == "aos":
            self.tap_coordinate(280, 1254)
            self.tap_coordinate(531, 2051)
        else:
            self.click(IOS_ContentshomeLocators.PAY_RENT_TAB)
            self.click(IOS_ContentshomeLocators.PAY_RENT_BTN)

    def click_pay_buy_viewer(self):
        if self.platform == "aos":
            self.tap_coordinate(531, 2051)
        else:
            self.click(IOS_ContentshomeLocators.PAY_OWN_BTN)

    def click_selectbuy_cart(self):
        if self.platform == "aos":
            self.click(AOS_ContentshomeLocators.SELECTBUY_CART_BTN)
        else:
            self.click(IOS_ContentshomeLocators.SELECTBUY_CART_BTN)
    
    def click_selectbuy_cart_rent_tab(self):
        if self.platform == "aos":
            self.click(AOS_ContentshomeLocators.SELECTBUY_CART_RENT_TAB)
        else:
            self.click(IOS_ContentshomeLocators.SELECTBUY_CART_RENT_TAB)
    
    def is_selectbuy_cart_1st_rent_displayed(self) -> bool:
        locator = AOS_ContentshomeLocators.SELECTBUY_CART_RENT_ITEM if self.platform == "aos" \
                else IOS_ContentshomeLocators.SELECTBUY_CART_RENT_ITEM
        return self.is_displayed(locator)
    
    def click_selectbuy_cart_own_tab(self):
        if self.platform == "aos":
            self.click(AOS_ContentshomeLocators.SELECTBUY_CART_OWN_TAB)
        else:
            self.click(IOS_ContentshomeLocators.SELECTBUY_CART_OWN_TAB)
    
    def click_selectbuy_cart_sort_episode(self):
        if self.platform == "aos":
            self.click(AOS_ContentshomeLocators.SELECTBUY_CART_SORT_EPISODE)
        else:
            self.click(IOS_ContentshomeLocators.SELECTBUY_CART_SORT_EPISODE)

    def click_selectbuy_cart_sort_last(self):
        if self.platform == "aos":
            self.click(AOS_ContentshomeLocators.SELECTBUY_CART_SORT_LAST)
        else:
            self.click(IOS_ContentshomeLocators.SELECTBUY_CART_SORT_LAST)
    
    def is_selectbuy_cart_1st_own_displayed(self) -> bool:
        locator = AOS_ContentshomeLocators.SELECTBUY_CART_OWN_ITEM if self.platform == "aos" \
                else IOS_ContentshomeLocators.SELECTBUY_CART_OWN_ITEM
        return self.is_displayed(locator)
    
    def is_selectbuy_cart_1st_last_displayed(self) -> bool:
        locator = AOS_ContentshomeLocators.SELECTBUY_CART_OWN_LAST_ITEM if self.platform == "aos" \
                else IOS_ContentshomeLocators.SELECTBUY_CART_OWN_LAST_ITEM
        return self.is_displayed(locator)

    def click_selectbuy_cart_1st_episode(self):
        if self.platform == "aos":
            self.click(AOS_ContentshomeLocators.SELECTBUY_CART_FIRST_TOGGLE)
        else:
            self.click(IOS_ContentshomeLocators.SELECTBUY_CART_OWN_LAST_ITEM)
    
    def click_cart_btn(self):
        if self.platform == "aos":
            self.click(AOS_ContentshomeLocators.CART_BTN)
        else:
            self.click(IOS_ContentshomeLocators.CART_BTN)

    def is_cart_toast_displayed(self) -> bool:
        locator = AOS_ContentshomeLocators.CART_TOAST if self.platform == "aos" \
                else IOS_ContentshomeLocators.CART_TOAST
        return self.is_present(locator, timeout=5)



