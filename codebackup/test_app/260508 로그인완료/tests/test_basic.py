import pytest
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

    def test_launchapp(self):
        if self.platform == "aos":
            if self.alert.is_displayed(CommonLocators.ALERT_ALLOW):
                # 알림허용, 브레이즈팝업
                self.alert.click_noti_alert()
                self.alert.click_braze_alert()
                self.alert.switch_to_webview()

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

    def test_login(self):
        self.page.open_deeplink(DeepLinks.MYRIDI)

        # 로그인
        self.page.click_login_btn()
        self.page.switch_to_webview()
        self.page.login(
            id=self.account["id"],
            pw=self.account["pw"]
        )
        self.page.switch_to_native()

        # 기기 교체 화면
        if self.replace.is_replace_device_displayed():
            self.replace.click_replace_toggle()
            self.replace.click_replace_btn()

        assert self.page.is_login_success(), \
            "❌ 로그인 실패"