import pytest
from config.settings import *
from tests.elements import *
from utils.helpers import *
from selenium.common.exceptions import TimeoutException

pytestmark = [
    pytest.mark.aos,
    pytest.mark.ios,
    pytest.mark.real,
    pytest.mark.emulator,
    pytest.mark.simulator,
    pytest.mark.chrome,
    pytest.mark.samsung,
    pytest.mark.safari,
]

class TestLogin:
    @pytest.mark.order(1)
    def test_login(self, logged_in): 
        assert "account/login" not in logged_in.current_url, \
            f"❌ 로그인 실패. 현재 URL: {logged_in.current_url}"
        
class TestContenthomeAll:
    """ 회차목록 > 4화 대여결제 및 뷰어진입 """
    @pytest.mark.order(2)
    def test_contenthome_all(self, logged_in): 
        driver = logged_in

        contents_home_all = URLs.CONTENT_HOME_ALL_AOS if is_android(driver) else URLs.CONTENT_HOME_ALL_IOS
        driver.get(contents_home_all)
        wait_for_page_load(driver)

        btn_rent = wait_for_element_clickable(driver, ContentHome.RENT_BTN)
        scroll_to_center_element(driver, btn_rent)
        wait_seconds(3)

        tap_element(driver, btn_rent)
        if is_chrome(driver):
            wait_for_element_visible(driver, PaymentPopup.FREE_VIEW_HEADER)
            payment_method_btn = wait_for_element_clickable(driver, PaymentPopup.PAYMENT_METHOD_BTN)
            tap_element(driver, payment_method_btn)

        wait_for_element_visible(driver, PaymentPopup.PAYMENT_HEADER)
        
        btn_payment = wait_for_element_clickable(driver, PaymentPopup.PAYMENT_BTN)
        tap_element(driver, btn_payment)

        viewer_contents_all = URLs.CONTENT_ALL_VIEW_AOS if is_android(driver) else URLs.CONTENT_ALL_VIEW_IOS
        wait_for_url_contains(driver, viewer_contents_all)
        wait_for_page_load(driver)

        assert viewer_contents_all in driver.current_url, \
            f"❌ 뷰어 진입 실패"

class TestViewerAll:
    """ 뷰어진입 및 다음화 결제 """
    @pytest.mark.order(3)
    def test_viewer_all(self, logged_in): 
        driver = logged_in

        viewer_contents_all = URLs.CONTENT_ALL_VIEW_AOS if is_android(driver) else URLs.CONTENT_ALL_VIEW_IOS
        driver.get(viewer_contents_all)
        wait_for_page_load(driver)

        btn_next= wait_for_element_clickable(driver, Viewer.NEXT_BTN)
        tap_element(driver, btn_next)
        wait_for_element_visible(driver, PaymentPopup.SELECT_PAYMENT_HEADER)
        
        btn_rent_nextcontent = wait_for_element_clickable(driver, PaymentPopup.RENT_NEXT_BTN)
        tap_element(driver, btn_rent_nextcontent)
        if is_chrome(driver):
            wait_for_element_visible(driver, PaymentPopup.FREE_VIEW_HEADER)
            next_payment_method_btn = wait_for_element_clickable(driver, PaymentPopup.NEXT_PAYMENT_METHOD_BTN)
            tap_element(driver, next_payment_method_btn)
        wait_for_element_visible(driver, PaymentPopup.PAYMENT_HEADER)
        
        btn_next_payment = wait_for_element_clickable(driver, PaymentPopup.NEXT_PAYMENT_BTN)
        tap_element(driver, btn_next_payment)
        
        viewer_nextcontents_all = URLs.CONTENT_ALL_NEXTVIEW_AOS if is_android(driver) else URLs.CONTENT_ALL_NEXTVIEW_IOS
        wait_for_url_contains(driver, viewer_nextcontents_all)
        wait_for_page_load(driver)

        assert viewer_nextcontents_all in driver.current_url, \
            f"❌ 다음화 뷰어 진입 실패"

class TestCart:
    """ 회차목록 > 카트담기 """
    @pytest.mark.order(4)
    def test_cart(self, logged_in):
        driver = logged_in

        driver.get(URLs.CONTENT_HOME)
        wait_for_page_load(driver)

        select_area = wait_for_element_visible(driver, ContentHome.SELECT_ALL)
        scroll_to_center_element(driver, select_area)
        wait_seconds(3)
        
        checkbox_first = wait_for_element(driver, ContentHome.FIRST_EPISODE_CHECKBOX)
        tap_element(driver, checkbox_first)

        btn_cart = wait_for_element_clickable(driver, ContentHome.CART_BTN)
        tap_element(driver, btn_cart)

        try:
            toast_msg = wait_for_element_visible(driver, ContentHome.TOAST_MSG_CART, timeout=5)
            assert toast_msg.is_displayed(), "❌ 카트담기 실패"
        except TimeoutException:
            assert False, "❌ 카트담기 토스트 메시지 미노출"
        
class TestCartPyament:
    @pytest.mark.order(5)
    def test_cartpage(self, logged_in):
        driver = logged_in
        
        driver.get(URLs.CART)
        wait_for_page_load(driver)

        # 소장 탭 활성화 여부 확인 후 분기 처리
        buy_tab = wait_for_element(driver, CartPage.BUY_TAB)

        if "selected" in buy_tab.get_attribute("class"):
            print("소장가능 탭 활성화 상태")
        else:
            # 활성화 안 된 경우 탭 클릭
            tap_element(driver, buy_tab)
            wait_for_element_visible(driver, CartPage.BUY_TAB_SELECTED)
            print("소장가능 탭 활성화 완료")

        # 최종 활성화 상태 assert
        assert "selected" in buy_tab.get_attribute("class"), \
            "소장가능 탭이 활성화되지 않았습니다."

        


