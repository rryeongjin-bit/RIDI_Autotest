from pages.base_page import *
from pages.locators import *


class LoginPage(BasePage):
    def click_login_btn(self):
        self.click(LoginLocators.LOGIN_BTN)

    def input_id(self, value: str):
        self.send_keys(LoginLocators.ID_INPUT, value)

    def input_pw(self, value: str):
        self.send_keys(LoginLocators.PW_INPUT, value)

    def click_login(self):
        self.click(LoginLocators.LOGIN_BUTTON)

    def login(self, id: str, pw: str):
        self.input_id(id)
        self.input_pw(pw)
        self.click_login()

class Replacedevicelist(BasePage):
    def click_replace_toggle(self):
        self.click(ReplacedeviceLocators.REPLACEDEVICE_TOGGLE_FIRST)

    def click_replace_btn(self):
        self.click(ReplacedeviceLocators.REPLACEDEVICE_BTN)
