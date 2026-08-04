from pages.base_page import *
from locators.contentshome import *
from locators.genrehome import *
from locators.common import *
from data.test_data import *

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
        self.log.info(f"요소 텍스트: {text}")
        self.log.info(f"작품명: {title}")
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
        self.log.info(f"desc1: {desc1}")
        self.log.info(f"desc2: {desc2}")
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
            self.log.info("[FALLBACK] 선택가능한 다운로드 버튼 미노출_총 회차목록 진입 후 재시도")
            self.click_episode_all_btn()
            time.sleep(2)
            if not self.is_download_btn_displayed():
                raise Exception("❌ 총 회차목록 내 선택가능한 다운로드 버튼 미노출")
            return True  
        return False  
            
    def is_paypopup_displayed(self) -> bool:
        locator = AOS_ContentshomeLocators.PAY_CASH_BTN if self.platform == "aos" \
                else IOS_ContentshomeLocators.PAY_CASH_BTN
        try:
            return self.is_displayed(locator)
        except Exception as e:
            self.log.warning(f"[is_paypopup_displayed] 예외 발생: {e}")
            self.switch_to_native()
            self.wait_for_native()
            return False
    
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
            btn = self.driver.find_element(AppiumBy.XPATH, '(//android.view.ViewGroup[@resource-id="downloadButton"])[1]')
            self.log.info(f"downloadButton bounds: {btn.get_attribute('bounds')}")
            
            elements = self.driver.find_elements(
                AppiumBy.XPATH,
                '(//android.view.ViewGroup[@resource-id="downloadButton"])[1]/preceding-sibling::android.view.ViewGroup[@content-desc]'
            )
            for el in elements:
                self.log.info(f"sibling desc: [{el.get_attribute('content-desc')}]")
            
            el = self.find_element(AOS_ContentshomeLocators.EPISODE_TITLE_BEFORE_DOWNLOAD)
            desc = el.text
            self.log.info(f"[get_first_download_episode_desc] desc: [{desc}]")
            return desc
        else:
            el = self.find_element(IOS_ContentshomeLocators.EPISODE_TITLE_BEFORE_DOWNLOAD)
            return el.get_attribute("name")

    def click_ownership_by_desc(self, desc: str):
        if self.platform == "aos":
            self.log.info(f"[click_ownership_by_desc] 찾는 desc: [{desc}]")
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

    def ensure_entry_webview_if_needed(self):
        if self.platform != "aos":
            return

        try:
            contexts = self.driver.contexts

            if any("WEBVIEW" in c for c in contexts):
                self.switch_to_webview()
                
                if self.driver.current_url.startswith("file://"):
                    self.log.info("file:// URL → native 유지")
                    self.switch_to_native()
                    return
                    
                self.wait_for_webview()
                self.log.info("webview 전환 성공")
            else:
                self.log.info("webview 없음 → native 유지")

        except Exception as e:
            self.log.warning(f"[webview skip] {e}")
            self.switch_to_native()

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
    
    @staticmethod
    def _get_episode_num(desc: str) -> int:
        match = re.search(r'(\d+)권', desc)
        return int(match.group(1)) if match else 0
    
    def click_selectbuy_cart_1st_episode(self):
        if self.platform == "aos":
            max_scroll = 50

            for i in range(max_scroll):
                elements = self.find_elements(
                    AOS_ContentshomeLocators.SELECTBUY_CART_OWN_LAST_ITEM
                )

                single_items = [
                    el for el in elements
                    if not (el.get_attribute('content-desc') or '').endswith(', 소장')
                    and re.search(r'\d+권', el.get_attribute('content-desc') or '')
                ]

                if single_items:
                    target_el = max(
                        single_items,
                        key=lambda el: self._get_episode_num(
                            el.get_attribute('content-desc') or ''
                        )
                    )

                    self.log.info(
                        f"[click_selectbuy_cart_1st_episode] 선택 에피소드: "
                        f"{target_el.get_attribute('content-desc')}"
                    )

                    toggle = target_el.find_element(
                        AppiumBy.CLASS_NAME,
                        "android.widget.ImageView"
                    )
                    toggle.click()
                    return

                self.log.info(
                    f"[click_selectbuy_cart_1st_episode] 요소 없음, 스크롤 attempt={i}"
                )
                self.scroll_uiautomator()

            raise Exception(
                "[click_selectbuy_cart_1st_episode] 조건에 맞는 에피소드 없음"
            )

        else:
            elements = self.find_elements(
                IOS_ContentshomeLocators.SELECTBUY_CART_OWN_LAST_ITEM
            )

            single_items = [
                el for el in elements
                if el.get_attribute('name') is not None
                and len(re.findall(r'\d+권', el.get_attribute('name'))) == 1
                and not el.get_attribute('name').endswith('소장')
            ]

            if not single_items:
                raise Exception(
                    "[click_selectbuy_cart_1st_episode] 조건에 맞는 에피소드 없음"
                )

            target = max(
                single_items,
                key=lambda el: int(
                    re.search(
                        r'(\d+)권',
                        el.get_attribute('name')
                    ).group(1)
                )
            )

            self.log.info(
                f"[click_selectbuy_cart_1st_episode] 선택 에피소드: "
                f"{target.get_attribute('name')}"
            )

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
        if self.platform == "aos":
            locator = CommonLocators.SELECT_DRAG_ALERT_AOS
            close_locator = CommonLocators.SELECT_DRAG_ALERT_CLOSE_AOS
        else:
            locator = CommonLocators.SELECT_DRAG_ALERT_IOS
            close_locator = CommonLocators.SELECT_DRAG_ALERT_CLOSE_IOS

        if self.is_present(locator, timeout=2):
            self.click(close_locator)
    
    def click_episode_all_back(self):
        if self.platform == "ios":
            self.tap_coordinate(20, 69)
        else:
            self.tap_coordinate(52, 160)

    def has_ownership_label_before_download(self) -> bool:
        if self.platform == "aos":
            locator = (AppiumBy.XPATH,
                '(//android.view.ViewGroup[@resource-id="downloadButton"])[1]/../android.widget.TextView[@resource-id="ownershipLabel"]')
        else:
            locator = (AppiumBy.XPATH,
                '(//XCUIElementTypeOther[@name="downloadButton"])[1]/../XCUIElementTypeStaticText[@name="ownershipLabel"]')
        return self.is_present(locator, timeout=5)

    def wait_for_download_complete(self, timeout: int = 30) -> bool:
        try:
            if self.platform == "aos":
                locator = AOS_ContentshomeLocators.CONTENTS_EPISODE_DOWNLOAD
            else:
                locator = IOS_ContentshomeLocators.CONTENTS_EPISODE_DOWNLOAD
            WebDriverWait(self.driver, timeout).until_not(
                lambda d: self.is_present(locator, timeout=1)
            )
            self.log.info("[wait_for_download_complete] 다운로드 완료")
            return True
        except Exception as e:
            self.log.warning(f"[wait_for_download_complete] 타임아웃: {e}")
            return False