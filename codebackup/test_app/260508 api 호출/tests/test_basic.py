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
        #self.mainhome = MainhomePage(driver, platform)
        #self.page     = LoginPage(driver, platform)
        self.alert    = Alertnotification(driver, platform)
        #self.replace  = Replacedevicelist(driver, platform)
        self.platform = platform
        #self.account  = TestAccount.AOS if platform == "aos" else TestAccount.IOS

    def test_launchapp(self):
        if self.alert.is_displayed(CommonLocators.ALERT_ALLOW):
            # 알림허용/브레이즈팝업
            self.alert.click_noti_alert()
            self.alert.click_braze_alert()

    def test_enter_mainhome(self):
        api    = APIs.WEBTOON_MAIN_VIEW
        status = check_api_status(
            url=api["url"],
            params=api["params"][self.platform]
        )
        assert status == 200, f"❌ 앱실행 및 장르홈 진입 실패 | status: {status}"

      
        # # 로그인
        # self.page.click_login_btn()
        # self.page.login(
        #     id=self.account["id"],
        #     pw=self.account["pw"]
        # )

        # # 기기 교체 화면
        # if self.replace.is_present(ReplacedeviceLocators.REPLACEDEVICE_LIST_TITLE):
        #     self.replace.click_replace_toggle()
        #     self.replace.click_replace_btn()

        # assert self.page.is_displayed(LoginLocators.LOGOUT_BNT), \
        #     "❌ 로그인 실패"