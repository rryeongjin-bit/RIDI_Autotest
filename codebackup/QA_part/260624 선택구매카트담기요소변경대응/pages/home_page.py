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