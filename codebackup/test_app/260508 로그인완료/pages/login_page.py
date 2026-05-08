from pages.base_page import *
from pages.locators import *


class LoginPage(BasePage):
    def click_login_btn(self):
        if self.platform == "aos":
            self.click(AOS_LoginLocators.LOGIN_BTN)
        else:
            self.click(IOS_LoginLocators.LOGIN_BTN)
    
    def input_id(self, value: str):
        if self.platform == "aos":
            self.send_keys(AOS_LoginLocators.ID_INPUT, value)
        else:
            self.send_keys(IOS_LoginLocators.ID_INPUT,value)

    def input_pw(self, value: str):
        if self.platform == "aos":
            self.send_keys(AOS_LoginLocators.PW_INPUT, value)
        else:
            self.send_keys(IOS_LoginLocators.PW_INPUT,value)

    def click_login(self):
        if self.platform == "aos":
            self.click(AOS_LoginLocators.LOGIN_BUTTON)
        else:
            self.click(IOS_LoginLocators.LOGIN_BUTTON)

    def login(self, id: str, pw: str):
        self.input_id(id)
        self.input_pw(pw)
        self.click_login()
    
    def is_login_success(self) -> bool:
        """로그인 성공 여부 확인 - 플랫폼별 분기"""
        locator = AOS_LoginLocators.LOGOUT_BNT if self.platform == "aos" \
                  else IOS_LoginLocators.LOGOUT_BTN
        return self.is_displayed(locator)

class Replacedevicelist(BasePage):
    def is_replace_device_displayed(self) -> bool:
        """기기 교체 화면 노출 여부 확인 - 플랫폼별 분기"""
        locator = AOS_ReplacedeviceLocators.REPLACEDEVICE_LIST_TITLE if self.platform == "aos" \
                  else IOS_ReplacedeviceLocators.REPLACEDEVICE_LIST_TITLE
        return self.is_present(locator)
    
    def click_replace_toggle(self):
        if self.platform == "aos":
            self.click(AOS_ReplacedeviceLocators.REPLACEDEVICE_TOGGLE_FIRST)
       
    def click_replace_btn(self):
        if self.platform == "aos":
            self.click(AOS_ReplacedeviceLocators.REPLACEDEVICE_BTN)
        else:
            self.click(IOS_ReplacedeviceLocators.REPLACEDEVICE_BTN)
