import pytest
from pages.login_page import *
from pages.locators import *
from data.test_data import *

pytestmark = [
    pytest.mark.aos,
    pytest.mark.ios,
    pytest.mark.real,
    pytest.mark.emulator,
    pytest.mark.simulator,
]


class TestLogin:
    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        """각 테스트 함수 실행 전 LoginPage 인스턴스 생성"""
        self.page     = LoginPage(driver, platform)
        self.platform = platform
        self.account  = TestAccount.AOS if platform == "aos" else TestAccount.IOS

    # -------------------------------------------------------
    # 로그인 성공
    # -------------------------------------------------------
    @pytest.mark.smoke
    def test_login_success(self):
        """정상 계정으로 로그인 성공 확인"""
        self.page.login(
            id=self.account["id"],
            pw=self.account["pw"]
        )
        assert self.page.is_displayed(HomeLocators.MAIN_BANNER), "로그인 실패 - 메인홈 배너 미노출"

    # -------------------------------------------------------
    # 로그인 실패 - 잘못된 계정
    # -------------------------------------------------------
    @pytest.mark.regression
    def test_login_fail_invalid_account(self):
        """잘못된 계정으로 로그인 실패 확인"""
        self.page.login(
            id="invalid_id@test.com",
            pw="invalid_pw"
        )
        assert self.page.is_error_message_displayed(), "오류 메시지 미노출"

    # -------------------------------------------------------
    # 로그인 실패 - 빈값
    # -------------------------------------------------------
    @pytest.mark.regression
    def test_login_fail_empty_id(self):
        """아이디 빈값으로 로그인 실패 확인"""
        self.page.login(
            id="",
            pw=self.account["pw"]
        )
        assert self.page.is_error_message_displayed(), "오류 메시지 미노출"

    @pytest.mark.regression
    def test_login_fail_empty_pw(self):
        """비밀번호 빈값으로 로그인 실패 확인"""
        self.page.login(
            id=self.account["id"],
            pw=""
        )
        assert self.page.is_error_message_displayed(), "오류 메시지 미노출"

    @pytest.mark.regression
    def test_login_fail_empty_all(self):
        """아이디/비밀번호 모두 빈값으로 로그인 실패 확인"""
        self.page.login(
            id="",
            pw=""
        )
        assert self.page.is_error_message_displayed(), "오류 메시지 미노출"