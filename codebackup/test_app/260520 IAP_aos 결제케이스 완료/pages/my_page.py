import re
from pages.base_page import *
from pages.locators import *

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
    
    def is_chargepopup_entered(self) -> bool:
        locator = AOS_MyLocators.CHARGE_RIDI_CASH_TITLE if self.platform == "aos" \
                    else IOS_MyLocators.CHARGE_RIDI_CASH_TITLE
        return self.is_displayed(locator)
    
    def is_ridi_cash_displayed(self) -> bool:
        if self.platform == "aos":
            locator = AOS_MyLocators.MY_RIDI_CASH
        else:
            locator = IOS_MyLocators.MY_RIDI_CASH
        
        result = self.is_displayed(locator)
        print(f"[ridi_cash] 노출여부 : {'✅ PASS' if result else '❌ FAIL'}")
        return result
    
    def get_ridi_cash_amount(self) -> str:
        if self.platform == "aos":
            locator = AOS_MyLocators.MY_RIDI_CASH
            text = self.find_element(locator).text
        else:
            locator = IOS_MyLocators.MY_RIDI_CASH
            full_text = self.find_element(locator).text
            # "내 리디캐시 3,080,310 캐시" → "3,080,310" 추출
            match = re.search(r'내 리디캐시\s+([\d,]+)\s+캐시', full_text)
            text = match.group(1) if match else ""

        print(f"[ridi_cash] 보유캐시 : '{text}'")
        return text

    def is_valid_ridi_cash(self) -> bool:
        text = self.get_ridi_cash_amount()
        pattern = r"^\d{1,3}(,\d{3})*$"
        result = bool(re.match(pattern, text))
        print(f"[ridi_cash] 보유캐시 {'✅ PASS' if result else '❌ FAIL'} - '{text}'")
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
        return self.is_element_present(locator)  # visible 여부 무관하게 존재 여부만 확인

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