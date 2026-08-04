import pytest
import time
import logging
from pages.genrehome_page import *
from pages.home_page import *
from pages.login_page import *
from pages.my_page import *
from data.test_data import *
from utils.helpers import *


class TestLaunchApp:
    """ 앱 실행 """
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
    """ 이미 로그인된 상태일 경우 로그아웃 진행 """
    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver  = driver
        self.platform = platform
        self.page    = LoginPage(driver, platform)
        self.myridi  = MyridiPage(driver, platform)

    def test_logout_if_logged_in(self, request):
        if request.config.getoption("--reset") == "skip":
            pytest.skip("단독 실행 - 스킵")

        self.page.open_deeplink(DeepLinks.MYRIDI)
        assert self.myridi.is_mypage_entered(), "❌ 마이리디 화면 진입 실패"

        if not self.page.is_login_success():
            logging.info("[SKIP] 로그아웃 상태 - 로그아웃 불필요")
            return

        self.page.click_logout()
        assert self.page.confirm_logout(), "❌ 로그아웃 확인 팝업 미노출"
        self.page.click_confirm_logout()
        assert self.page.is_login_page_displayed(), "❌ 로그아웃 실패"

class TestLogin:
    """ 로그인 """
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
        time.sleep(10)
        self.page.click_login_btn()

        self.page.switch_to_webview_with_retry()
        logging.info(f"현재 컨텍스트: {self.driver.contexts}")

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
            logging.info("[SKIP] 기기 대체 화면 미노출")

        assert self.page.is_login_success(), \
            "❌ 로그인 실패"


class TestComicCategory:
    """만화 장르홈 우측 상단 햄버거(카테고리) 버튼 진입 및 상위/하위메뉴 순회검증"""
    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver   = driver
        self.platform = platform
        self.page     = ComicGenrePage(driver, platform)

    def test_001_만화장르홈_진입(self):
        self.page.enter_comic_genrehome()
        assert self.page.is_comic_genrehome_displayed(), \
            "❌ 만화 장르홈 진입 실패 — 추천 서브탭 미노출"

    def test_002_카테고리버튼_진입(self):
        self.page.click_subtab("추천")
        time.sleep(1)
        opened = self.page.open_category_page()
        assert opened, "❌ 카테고리 버튼 선택 후 '만화 카테고리' 타이틀 미노출"

    def _run_topmenu_flow(self, topmenu_name: str):
        submenus = self.page.CATEGORY_SUBMENUS[topmenu_name]
        self.page.expand_category_topmenu(topmenu_name)

        try:
            for submenu_name in submenus:
                self.page.tap_category_submenu(submenu_name)
                time.sleep(3)

                title_ok = self.page.is_category_dest_title_visible(submenu_name)
                logging.info(f"[{topmenu_name}][{submenu_name}] 목적지 타이틀 일치 {'✅' if title_ok else '❌'}")
                assert title_ok, f"❌ [{topmenu_name}][{submenu_name}] 목적지 화면 타이틀 불일치"

                collected = self.page.collect_category_dest_items_by_scroll(submenu_name)
                first_item = collected[0] if collected else "(확인불가)"
                last_item = collected[-1] if collected else "(확인불가)"
                logging.info(f"[{topmenu_name}][{submenu_name}] 1위 작품: {first_item}")
                logging.info(f"[{topmenu_name}][{submenu_name}] 마지막 작품(스크롤 수집 {len(collected)}건): {last_item}")

                self.page.navigate_back_one_screen()
                assert self.page.is_category_page_displayed(), \
                    f"❌ [{topmenu_name}][{submenu_name}] 뒤로가기 후 카테고리 화면 복귀 실패"
        finally:
            # 다음 상위메뉴 테스트가 누적 없이 깨끗한 상태에서 시작할 수 있도록, 하위메뉴
            # 순회 중 실패가 나더라도 항상 상위메뉴를 다시 접는다.
            self.page.collapse_category_topmenu(topmenu_name)

    def test_003_만화e북_하위메뉴_순회검증(self):
        self._run_topmenu_flow("만화 e북")

    def test_004_만화연재_하위메뉴_순회검증(self):
        self._run_topmenu_flow("만화 연재")

    def test_005_BL만화e북_하위메뉴_순회검증(self):
        self._run_topmenu_flow("BL 만화 e북")

    def test_006_라이트노벨_하위메뉴_순회검증(self):
        self._run_topmenu_flow("라이트노벨")
