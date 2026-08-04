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
        self.platform = platform
        self.page     = MainhomePage(driver, platform)

    def test_App_Checklist_001_앱실행(self, request):
        if request.config.getoption("--reset") == "skip":
            pytest.skip("앱 초기화 없이 실행 중 - 스킵")
        assert self.page.launch_and_verify_genrehome(), \
            "❌ 앱실행 및 장르홈 진입 실패"


class TestLogoutIfNeeded:
    """ 이미 로그인된 상태일 경우 로그아웃 진행 """
    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.platform = platform
        self.page     = LoginPage(driver, platform)

    def test_logout_if_logged_in(self, request):
        if request.config.getoption("--reset") == "skip":
            pytest.skip("단독 실행 - 스킵")
        ok, reason = self.page.logout_if_logged_in()
        assert ok, reason


class TestLogin:
    """ 로그인 """
    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.platform = platform
        self.page     = LoginPage(driver, platform)

    def test_App_Checklist_072_로그인(self, request):
        if request.config.getoption("--reset") == "skip" and request.config.getoption("--login") == "skip":
            pytest.skip("앱 초기화 없이 실행 중 - 스킵")
        assert self.page.login_if_needed(), "❌ 로그인 실패"


class _CategoryTopmenuFlowMixin:
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

                first_item = self.page.get_category_dest_first_item(submenu_name)
                logging.info(f"[{topmenu_name}][{submenu_name}] 1위 작품: {first_item}")

                self.page.navigate_back_one_screen()
                assert self.page.is_category_page_displayed(), \
                    f"❌ [{topmenu_name}][{submenu_name}] 뒤로가기 후 카테고리 화면 복귀 실패"
        finally:
            self.page.collapse_category_topmenu(topmenu_name)


class TestComicCategory(_CategoryTopmenuFlowMixin):
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

    def test_003_만화e북_하위메뉴_순회검증(self):
        self._run_topmenu_flow("만화 e북")

    def test_004_만화연재_하위메뉴_순회검증(self):
        self._run_topmenu_flow("만화 연재")

    def test_005_BL만화e북_하위메뉴_순회검증(self):
        self._run_topmenu_flow("BL 만화 e북")

    def test_006_라이트노벨_하위메뉴_순회검증(self):
        self._run_topmenu_flow("라이트노벨")


class TestWebtoonCategory(_CategoryTopmenuFlowMixin):
    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver   = driver
        self.platform = platform
        self.page     = WebtoonGenrePage(driver, platform)

    def test_001_웹툰장르홈_진입(self):
        self.page.enter_webtoon_genrehome()
        assert self.page.is_webtoon_genrehome_displayed(), \
            "❌ 웹툰 장르홈 진입 실패 — 추천 서브탭 미노출"

    def test_002_카테고리버튼_진입(self):
        self.page.click_subtab("추천")
        time.sleep(1)
        opened = self.page.open_category_page()
        assert opened, "❌ 카테고리 버튼 선택 후 '웹툰 카테고리' 타이틀 미노출"

    def test_003_웹툰_하위메뉴_순회검증(self):
        self._run_topmenu_flow("웹툰")

    def test_004_BL웹툰_하위메뉴_순회검증(self):
        self._run_topmenu_flow("BL 웹툰")


class TestWebnovelCategory(_CategoryTopmenuFlowMixin):
    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver   = driver
        self.platform = platform
        self.page     = WebnovelGenrePage(driver, platform)

    def test_001_웹소설장르홈_진입(self):
        self.page.enter_webnovel_genrehome()
        assert self.page.is_webnovel_genrehome_displayed(), \
            "❌ 웹소설 장르홈 진입 실패 — 추천 서브탭 미노출"

    def test_002_카테고리버튼_진입(self):
        self.page.click_subtab("추천")
        time.sleep(1)
        opened = self.page.open_category_page()
        assert opened, "❌ 카테고리 버튼 선택 후 '웹소설 카테고리' 타이틀 미노출"

    def test_003_로맨스웹소설_하위메뉴_순회검증(self):
        self._run_topmenu_flow("로맨스 웹소설")

    def test_004_로맨스e북_하위메뉴_순회검증(self):
        self._run_topmenu_flow("로맨스 e북")

    def test_005_로판웹소설_하위메뉴_순회검증(self):
        self._run_topmenu_flow("로판 웹소설")

    def test_006_로판e북_하위메뉴_순회검증(self):
        self._run_topmenu_flow("로판 e북")

    def test_007_판타지웹소설_하위메뉴_순회검증(self):
        self._run_topmenu_flow("판타지 웹소설")

    def test_008_판타지e북_하위메뉴_순회검증(self):
        self._run_topmenu_flow("판타지 e북")

    def test_009_BL웹소설_하위메뉴_순회검증(self):
        self._run_topmenu_flow("BL 웹소설")

    def test_010_BL소설e북_하위메뉴_순회검증(self):
        self._run_topmenu_flow("BL 소설 e북")


class TestGeneralbookCategory(_CategoryTopmenuFlowMixin):
    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver   = driver
        self.platform = platform
        self.page     = GeneralbookGenrePage(driver, platform)

    def _run_topmenu_flow(self, topmenu_name: str):
        submenus = self.page.CATEGORY_SUBMENUS[topmenu_name]
        self.page.scroll_topmenu_to_top(topmenu_name)
        self.page.expand_category_topmenu_light(topmenu_name)

        try:
            for submenu_name in submenus:
                self.page.tap_category_submenu(submenu_name)
                time.sleep(3)

                title_ok = self.page.is_category_dest_title_visible(submenu_name)
                if not title_ok and self.platform == "aos":
                    logging.warning(f"[{topmenu_name}][{submenu_name}] 실제 타이틀: '{self.page.get_current_top_title()}'")
                logging.info(f"[{topmenu_name}][{submenu_name}] 목적지 타이틀 일치 {'✅' if title_ok else '❌'}")
                assert title_ok, f"❌ [{topmenu_name}][{submenu_name}] 목적지 화면 타이틀 불일치"

                first_item = self.page.get_category_dest_first_item(submenu_name)
                logging.info(f"[{topmenu_name}][{submenu_name}] 1위 작품: {first_item}")

                self.page.navigate_back_one_screen()
                assert self.page.is_category_page_displayed(), \
                    f"❌ [{topmenu_name}][{submenu_name}] 뒤로가기 후 카테고리 화면 복귀 실패"
        finally:
            self.page.collapse_category_topmenu(topmenu_name)

    def test_001_일반도서장르홈_진입(self):
        self.page.enter_generalbook_genrehome()
        assert self.page.is_generalbook_genrehome_displayed(), \
            "❌ 일반도서 장르홈 진입 실패 — 추천 서브탭 미노출"

    def test_002_카테고리버튼_진입(self):
        self.page.click_subtab("추천")
        time.sleep(1)
        opened = self.page.open_category_page()
        assert opened, "❌ 카테고리 버튼 선택 후 '도서 카테고리' 타이틀 미노출"

    def test_003_소설_하위메뉴_순회검증(self):
        self._run_topmenu_flow("소설")

    def test_004_경영경제_하위메뉴_순회검증(self):
        self._run_topmenu_flow("경영/경제")

    def test_005_인문사회역사_하위메뉴_순회검증(self):
        self._run_topmenu_flow("인문/사회/역사")

    def test_006_자기계발_하위메뉴_순회검증(self):
        self._run_topmenu_flow("자기계발")

    def test_007_에세이시_하위메뉴_순회검증(self):
        self._run_topmenu_flow("에세이/시")

    def test_008_여행_하위메뉴_순회검증(self):
        self._run_topmenu_flow("여행")

    def test_009_종교_하위메뉴_순회검증(self):
        self._run_topmenu_flow("종교")

    def test_010_외국어_하위메뉴_순회검증(self):
        self._run_topmenu_flow("외국어")

    def test_011_과학_하위메뉴_순회검증(self):
        self._run_topmenu_flow("과학")

    def test_012_진로교육교재_하위메뉴_순회검증(self):
        self._run_topmenu_flow("진로/교육/교재")

    def test_013_컴퓨터IT_하위메뉴_순회검증(self):
        self._run_topmenu_flow("컴퓨터/IT")

    def test_014_건강다이어트_하위메뉴_순회검증(self):
        self._run_topmenu_flow("건강/다이어트")

    def test_015_가정생활_하위메뉴_순회검증(self):
        self._run_topmenu_flow("가정/생활")

    def test_016_어린이청소년_하위메뉴_순회검증(self):
        self._run_topmenu_flow("어린이/청소년")

    def test_017_해외도서_하위메뉴_순회검증(self):
        self._run_topmenu_flow("해외도서")

    def test_018_잡지_하위메뉴_순회검증(self):
        self._run_topmenu_flow("잡지")
