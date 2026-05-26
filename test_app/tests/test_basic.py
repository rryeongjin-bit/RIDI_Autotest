import pytest
import time
from pages.base_page import *
from pages.home_page import *
from pages.login_page import *
from pages.viewer_page import *
from pages.cart_page import *
from pages.checkout_page import *
from pages.signup_page import *
from pages.my_page import *
from data.test_data import *
from utils.helpers import *
from utils.gmail_helpers import *
from utils.google_auth import *

class TestLaunchApp:
    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver   = driver
        self.mainhome = MainhomePage(driver, platform)
        self.alert    = Alertnotification(driver, platform)
        self.platform = platform

    def test_App_Checklist_001_앱실행(self, request):
        if request.config.getoption("--reset") == "skip":
            pytest.skip("앱 초기화 없이 실행 중 - 스킵")

        if self.alert.is_noti_displayed():
            self.alert.click_noti_alert()
        else:
            logging.info("[SKIP] 알림 권한 팝업 미노출")

        time.sleep(3)
        self.alert.close_braze_if_present() 

        assert self.mainhome.is_genrehome_displayed(), \
            "❌ 앱실행 및 장르홈 진입 실패"

class TestLogoutIfNeeded:
    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver   = driver
        self.platform = platform
        self.page     = LoginPage(driver, platform)
        self.myridi    = MyridiPage(driver, platform)

    def test_logout_if_logged_in(self, request):
        if request.config.getoption("--reset") == "skip":
            pytest.skip("단독 실행 - 스킵")

        self.page.open_deeplink(DeepLinks.MYRIDI)
        assert self.myridi.is_mypage_entered(), "❌ 마이리디 화면 진입 실패"

        if not self.page.is_login_success():
            print("[SKIP] 로그아웃 상태 - 로그아웃 불필요")
            return

        self.page.click_logout()
        assert self.page.confirm_logout(), "❌ 로그아웃 확인 팝업 미노출"
        self.page.click_confirm_logout()
        assert self.page.is_login_page_displayed(), "❌ 로그아웃 실패"

class TestSignUp:
    sign_up_id         = None
    sign_up_pw         = None
    sign_up_email      = None
    signup_start_time  = None  

    @pytest.fixture(autouse=True)
    def setup(self, driver, platform, udid):
        self.driver   = driver
        self.platform = platform
        self.page     = SignUpPage(driver, platform, udid)
        self.alert    = Alertnotification(driver, platform)
        self.myridi    = MyridiPage(driver, platform)

    def test_App_Checklist_070_회원가입(self):
        self.page.open_deeplink(DeepLinks.LOGIN)
        self.page.click_join_btn()
        assert self.page.is_signup_title_displayed(), "❌ 회원가입 화면 진입 실패"

    def test_signup_form(self):
        TestSignUp.signup_start_time = int(time.time())
        timestamp = datetime.now().strftime("%y%m%d%H%M%S")
        user_id   = f"qa{timestamp}"
        email     = f"qa.part.test+{timestamp}@ridi.com"
        password  = SignUpData.SIGNUP_PASSWORD

        TestSignUp.sign_up_id    = user_id
        TestSignUp.sign_up_pw    = password
        TestSignUp.sign_up_email = email

        self.page.fill_signup_form(user_id, password, email, SignUpData.SIGNUP_NAME)
        self.page.click_agree_checkboxes()  
        self.page.click_signup_btn()

        assert self.page.is_signup_verify_displayed(), "❌ 회원가입 폼 제출 실패"

    def test_email_verify(self):
        url = None
        for i in range(12):
            try:
                url = get_latest_verification_url(
                    after_timestamp=TestSignUp.signup_start_time - 60,
                    sign_up_email=TestSignUp.sign_up_email
                )
            except TokenRefreshFailedError as e:
                pytest.fail(f"❌ Gmail 토큰 오류: {e}")
            if url:
                break
            print(f"[email_verify] 메일 대기 중... ({(i+1)*5}초 경과)")
            time.sleep(5)

        assert url, "❌ 인증 메일 수신 실패 (60초 초과)"
        print(f"[email_verify] 인증 URL: {url}")

        self.page.open_url_in_browser_pc(url)
        time.sleep(10)

        self.page.switch_to_native()
        self.page.wait_for_native()
        assert self.page.is_emailverify_complete_displayed(), "❌ 이메일 인증완료 및 회원가입완료 화면 진입 실패"

    def test_signup_confirm(self):
        self.page.switch_to_webview()
        self.page.wait_for_webview()
        self.page.click_confirm_btn()
        self.page.switch_to_native()
        self.page.wait_for_native()
        time.sleep(3)
    
        if self.myridi.is_mypage_entered():
            assert self.myridi.is_mypage_entered(), "❌ 회원가입 완료 후 마이홈 진입 실패"
        else:
            self.alert.close_braze_if_present()
            assert self.page.is_signup_complete_displayed(), "❌ 회원가입 완료 후 장르홈 진입 실패"
        
class TestMyinfo:
    current_user_id = None

    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver   = driver
        self.platform = platform
        self.page     = MyInfoPage(driver, platform)
        self.myridi    = MyridiPage(driver, platform)

    def test_myinfo_enter(self):
        self.page.open_deeplink(DeepLinks.MYRIDI)
        assert self.myridi.is_mypage_entered(), "❌ 마이리디 화면 진입 실패"

        self.page.click_my_info()
        assert self.page.is_recheck_pw_title_displayed(), "❌ 비밀번호 재확인 화면 진입 실패"

    def test_myinfo_recheck_pw(self):
        self.page.input_recheck_pw(SignUpData.SIGNUP_PASSWORD)
        self.page.click_recheck_pw_ok()
        assert self.page.is_my_info_manage_title_displayed(), "❌ 내 정보 관리 화면 진입 실패"
    
    def test_myinfo_back(self):
        TestMyinfo.current_user_id = self.page.get_current_user_id()

        if self.platform == "ios":
            self.page.click_back_to_myridi()
            assert self.page.is_my_title_displayed(), "❌ MY 화면 복귀 실패"
        else:
            pytest.skip("aos - 해당 없음")

class TestWithdraw:
    current_user_id = None 

    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver   = driver
        self.platform = platform
        self.page     = WithdrawPage(driver, platform)
        self.myinfo   = MyInfoPage(driver, platform)
        self.myridi    = MyridiPage(driver, platform)
        self.alert    = Alertnotification(driver, platform)

    def test_withdraw_enter(self):
        self.page.open_deeplink(DeepLinks.MYRIDI)
        assert self.myridi.is_mypage_entered(), "❌ 마이리디 화면 진입 실패"

        if self.platform == "aos":
            self.myinfo.click_my_info()
            self.myinfo.input_recheck_pw(SignUpData.SIGNUP_PASSWORD)
            self.myinfo.click_recheck_pw_ok()
            assert self.myinfo.is_my_info_manage_title_displayed(), "❌ 내 정보 관리 화면 진입 실패"
       
            TestWithdraw.current_user_id = TestSignUp.sign_up_id or TestMyinfo.current_user_id or self.myinfo.get_current_user_id()
            self.myinfo.click_withdraw_account()
            assert self.page.is_withdraw_title_displayed(), "❌ 회원탈퇴 화면 진입 실패"
        else:
            if TestMyinfo.current_user_id:
                TestWithdraw.current_user_id = TestMyinfo.current_user_id
                self.page.click_settings()
            else:
                self.myinfo.click_my_info()
                self.myinfo.input_recheck_pw(SignUpData.SIGNUP_PASSWORD)
                self.myinfo.click_recheck_pw_ok()
                assert self.myinfo.is_my_info_manage_title_displayed(), "❌ 내 정보 관리 화면 진입 실패"
                TestWithdraw.current_user_id = self.myinfo.get_current_user_id()
                self.myinfo.click_back_to_myridi()
                self.page.click_settings()

            assert self.page.is_settings_title_displayed(), "❌ 설정 화면 진입 실패"
            self.page.scroll_to_appinfo()
            self.page.click_menu_withdraw_account()
            assert self.page.is_withdraw_title_displayed(), "❌ 회원탈퇴 화면 진입 실패"

    def test_withdraw_process(self):
        self.page.scroll_to_agree_checkbox()
        self.page.click_reason_checkbox()
        
        if self.platform == "aos":
            self.page.input_withdraw_pw(SignUpData.SIGNUP_PASSWORD)
        
        self.page.click_agree_checkbox()
        self.page.click_withdraw_btn()
        assert self.page.is_check_withdraw_popup_displayed(TestWithdraw.current_user_id), "❌ 회원탈퇴 확인 팝업 미노출"
        
    def test_withdraw_confirm(self):
        self.page.click_check_withdraw_ok()
        assert self.page.is_withdraw_complete_popup_displayed(), "❌ 회원탈퇴 완료 팝업 미노출"

        self.page.click_check_withdraw_ok()
        self.alert.close_braze_if_present() 
        assert self.page.is_genrehome_displayed(), "❌ 탈퇴 후 장르홈 이동 실패"

class TestLogin:
    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver     = driver
        self.platform   = platform
        self.page       = LoginPage(driver, platform)
        self.replace    = Replacedevicelist(driver, platform)
        self.account    = TestAccount.AOS if platform == "aos" else TestAccount.IOS
        self.alert      = Alertnotification(driver, platform)

    def test_App_Checklist_072_로그인(self, request):
        if request.config.getoption("--reset") == "skip" and request.config.getoption("--login") == "skip":
            pytest.skip("앱 초기화 없이 실행 중 - 스킵")

        self.page.open_deeplink(DeepLinks.MYRIDI)
        self.alert.close_braze_if_present() 
        self.page.click_login_btn()
        time.sleep(3)
        print("현재 컨텍스트:", self.driver.contexts)
        self.page.switch_to_webview() 
        self.page.wait_for_webview()
        self.page.login(
            id=self.account["id"],
            pw=self.account["pw"]
        )
        self.page.switch_to_native() 
        self.page.wait_for_native()

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
        time.sleep(20)
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

        if self.page.is_watchorder_displayed():
            self.page.click_watchorder_sort()
            assert self.page.is_episode_any_displayed(), "❌ 보던순 정렬 실패"
        else:
            print("[SKIP] 보던순 미노출 - 회차순 유지")

    def test_App_Checklist_177_다운로드아이콘(self):
        try:
            self.page.click_episode_download_with_fallback()
        except Exception as e:
            pytest.fail(str(e))

        TestContentsHome_AllAges.episode_desc = self.page.get_first_download_episode_desc()
        self.page.click_episode_download()
        time.sleep(20)

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
                assert self.page.is_pay_renttab_displayed(), "❌ 캐시로 결제 버튼 선택 실패"
                self.page.click_pay_rent_btn()
                self.page.switch_to_native()
                self.page.wait_for_native()
                self.page.click_ownership_by_desc(TestContentsHome_AllAges.episode_desc) 

            except Exception as e:
                logging.warning(f"[결제 팝업] 웹뷰 전환 실패 - 스킵: {e}")
                self.page.switch_to_native()
                self.page.wait_for_native()

        time.sleep(60)
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

    def test_episode_sort(self):
        self.page.click_episode_tab()
        assert self.page.is_episode_tab_entered(), "❌ 회차 앵커탭 진입 실패"

        self.page.click_episode_sort()
        assert self.page.is_episode_1st_displayed(), "❌ 회차순 정렬 실패"
            
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
        time.sleep(20)
        assert self.page.is_adult_contents_title_displayed(), "❌ 성인작품홈 진입 실패"

    def test_App_Checklist_180_회차목록_정렬(self):
        self.page.click_episode_tab()
        assert self.page.is_episode_tab_entered(), "❌ 회차 앵커탭 진입 실패"

        self.page.click_episode_sort()
        assert self.page.is_episode_1st_displayed(), "❌ 회차순 정렬 실패"

        if self.page.is_watchorder_displayed():
            self.page.click_watchorder_sort()
            assert self.page.is_episode_any_displayed(), "❌ 보던순 정렬 실패"
        else:
            print("[SKIP] 보던순 미노출 - 회차순 유지")

    def test_App_Checklist_177_다운로드아이콘(self):
        assert self.page.is_download_btn_displayed(), "❌ 다운로드 버튼 미노출"
        
        TestContentsHome_Adult.episode_desc = self.page.get_first_download_episode_desc()
        self.page.click_episode_download()
        time.sleep(20)    

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
                assert self.page.is_pay_ownbtn_displayed(), "❌ 캐시로 결제 버튼 선택 실패"
                self.page.click_pay_buy_btn()
                self.page.switch_to_native()
                self.page.wait_for_native()
                self.page.click_ownership_by_desc(TestContentsHome_Adult.episode_desc) 

            except Exception as e:
                logging.warning(f"[결제 팝업] 웹뷰 전환 실패 - 스킵: {e}")
                self.page.switch_to_native()
                self.page.wait_for_native()

        time.sleep(60)
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
    
    def test_episode_sort(self):
        self.page.click_episode_tab()
        assert self.page.is_episode_tab_entered(), "❌ 회차 앵커탭 진입 실패"

        self.page.click_episode_sort()
        assert self.page.is_episode_1st_displayed(), "❌ 회차순 정렬 실패"

class TestSelectbuy_Cart:
    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver   = driver
        self.platform = platform
        self.page     = ContentshomePage(driver, platform)

    def test_contentshome(self):
        self.page.open_deeplink(DeepLinks.CONTENT_CART)
        time.sleep(20)
        assert self.page.is_cart_contents_title_displayed(), "❌ 작품홈 진입 실패"

    def test_selectbuy_cart(self):
        self.page.click_episode_tab()
        assert self.page.is_episode_tab_entered(), "❌ 회차 앵커탭 진입 실패"

        self.page.click_selectbuy_cart()
        self.page.close_select_drag_alert_if_visible()
        assert self.page.is_selectbuy_cart_entered(), "❌ 선택구매_카트담기 화면진입 실패"

    def test_App_Checklist_223_선택구매카트담기(self):
        if not self.page.is_selectbuy_cart_1st_rent_displayed():
            self.page.click_selectbuy_cart_rent_tab()
            time.sleep(3)

        rent_displayed = self.page.is_selectbuy_cart_1st_rent_displayed()
        assert rent_displayed, \
            "❌ 선택구매 및 카트담기 화면 대여탭 진입 실패"

        self.page.click_selectbuy_cart_own_tab()
        own_displayed = self.page.is_selectbuy_cart_1st_own_displayed()
        assert own_displayed, \
            "❌ 선택구매 및 카트담기 화면 소장탭 진입 실패"
    
    def test_App_Checklist_226_회차목록정렬(self):
        self.page.click_selectbuy_cart_sort_last()
        assert self.page.is_sort_latest_selected(), "❌ 최신순 정렬 실패"

    def test_App_Checklist_228_카트담기(self):
        self.page.click_selectbuy_cart_1st_episode()
        time.sleep(3)
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