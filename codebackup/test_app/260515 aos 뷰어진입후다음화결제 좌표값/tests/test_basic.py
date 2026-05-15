import pytest
import time
from pages.base_page import *
from pages.home_page import *
from pages.login_page import *
from pages.viewer_page import *
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
        if self.alert.is_noti_displayed():
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

class TestContentsHome_AllAges:
    episode_desc  = ""
    before_count  = 0
    has_pay_popup = False

    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver   = driver
        self.platform = platform
        self.page     = ContentshomePage(driver, platform)
        self.viewer   = ViewerPage(driver, platform)

    def test_contents_all_ages(self):
        self.page.open_deeplink(DeepLinks.CONTENT_ALL_AGES)
        self.page.is_all_contents_title_displayed()
        assert self.page.is_all_contents_title_displayed(), "❌ 전연령작품홈 진입 실패"

    def test_App_Checklist_180_회차목록_정렬(self):
        self.page.click_episode_tab()
        assert self.page.is_episode_tab_entered(), "❌ 회차 앵커탭 진입 실패"

        self.page.click_episode_sort()
        assert self.page.is_episode_1st_displayed(), "❌ 회차순 정렬 실패"

    def test_App_Checklist_175_회차썸네일_확인(self):
        result = self.page.is_all_thumbnail_changed()
        print(f"\n썸네일 변경 여부: {result}")
        assert result, "❌ 회차별 썸네일 확인필요"

    def test_App_Checklist_177_다운로드아이콘(self):
        assert self.page.is_download_btn_displayed(), "❌ 다운로드 버튼 미노출"
        
        TestContentsHome_AllAges.episode_desc = self.page.get_first_download_episode_desc()
        self.page.click_episode_download()
        time.sleep(3)     

        TestContentsHome_AllAges.has_pay_popup = self.page.has_webview()
        print(f"\nhas_webview 결과: {TestContentsHome_AllAges.has_pay_popup}")
        print(f"\ncontexts: {self.driver.contexts}")

    def test_App_Checklist_423_회차구매_뷰어진입(self):
        if TestContentsHome_AllAges.has_pay_popup:  
            try:
                self.page.switch_to_webview()
                self.page.wait_for_webview()
                assert self.page.is_paypopup_displayed(), "❌ 결제 팝업 미노출"

                self.page.click_pay_cash()
                self.page.click_pay_rent_btn()
                self.page.switch_to_native()
                self.page.wait_for_native()
                self.page.click_ownership_by_desc(TestContentsHome_AllAges.episode_desc) 

            except Exception as e:
                logging.warning(f"[결제 팝업] 웹뷰 전환 실패 - 스킵: {e}")
                self.page.switch_to_native()
                self.page.wait_for_native()

        time.sleep(3)
        self.viewer.click_all_viewer()
        assert self.viewer.is_adult_viewer_top_title(TestContent.ALL_AGES["title"]), "❌ 뷰어 진입 실패"

    def test_App_Checklist_294_다음화결제(self):
        first_title = self.viewer.get_all_viewer_title()
        print(f"\n첫 번째 타이틀: {first_title}")
        self.viewer.is_next_episode_displayed()

        if self.page.has_webview():
            try:
                self.page.switch_to_webview(timeout=5)
                self.page.wait_for_webview()
                assert self.page.is_paypopup_displayed(), "❌ 결제 팝업 미노출"

                self.page.click_pay_cash()
                self.page.click_pay_rent_tab()
                self.page.click_pay_rent_btn()
                self.page.switch_to_native()
                self.page.wait_for_native()
                self.page.click_rent_ownership_displayed()
            except Exception as e:
                logging.warning(f"[결제 팝업] 웹뷰 전환 실패 - 스킵: {e}")
                self.page.switch_to_native()
                self.page.wait_for_native()

        time.sleep(2)
        self.viewer.click_all_viewer()
        second_title = self.viewer.get_all_viewer_title()
        print(f"\n두 번째 타이틀: {second_title}")

        assert first_title != second_title, \
            f"❌ 다음화 이동 실패"
        
class TestContentsHome_Adult:
    episode_desc  = ""
    before_count  = 0
    has_pay_popup = False

    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver   = driver
        self.platform = platform
        self.page     = ContentshomePage(driver, platform)
        self.viewer   = ViewerPage(driver, platform)
      
    def test_contents_adult(self):
        self.page.open_deeplink(DeepLinks.CONTENT_ADULT)
        assert self.page.is_adult_contents_title_displayed(), "❌ 성인작품홈 진입 실패"

    def test_App_Checklist_180_회차목록_정렬(self):
        self.page.click_episode_tab()
        assert self.page.is_episode_tab_entered(), "❌ 회차 앵커탭 진입 실패"

        self.page.click_episode_sort()
        assert self.page.is_episode_1st_displayed(), "❌ 회차순 정렬 실패"

    def test_App_Checklist_177_다운로드아이콘(self):
        assert self.page.is_download_btn_displayed(), "❌ 다운로드 버튼 미노출"
        
        TestContentsHome_Adult.episode_desc = self.page.get_first_download_episode_desc()
        self.page.click_episode_download()
        time.sleep(3)     

        TestContentsHome_Adult.has_pay_popup = self.page.has_webview()
        print(f"\nhas_webview 결과: {TestContentsHome_Adult.has_pay_popup}")
        print(f"\ncontexts: {self.driver.contexts}")

    def test_App_Checklist_423_회차구매_뷰어진입(self):
        if TestContentsHome_Adult.has_pay_popup:  
            try:
                self.page.switch_to_webview()
                self.page.wait_for_webview()
                assert self.page.is_paypopup_displayed(), "❌ 결제 팝업 미노출"

                self.page.click_pay_cash()
                self.page.click_pay_buy_btn()
                self.page.switch_to_native()
                self.page.wait_for_native()
                self.page.click_ownership_by_desc(TestContentsHome_Adult.episode_desc) 

            except Exception as e:
                logging.warning(f"[결제 팝업] 웹뷰 전환 실패 - 스킵: {e}")
                self.page.switch_to_native()
                self.page.wait_for_native()

        time.sleep(3)
        self.viewer.click_adult_viewer()
        assert self.viewer.is_adult_viewer_top_title(TestContent.ADULT["title"]), "❌ 뷰어 진입 실패"

    def test_App_Checklist_294_다음화결제(self):
        first_title = self.viewer.get_adult_viewer_title()
        print(f"\n첫 번째 타이틀: {first_title}")
        
        self.viewer.is_next_episode_displayed()
        TestContentsHome_Adult.has_pay_popup = self.page.has_webview()
        print(f"\nhas_webview 결과: {TestContentsHome_Adult.has_pay_popup}")
        print(f"\ncontexts: {self.driver.contexts}")

        if self.page.has_webview():
            try:
                self.page.switch_to_webview()
                self.page.wait_for_webview()
                self.page.click_pay_cash_viewer()
                self.page.click_pay_buy_viewer()
                self.page.switch_to_native()
                self.page.wait_for_native()

            except Exception as e:
                logging.warning(f"[결제 팝업] 웹뷰 전환 실패 - 스킵: {e}")
                self.page.switch_to_native()
                self.page.wait_for_native()

        time.sleep(3)
        self.viewer.click_adult_viewer()
        second_title = self.viewer.get_adult_viewer_title()
        print(f"\n두 번째 타이틀: {second_title}")

        assert first_title != second_title, \
            f"❌ 다음화 이동 실패"
        
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