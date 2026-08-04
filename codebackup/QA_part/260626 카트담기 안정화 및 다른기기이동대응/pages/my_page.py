import re
from pages.base_page import *
from locators.myridi import *

class MyridiPage(BasePage):
    def is_mypage_entered(self) -> bool:
        locator = AOS_MyLocators.MY_TITLE if self.platform == "aos" \
                    else IOS_MyLocators.MY_TITLE
        return self.is_displayed(locator)
    
    def click_charge_cash(self):
        if self.platform == "aos":
            self.click(AOS_MyLocators.CHARGE_RIDI_CASH)
        else:
            self.click(IOS_MyLocators.CHARGE_RIDI_CASH)
    
    def is_chargepopup_entered(self, timeout=DEFAULT_TIMEOUT) -> bool:
        locator = AOS_MyLocators.CHARGE_RIDI_CASH_TITLE if self.platform == "aos" \
                    else IOS_MyLocators.CHARGE_RIDI_CASH_TITLE
        return self.is_displayed(locator, timeout)
    
    def is_ridi_cash_displayed(self) -> bool:
        if self.platform == "aos":
            locator = AOS_MyLocators.MY_RIDI_CASH
        else:
            locator = IOS_MyLocators.MY_RIDI_CASH
        
        result = self.is_displayed(locator)
        self.log.info(f"[ridi_cash] 노출여부 : {'✅ PASS' if result else '❌ FAIL'}")
        return result
    
    def get_ridi_cash_amount(self) -> str:
        if self.platform == "aos":
            locator = AOS_MyLocators.MY_RIDI_CASH
            text = self.find_element(locator).text
        else:
            locator = IOS_MyLocators.MY_RIDI_CASH
            full_text = self.find_element(locator).text
            match = re.search(r'내 리디캐시\s+([\d,]+)\s+캐시', full_text)
            text = match.group(1) if match else ""

        self.log.info(f"[ridi_cash] 보유캐시 : '{text}'")
        return text

    def is_valid_ridi_cash(self) -> bool:
        text = self.get_ridi_cash_amount()
        pattern = r"^\d{1,3}(,\d{3})*$"
        result = bool(re.match(pattern, text))
        self.log.info(f"[ridi_cash] 보유캐시 {'✅ PASS' if result else '❌ FAIL'} - '{text}'")
        return result
    
    def is_chargehistory_displayed(self) -> bool:
        locator = AOS_MyLocators.CHARGE_HISTORY if self.platform == "aos" \
                else IOS_MyLocators.CHARGE_HISTORY
        return self.is_displayed(locator)
    
    def is_autocharge_manage_displayed(self) -> bool:
        locator = IOS_MyLocators.AUTOCHARGE_MANAGE_BTN
        return self.is_displayed(locator)
    
    def is_autocharge_banner_displayed(self) -> bool:
        locator = IOS_MyLocators.AUTOCHARGE_BANNER
        return self.is_element_present(locator)  

    def click_chargetier(self):
        self.click(AOS_MyLocators.CHARGE_TIER_FIRST)

    def is_sandbox_displayed(self) -> bool:
        return self.is_present(AOS_MyLocators.CHARGE_BTN, timeout=5)

    def click_charge_btn(self):
        self.click(AOS_MyLocators.CHARGE_BTN)

    def is_charge_complete_displayed(self) -> bool:
        return self.is_present(AOS_MyLocators.CHARGE_COMPLETE_POPUP, timeout=5)

    def click_charge_complete_btn(self):
        self.click(AOS_MyLocators.CHARGE_COMPLETE_CHECK)

class MyInfoPage(BasePage):
    def click_my_info(self):
        if self.platform == "aos":
            self.click(AOS_MyInfoLocators.MY_INFO)
        else:
            self.click(IOS_MyInfoLocators.MY_INFO)

    def is_recheck_pw_title_displayed(self) -> bool:
        if self.platform == "aos":
            result = self.is_displayed(AOS_MyInfoLocators.RECHECK_PW_TITLE, timeout=3)
        else:
            result = self.is_displayed(IOS_MyInfoLocators.RECHECK_PW_TITLE, timeout=3)
        if not result:
            self.log.info("[SKIP] 비밀번호 재확인 타이틀 미노출")
        return result

    def input_recheck_pw(self, password: str):
        if self.platform == "aos":
            if self.is_displayed(AOS_MyInfoLocators.RECHECK_PW_INPUT, timeout=DEFAULT_TIMEOUT):
                self.find_element(AOS_MyInfoLocators.RECHECK_PW_INPUT).send_keys(password)
            else:
                self.log.info("[SKIP] 비밀번호 재확인 입력 필드 미노출")
        else:
            if self.is_displayed(IOS_MyInfoLocators.RECHECK_PW_INPUT, timeout=DEFAULT_TIMEOUT):
                self.find_element(IOS_MyInfoLocators.RECHECK_PW_INPUT).send_keys(password)
            else:
                self.log.info("[SKIP] 비밀번호 재확인 입력 필드 미노출")

    def click_recheck_pw_ok(self):
        if self.platform == "aos":
            if self.is_displayed(AOS_MyInfoLocators.RECHECK_PW_OK_BTN, timeout=3):
                self.click(AOS_MyInfoLocators.RECHECK_PW_OK_BTN)
            else:
                self.log.info("[SKIP] 비밀번호 재확인 확인 버튼 미노출")
        else:
            if self.is_displayed(IOS_MyInfoLocators.RECHECK_PW_OK_BTN, timeout=3):
                self.click(IOS_MyInfoLocators.RECHECK_PW_OK_BTN)
            else:
                self.log.info("[SKIP] 비밀번호 재확인 확인 버튼 미노출")

    def is_my_info_manage_title_displayed(self) -> bool:
        if self.platform == "aos":
            return self.is_displayed(AOS_MyInfoLocators.MY_INFO_MANAGE_TITLE)
        else:
            return self.is_displayed(IOS_MyInfoLocators.MY_INFO_MANAGE_TITLE)
    
    def get_current_user_id(self) -> str:
        if self.platform == "aos":
            user_id = self.find_element(AOS_MyInfoLocators.CURRENT_USER_ID).text
        else:
            user_id = self.find_element(IOS_MyInfoLocators.CURRENT_USER_ID).get_attribute("name")
        logging.info(f"[current_user_id] 현재 계정 ID: {user_id}")
        return user_id

    # ios 전용
    def click_back_to_myridi(self):
        self.click(IOS_MyInfoLocators.BACK_TO_MYRIDI)

    def is_my_title_displayed(self) -> bool:
        if self.platform == "aos":
            return self.is_displayed(AOS_MyLocators.MY_TITLE)
        else:
            return self.is_displayed(IOS_MyLocators.MY_TITLE)

    # aos 전용
    def click_withdraw_account(self):
        self.click(AOS_MyInfoLocators.WITHDRAW_ACCOUNT)

    
