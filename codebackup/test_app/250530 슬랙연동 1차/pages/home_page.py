from pages.base_page import *
from locators.contentshome import *
from locators.genrehome import *
from locators.common import *
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
                logging.info("[click_noti_alert] 알림 권한 팝업 허용")
                try:
                    self.driver.execute_script("mobile: alert", {"action": "accept"})
                    logging.info("[click_noti_alert] 트래킹 팝업 허용")
                except:
                    logging.info("[SKIP] 트래킹 팝업 미노출")
            except:
                logging.info("[SKIP] 알림 권한 팝업 미노출")
        else:
            self.click(CommonLocators.ALLOW_BTN_AOS)
            logging.info("[click_noti_alert] 알림 권한 팝업 허용")

    def is_braze_displayed(self) -> bool:
        if self.platform == "aos":
            return self.is_present(CommonLocators.BRAZEPOPUP_CLOSE_AOS)
        else:
            return self.is_present(CommonLocators.BRAZEPOPUP_CLOSE_IOS)
        
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
                try:
                    self.switch_to_webview()
                    self.wait_for_webview()
                    if self.is_braze_displayed():
                        self.click_braze_alert()
                        logging.info("[close_braze_if_present] Braze 팝업 닫기 완료")
                        self.switch_to_native()
                        self.wait_for_native()
                        return True
                    self.switch_to_native()
                    self.wait_for_native()
                except Exception as e:
                    logging.info(f"[SKIP] 웹뷰 전환 실패 - 스킵: {e}")
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

        logging.info("[SKIP] Braze 팝업 미노출")
        return False

class MainhomePage(BasePage):
    def is_genrehome_displayed(self) -> bool:
        locator = AOS_GenrehomeLocators.WEBTOON_RECOMMEND_TAB if self.platform == "aos" \
                  else IOS_GenrehomeLocators.WEBTOON_NEW_QUICK
        return self.is_present(locator)
    
    def click_cart_icon(self):
        if self.platform == "aos":
            self.tap_coordinate(1006, 156)
        else:
            self.tap_coordinate(363, 69)

class ContentshomePage(BasePage):
    def is_all_contents_title_displayed(self) -> bool:
        locator = AOS_ContentshomeLocators.ALL_CONTENTS_TITLE if self.platform == "aos" \
                else IOS_ContentshomeLocators.ALL_CONTENTS_TITLE
        return self.is_present(locator)
    
    def is_adult_contents_title_displayed(self) -> bool:
        locator = AOS_ContentshomeLocators.ADULT_CONTENTS_TITLE if self.platform == "aos" \
            else IOS_ContentshomeLocators.ADULT_CONTENTS_TITLE
        return self.is_present(locator)

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
    
    def is_watchorder_displayed(self) -> bool:
        locator = AOS_ContentshomeLocators.CONTENTS_WATCHING_SORT if self.platform == "aos" \
                else IOS_ContentshomeLocators.CONTENTS_WATCHING_SORT
        return self.is_displayed(locator)

    def click_watchorder_sort(self):
        if self.platform == "aos":
            self.click(AOS_ContentshomeLocators.CONTENTS_WATCHING_SORT)
        else:
            self.click(IOS_ContentshomeLocators.CONTENTS_WATCHING_SORT)

    def is_episode_any_displayed(self) -> bool:
        locator = AOS_ContentshomeLocators.CONTENTS_EPISODE_ANY if self.platform == "aos" \
                else IOS_ContentshomeLocators.CONTENTS_EPISODE_ANY
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

    def click_episode_download_with_fallback(self) -> bool:
        if not self.is_download_btn_displayed():
            print("[FALLBACK] 선택가능한 다운로드 버튼 미노출_총 회차목록 진입 후 재시도")
            self.click_episode_all_btn()
            time.sleep(2)
            if not self.is_download_btn_displayed():
                raise Exception("❌ 총 회차목록 내 선택가능한 다운로드 버튼 미노출")
            return True  
        return False  
            
    def is_paypopup_displayed(self) -> bool:
        locator = AOS_ContentshomeLocators.PAY_CASH_BTN if self.platform == "aos" \
                else IOS_ContentshomeLocators.PAY_CASH_BTN
        return self.is_displayed(locator)
    
    def click_pay_cash(self):
        if self.platform == "aos":
            self.click(AOS_ContentshomeLocators.PAY_CASH_BTN)
        else:
            self.click(IOS_ContentshomeLocators.PAY_CASH_BTN)

    def is_pay_renttab_displayed(self) -> bool:
        locator = AOS_ContentshomeLocators.PAY_RENT_TAB if self.platform == "aos" \
                  else IOS_ContentshomeLocators.PAY_RENT_TAB
        return self.is_displayed(locator)

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
    
    def is_pay_ownbtn_displayed(self) -> bool:
        locator = AOS_ContentshomeLocators.PAY_OWN_BTN if self.platform == "aos" \
                  else IOS_ContentshomeLocators.PAY_OWN_BTN
        return self.is_displayed(locator)

    def click_pay_buy_btn(self):
        if self.platform == "aos":
            self.click(AOS_ContentshomeLocators.PAY_OWN_BTN)
        else:
            self.click(IOS_ContentshomeLocators.PAY_OWN_BTN)
    
    def get_first_download_episode_desc(self) -> str:
        if self.platform == "aos":
            # 디버깅용
            btn = self.driver.find_element(AppiumBy.XPATH, '(//android.view.ViewGroup[@resource-id="downloadButton"])[1]')
            print(f"downloadButton bounds: {btn.get_attribute('bounds')}")
            
            elements = self.driver.find_elements(
                AppiumBy.XPATH,
                '(//android.view.ViewGroup[@resource-id="downloadButton"])[1]/preceding-sibling::android.view.ViewGroup[@content-desc]'
            )
            for el in elements:
                print(f"sibling desc: [{el.get_attribute('content-desc')}]")
            
            el = self.find_element(AOS_ContentshomeLocators.EPISODE_TITLE_BEFORE_DOWNLOAD)
            desc = el.text
            print(f"[get_first_download_episode_desc] desc: [{desc}]")
            return desc
        else:
            el = self.find_element(IOS_ContentshomeLocators.EPISODE_TITLE_BEFORE_DOWNLOAD)
            return el.get_attribute("name")

    def click_ownership_by_desc(self, desc: str):
        if self.platform == "aos":
            print(f"[click_ownership_by_desc] 찾는 desc: [{desc}]")
            locator = (AppiumBy.ANDROID_UIAUTOMATOR,
                f'new UiSelector().text("{desc}")')
            self.click(locator)
        else:
            locator = (AppiumBy.IOS_CLASS_CHAIN,
                f'**/XCUIElementTypeOther[`name == "{desc}"`]')
            self.click_by_visible(locator)

    def click_pay_cash_viewer(self):
        if self.platform == "aos":
            self.tap_coordinate(244, 2108)
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
    
    def is_selectbuy_cart_1st_own_displayed(self) -> bool:
        locator = AOS_ContentshomeLocators.SELECTBUY_CART_OWN_ITEM if self.platform == "aos" \
                else IOS_ContentshomeLocators.SELECTBUY_CART_OWN_ITEM
        return self.is_displayed(locator)
    
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
        
    def is_sort_latest_selected(self) -> bool:
        if self.platform == "aos":
            el = self.find_element(AOS_ContentshomeLocators.SELECTBUY_CART_SORT_LAST)
            return el.get_attribute('enabled') == 'true'
        else:
            el = self.find_element(IOS_ContentshomeLocators.SELECTBUY_CART_SORT_LAST)
            return el.get_attribute('enabled') == 'false'

    def click_selectbuy_cart_1st_episode(self):
        if self.platform == "aos":
            elements = self.find_elements(AOS_ContentshomeLocators.SELECTBUY_CART_OWN_LAST_ITEM)
            single_items = [
                el for el in elements
                if not el.get_attribute('content-desc').endswith(', 소장')
            ]

            def get_episode_num(el):
                match = re.search(r'(\d+)권', el.get_attribute('content-desc'))
                return int(match.group(1)) if match else 0

            target = max(single_items, key=get_episode_num)
            target_desc = target.get_attribute('content-desc')
            self.log.info(f"[click_selectbuy_cart_1st_episode] 선택한 에피소드: {target_desc}")
            
            target_locator = (
                AppiumBy.XPATH,
                f'//android.view.ViewGroup[@content-desc="{target_desc}"]'
            )
            self.scroll_until_visible(target_locator, direction="up")
            target = self.find_element(target_locator)
            toggle = target.find_element(AppiumBy.CLASS_NAME, 'android.widget.ImageView')
            toggle.click()
        else:
            elements = self.find_elements(IOS_ContentshomeLocators.SELECTBUY_CART_OWN_LAST_ITEM)
            single_items = [
                el for el in elements
                if el.get_attribute('name') is not None
                and len(re.findall(r'\d+권', el.get_attribute('name'))) == 1
                and not el.get_attribute('name').endswith('소장')
            ]
            target = max(single_items, key=lambda el: int(re.search(r'(\d+)권', el.get_attribute('name')).group(1)))
            self.log.info(f"[click_selectbuy_cart_1st_episode] 선택 에피소드: {target.get_attribute('name')}")
            target.click()
                            
    def click_cart_btn(self):
        if self.platform == "aos":
            self.click(AOS_ContentshomeLocators.CART_BTN)
        else:
            self.click(IOS_ContentshomeLocators.CART_BTN)

    def is_cart_toast_displayed(self) -> bool:
        locator = AOS_ContentshomeLocators.CART_TOAST if self.platform == "aos" \
                else IOS_ContentshomeLocators.CART_TOAST
        return self.is_present(locator, timeout=5)

    def close_select_drag_alert_if_visible(self):
        if self.platform != "aos":
            return
        locator = CommonLocators.SELECT_DRAG_ALERT_AOS
        if self.is_present(locator, timeout=2):  
            self.click(CommonLocators.SELECT_DRAG_ALERT_CLOSE_AOS)
   
    def click_episode_all_back(self):
        if self.platform == "ios":
            self.tap_coordinate(20, 69)
        else:
            self.tap_coordinate(52, 160)