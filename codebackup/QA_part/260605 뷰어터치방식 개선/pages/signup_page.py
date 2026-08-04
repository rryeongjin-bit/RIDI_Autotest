import time
import webbrowser
from datetime import datetime
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from pages.base_page import BasePage
from data.test_data import *
from config.settings import *
from locators.myridi import *
from locators.signup import *
from locators.genrehome import *

class SignUpPage(BasePage):
    def __init__(self, driver, platform, udid=None):
        super().__init__(driver, platform)
        self.udid = udid

    def is_joinbtn_displayed(self):
            if self.platform == "aos":
                self.is_present(AOS_SignUpLocators.LOGIN_JOIN_BTN)
            else:
                self.is_present(IOS_SignUpLocators.LOGIN_JOIN_BTN)

    def click_join_btn(self):
        if self.platform == "aos":
            self.click(AOS_SignUpLocators.LOGIN_JOIN_BTN) 
        else:
            self.click(IOS_SignUpLocators.LOGIN_JOIN_BTN)

    def is_signup_title_displayed(self) -> bool:
        self.switch_to_native()
        self.wait_for_native()
        if self.platform == "aos":
            return self.is_displayed(AOS_SignUpLocators.SIGNUP_TITLE)
        else:
            return self.is_displayed(IOS_SignUpLocators.SIGNUP_TITLE)

    def fill_signup_form(self, user_id, password, email, name):
        if self.platform == "aos":
            self.switch_to_webview()
            self.wait_for_webview()
            self.wait_for_element_visible(AOS_SignUpLocators.INPUT_ID) 
            self.find_element(AOS_SignUpLocators.INPUT_ID).send_keys(user_id)
            self.find_element(AOS_SignUpLocators.INPUT_PW).send_keys(password)
            self.find_element(AOS_SignUpLocators.INPUT_PW_CONFIRM).send_keys(password)
            self.find_element(AOS_SignUpLocators.INPUT_EMAIL).send_keys(email)
            self.find_element(AOS_SignUpLocators.INPUT_NAME).send_keys(name)
        else:
            self.find_element(IOS_SignUpLocators.INPUT_ID).send_keys(user_id)
            self.find_element(IOS_SignUpLocators.INPUT_PW).send_keys(password)
            self.find_element(IOS_SignUpLocators.INPUT_PW_CONFIRM).send_keys(password)
            self.find_element(IOS_SignUpLocators.INPUT_EMAIL).send_keys(email)
            self.find_element(IOS_SignUpLocators.INPUT_NAME).send_keys(name)

    def click_agree_checkboxes(self):
        if self.platform == "aos":
            self.click(AOS_SignUpLocators.AGREE_FIRST)
            if self.is_displayed(AOS_SignUpLocators.AGREE_CHECK):
                raise Exception("❌ 약관 동의 체크 실패")
        else:
            self.click(IOS_SignUpLocators.AGREE_FIRST)
            if self.is_displayed(IOS_SignUpLocators.AGREE_CHECK):
                raise Exception("❌ 약관 동의 체크 실패")
            

    def click_signup_btn(self):
        if self.platform == "aos":
            self.click(AOS_SignUpLocators.SIGNUP_BTN)
        else:
            self.click(IOS_SignUpLocators.SIGNUP_BTN)

    def is_signup_verify_displayed(self) -> bool:
        if self.platform == "aos":
            return self.is_displayed(AOS_SignUpLocators.SIGNUP_VERIFY)
        else:
            return self.is_displayed(IOS_SignUpLocators.SIGNUP_VERIFY)

    def open_url_in_browser_pc(self, url: str):
        webbrowser.open(url)
        self.log.info(f"[open_url_pc] PC 크롬에서 URL 열기: {url}")

    def is_emailverify_complete_displayed(self) -> bool:
        if self.platform == "aos":
            return self.is_displayed(AOS_SignUpLocators.SIGNUP_COMPLET)
        else:
            return self.is_displayed(IOS_SignUpLocators.SIGNUP_COMPLET)

    def click_confirm_btn(self):
        if self.platform == "aos":
            self.click(AOS_SignUpLocators.CONFIRM_BTN)
        else:
            self.click(IOS_SignUpLocators.CONFIRM_BTN)

    def is_signup_complete_displayed(self) -> bool:
        self.switch_to_native()
        self.wait_for_native()
        if self.platform == "aos":
            return self.is_displayed(AOS_GenrehomeLocators.COMIC_RECOMMEND_TAB)
        else:
            return self.is_displayed(IOS_GenrehomeLocators.COMIC_NEW_QUICK)

class WithdrawPage(BasePage):
    def is_withdraw_title_displayed(self) -> bool:
        if self.platform == "aos":
            return self.is_displayed(AOS_WithdrawAccountLocators.WITHDRAW_ACCOUNT_TITLE)
        else:
            return self.is_displayed(IOS_WithdrawAccountLocators.WITHDRAW_ACCOUNT_TITLE)

    def scroll_to_agree_checkbox(self):
        self.scroll_until_visible(
            AOS_WithdrawAccountLocators.AGREE_CHECKBOX if self.platform == "aos"
            else IOS_WithdrawAccountLocators.AGREE_CHECKBOX,
            direction="up"
        )

    def click_reason_checkbox(self):
        if self.platform == "aos":
            self.click(AOS_WithdrawAccountLocators.REASON_WITHDRAW_CHECKBOX_FIRST)
        else:
            self.click(IOS_WithdrawAccountLocators.REASON_WITHDRAW_CHECKBOX_FIRST)

    def click_agree_checkbox(self):
        if self.platform == "aos":
            self.click(AOS_WithdrawAccountLocators.AGREE_CHECKBOX)
        else:
            self.click(IOS_WithdrawAccountLocators.AGREE_CHECKBOX)

    def click_withdraw_btn(self):
        if self.platform == "aos":
            self.click(AOS_WithdrawAccountLocators.WITHDRAW_BTN)
        else:
            self.click(IOS_WithdrawAccountLocators.WITHDRAW_BTN)

    def is_check_withdraw_popup_displayed(self, user_id: str = None) -> bool:
        if self.platform == "aos":
            return self.is_displayed(AOS_WithdrawAccountLocators.CHECK_WITHDRAW_ACCOUNT_POPUP)
        else:
            locator = IOS_WithdrawAccountLocators.CHECK_WITHDRAW_ACCOUNT_POPUP(user_id)
            return self.is_displayed(locator)

    def click_check_withdraw_ok(self):
        if self.platform == "aos":
            self.click(AOS_WithdrawAccountLocators.CHECK_WITHDRAW_ACCOUNT_OK_BTN)
        else:
            self.click(IOS_WithdrawAccountLocators.CHECK_WITHDRAW_ACCOUNT_OK_BTN)

    def is_withdraw_complete_popup_displayed(self) -> bool:
        if self.platform == "aos":
            return self.is_displayed(AOS_WithdrawAccountLocators.WITHDRAW_ACCOUNT_COMPLETE_POPUP)
        else:
            return self.is_displayed(IOS_WithdrawAccountLocators.WITHDRAW_ACCOUNT_COMPLETE_POPUP)

    def is_genrehome_displayed(self) -> bool:
        self.switch_to_native()
        self.wait_for_native()
        if self.platform == "aos":
            return self.is_displayed(AOS_GenrehomeLocators.COMIC_RECOMMEND_TAB)
        else:
            return self.is_displayed(IOS_GenrehomeLocators.COMIC_NEW_QUICK)

    # ios 전용_설정진입 후 회원탈퇴
    def click_settings(self):
        self.click(IOS_SettingLocators.SETTINGS)

    def is_settings_title_displayed(self) -> bool:
        return self.is_displayed(IOS_SettingLocators.SETTINGS_TITLE)

    def scroll_to_appinfo(self):
        self.scroll_until_visible(
            IOS_SettingLocators.SECTION_APPINFO_TITLE,
            direction="up"
        )

    def click_menu_withdraw_account(self):
        self.click(IOS_SettingLocators.WITHDRAW_ACCOUNT)

    #aos 전용_회원탈퇴 비밀번호 재입력
    def input_withdraw_pw(self, password: str):
        self.find_element(AOS_WithdrawAccountLocators.PW_INPUT).send_keys(password)

