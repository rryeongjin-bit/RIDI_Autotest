from pages.base_page import *
from pages.locators import *


class LoginPage(BasePage):

    # 액션 메서드
    def input_id(self, value: str):
        """아이디 입력"""
        self.send_keys(LoginLocators.ID_INPUT, value)

    def input_pw(self, value: str):
        """비밀번호 입력"""
        self.send_keys(LoginLocators.PW_INPUT, value)

    def click_login(self):
        """로그인 버튼 클릭"""
        self.click(LoginLocators.LOGIN_BUTTON)

    def login(self, id: str, pw: str):
        """아이디/비밀번호 입력 후 로그인 버튼 클릭까지 한번에 처리"""
        self.input_id(id)
        self.input_pw(pw)
        self.click_login()

    # 검증 메서드
    def get_error_message(self) -> str:
        """오류 메시지 텍스트 반환"""
        return self.get_text(LoginLocators.ERROR_MESSAGE)

    def is_error_message_displayed(self) -> bool:
        """오류 메시지 노출 여부 반환"""
        return self.is_displayed(LoginLocators.ERROR_MESSAGE)