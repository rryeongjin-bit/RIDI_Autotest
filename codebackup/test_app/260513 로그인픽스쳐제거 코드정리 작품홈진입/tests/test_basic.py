import pytest
import time
from pages.base_page import *
from pages.home_page import *
from pages.login_page import *
from data.test_data import *
from utils.helpers import *

pytestmark = [
    pytest.mark.aos,
    pytest.mark.ios,
    pytest.mark.real,
    pytest.mark.emulator,
    pytest.mark.simulator,
]

class TestLaunchApp:
    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver   = driver
        self.mainhome = MainhomePage(driver, platform)
        self.alert    = Alertnotification(driver, platform)
        self.platform = platform

    def test_App_Checklist_001_앱실행(self):
        if self.platform == "aos":
            if self.alert.is_displayed(CommonLocators.ALERT_ALLOW):
                self.alert.click_noti_alert()
            self.alert.close_braze_if_present()

        assert self.mainhome.is_genrehome_displayed(), \
        "❌ 앱실행 및 장르홈 진입 실패"

class TestLogin:
    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver     = driver
        self.platform   = platform
        self.page       = LoginPage(driver, platform)
        self.replace    = Replacedevicelist(driver, platform)
        self.account    = TestAccount.AOS if platform == "aos" else TestAccount.IOS

    def test_App_Checklist_072_로그인(self):
        self.page.open_deeplink(DeepLinks.MYRIDI)
        self.page.click_login_btn()
        self.page.switch_to_webview() 
        self.page.wait_for_webview()
        self.page.login(
            id=self.account["id"],
            pw=self.account["pw"]
        )
        self.page.switch_to_native() 
        self.page.wait_for_native()

        # 기기 대체 화면
        if self.replace.is_replace_device_displayed():
            self.replace.click_replace_toggle()
            self.replace.click_replace_btn()

        assert self.page.is_login_success(), \
            "❌ 로그인 실패"

class TestContentsHome:
    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver     = driver
        self.platform   = platform
        self.page       = ContentshomePage(driver, platform)

    def test_contents_all_ages(self):
        self.page.open_deeplink(DeepLinks.CONTENT_ALL_AGES)
        time.sleep(3)

        # 회차목록 결제시도
        self.page.click_episode_tab()
        self.page.click_episode_sort()
        self.page.click_4th_episode()

class TestLogout:
    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver     = driver
        self.platform   = platform
        self.page       = LoginPage(driver, platform)

    def test_confirm_logout(self):
        self.page.open_deeplink(DeepLinks.MYRIDI)
        self.page.is_login_success()
        self.page.click_logout()

        assert self.page.confirm_logout(), \
        "❌ 로그아웃 확인 팝업 미노출"

    def test_App_Checklist_072_로그아웃(self):
        self.page.confirm_logout()
        self.page.click_confirm_logout()

        assert self.page.is_login_page_displayed(), \
        "❌ 로그아웃 실패"