import pytest
import time
from pages.base_page import *
from pages.home_page import *
from pages.login_page import *
from pages.viewer_page import *
from pages.cart_page import *
from pages.checkout_page import *
from pages.my_page import *
from data.test_data import *
from utils.helpers import *

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
        else:
            print("[SKIP] 알림 권한 팝업 미노출")

        time.sleep(3)
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
        print("현재 컨텍스트:", self.driver.contexts)
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
        else:
            print("[SKIP] 기기 대체 화면 미노출")

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
        assert self.viewer.is_all_viewer_top_title(TestContent.ALL_AGES["title"]), "❌ 뷰어 진입 실패"

    def test_App_Checklist_388_다음화결제(self):
        first_title = self.viewer.get_all_viewer_title()
        print(f"\n첫 번째 타이틀: {first_title}")
        
        self.viewer.is_next_episode_displayed()
        TestContentsHome_AllAges.has_pay_popup = self.page.has_webview()
        print(f"\nhas_webview 결과: {TestContentsHome_AllAges.has_pay_popup}")
        print(f"\ncontexts: {self.driver.contexts}")

        if self.page.has_webview():
            try:
                self.page.switch_to_webview()
                self.page.wait_for_webview()
                self.page.click_pay_cash_viewer()
                self.page.click_pay_rent_viewer()
                self.page.switch_to_native()
                self.page.wait_for_native()

            except Exception as e:
                logging.warning(f"[결제 팝업] 웹뷰 전환 실패 - 스킵: {e}")
                self.page.switch_to_native()
                self.page.wait_for_native()

        time.sleep(3)
        self.viewer.click_all_viewer()
        second_title = self.viewer.get_all_viewer_title()
        print(f"\n두 번째 타이틀: {second_title}")

        assert first_title != second_title, \
            f"❌ 다음화 이동 실패"
    
    def test_App_Checklist_383_뷰어이탈(self):
        self.viewer.click_back_all()
        assert self.page.is_episode_tab_entered(), "❌ 뷰어이탈 및 작품홈 진입 실패" 
            
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

    def test_App_Checklist_181_회차구매_뷰어진입(self):
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
    
    def test_App_Checklist_288_뷰어이탈(self):
        self.viewer.click_back_adult()
        assert self.page.is_episode_tab_entered(), "❌ 뷰어이탈 및 작품홈 진입 실패" 

class TestSelectbuy_Cart:
    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver   = driver
        self.platform = platform
        self.page     = ContentshomePage(driver, platform)

    def test_contentshome(self):
        self.page.open_deeplink(DeepLinks.CONTENT_CART)
        assert self.page.is_cart_contents_title_displayed(), "❌ 작품홈 진입 실패"

    def test_selectbuy_cart(self):
        self.page.click_episode_tab()
        assert self.page.is_episode_tab_entered(), "❌ 회차 앵커탭 진입 실패"

        self.page.click_selectbuy_cart()
        assert self.page.is_selectbuy_cart_entered(), "❌ 선택구매_카트담기 화면진입 실패"

    def test_App_Checklist_223_선택구매카트담기(self):
        if not self.page.is_selectbuy_cart_1st_rent_displayed():
            self.page.click_selectbuy_cart_rent_tab()

        if not self.page.is_selectbuy_cart_1st_rent_displayed():
            self.page.click_selectbuy_cart_sort_episode()

        rent_displayed = self.page.is_selectbuy_cart_1st_rent_displayed()
        assert rent_displayed, \
            "❌ 선택구매 및 카트담기 화면 대여탭 진입 실패"

        self.page.click_selectbuy_cart_own_tab()

        if not self.page.is_selectbuy_cart_1st_own_displayed():
            self.page.click_selectbuy_cart_sort_episode()

        own_displayed = self.page.is_selectbuy_cart_1st_own_displayed()
        assert own_displayed, \
            "❌ 선택구매 및 카트담기 화면 소장탭 진입 실패"
    
    def test_App_Checklist_226_회차목록정렬(self):
        self.page.click_selectbuy_cart_sort_last()
        assert self.page.is_selectbuy_cart_1st_last_displayed(), "❌ 회차순 정렬 실패"

    def test_App_Checklist_228_카트담기(self):
        self.page.click_selectbuy_cart_1st_episode()
        self.page.click_cart_btn()
        assert self.page.is_cart_toast_displayed(), "❌ 카트 담기 토스트 미노출"

class TestCart:
    has_pay_popup = False
    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver   = driver
        self.platform = platform
        self.page     = CartPage(driver, platform)
        self.home     = MainhomePage(driver, platform)
        self.order    = CheckoutPage(driver,platform)
    
    def test_Genrehome(self):
        self.page.open_deeplink(DeepLinks.HOME)
        assert self.home.is_genrehome_displayed(), "❌ 앱실행 및 장르홈 진입 실패"

    def test_App_Checklist_095_카트진입(self):
        self.home.click_cart_icon()

        if TestCart.has_pay_popup:
            try:
                self.page.switch_to_webview()
                self.page.wait_for_webview()
                assert self.page.is_owntab_displayed(), "❌ 카트 화면 진입 실패"
            except Exception as e:
                logging.warning(f"[결제 팝업] 웹뷰 전환 실패 - 스킵: {e}")

    def test_cartpayment(self):
        if not self.page.is_owntab_displayed():
            self.page.click_owntab()

        self.page.click_checkbox_all()
        self.page.click_checkbox_first()
        self.page.click_own_pay()
        assert self.order.is_orderlist_section_displayed(), "❌ 주문결제 화면 진입 실패"

    def test_checkout_pay(self):
        if self.platform == "aos":
            self.page.switch_to_native()
            self.page.wait_for_native()

        self.order.scroll_to_payment_detail_section()
        self.order.click_payment_agree()
        self.order.click_payemnt_btn()

        assert self.order.is_payment_complete_displayed(), "❌ 결제완료 화면 진입 실패"

    def test_movehome(self):
        if self.platform == "aos":
            self.page.switch_to_webview()
            self.page.wait_for_webview()

        self.order.click_move_to_home()

        if self.platform == "aos":
            self.page.switch_to_native()
            self.page.wait_for_native()

        assert self.home.is_genrehome_displayed(), "❌ 장르홈 이동 실패"

class TestMyridi:
    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver     = driver
        self.platform   = platform
        self.page       = MyridiPage(driver, platform)
    
    def test_Myridipage(self):
        self.page.open_deeplink(DeepLinks.MYRIDI)
        assert self.page.is_mypage_entered(), "❌ 마이리디 화면 진입 실패"
    
    def test_entered_chargecash_popup(self):
        self.page.click_charge_cash()
        assert self.page.is_chargepopup_entered(), "❌ 리디캐시 충전화면 진입 실패"
    
    def test_chargecash_popup(self):
        assert self.page.is_valid_ridi_cash(), "❌ 보유캐시 확인필요"
        assert self.page.is_chargehistory_displayed(), "❌ 충전 내역 미노출"

    def test_autocharge_manage(self):
        if self.platform != "ios":
            pytest.skip("iOS 전용 테스트 - aos 미지원")
        assert self.page.is_autocharge_manage_displayed(), "❌ 자동충전 관리 버튼 미노출"

    def test_autocharge_banner(self):
        if self.platform != "ios":
            pytest.skip("iOS 전용 테스트 - aos 미지원")
        assert self.page.is_autocharge_banner_displayed(), "❌ 자동충전 배너 미노출"
    
    def test_App_Checklist_078_리디캐시충전(self):
        if self.platform != "aos":
            pytest.skip("iOS 인앱결제 Sandbox 자동화 불가 - aos 전용 테스트")

        self.page.click_chargetier()
        assert self.page.is_sandbox_displayed(), "❌ sandbox 노출 실패"

        self.page.click_charge_btn()
        time.sleep(3)
        assert self.page.is_charge_complete_displayed(), "❌ 리디캐시 충전 실패"

        self.page.click_charge_complete_btn()
        time.sleep(3)
        assert self.page.is_mypage_entered(), "❌ 리디캐시 충전 후 마이리디 화면 복귀 실패"
            
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