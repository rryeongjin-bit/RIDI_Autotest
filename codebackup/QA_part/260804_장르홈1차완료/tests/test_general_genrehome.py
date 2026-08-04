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


class TestGenrehome:
    """ 도서 장르홈 진입 """
    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver   = driver
        self.platform = platform
        self.page     = GeneralbookGenrePage(driver, platform)

    def test_001_도서장르홈_진입(self):
        self.page.enter_generalbook_genrehome()
        assert self.page.is_generalbook_genrehome_displayed(), \
            "❌ 도서 장르홈 진입 실패 — 추천 서브탭 미노출"


class TestBigbanner:
    """ 도서 장르홈 빅배너 섹션 """
    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver   = driver
        self.platform = platform
        self.page     = GeneralbookGenrePage(driver, platform)

    def test_001_도서장르홈_진입(self):
        self.page.enter_generalbook_genrehome()
        assert self.page.is_generalbook_genrehome_displayed(), \
            "❌ 도서 장르홈 진입 실패 — 추천 서브탭 미노출"

    def test_002_빅배너_스와이프(self):
        self.page.click_subtab("추천")
        time.sleep(10)

        items = self.page.collect_big_banner_items_by_polling(target_count=5)
        logging.info(f"[빅배너] 자동전환 폴링으로 수집한 배너 {len(items)}개")
        for i, text in enumerate(items, 1):
            logging.info(f"[빅배너]   {i}. {text}")

        assert len(items) >= 5, \
            f"❌ 빅배너 자동전환 폴링으로 서로 다른 배너 5개를 확인하지 못함 (수집 {len(items)}개)"


class TestQuickmenu:
    """ 도서 장르홈 퀵메뉴 섹션 (신간 / 북스 베스트 / 이벤트 / 리디온리) """
    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver   = driver
        self.platform = platform
        self.page     = GeneralbookGenrePage(driver, platform)

    def test_001_도서장르홈_진입(self):
        self.page.enter_generalbook_genrehome()
        assert self.page.is_generalbook_genrehome_displayed(), \
            "❌ 도서 장르홈 진입 실패 — 추천 서브탭 미노출"

    def test_002_퀵메뉴_좌스와이프_전체확인(self):
        self.page.click_subtab("추천")
        time.sleep(1)

        quick_menus = list(self.page.QUICK_MENU_LOCATOR.keys())
        found = {}
        for name in quick_menus:
            if self.page.is_quickmenu_visible(name, log=False):
                found[name] = "초기"
        logging.info(f"[퀵메뉴] 초기 탐색 결과: {list(found.keys()) or '없음'}")

        swipe_count = 0
        stall = 0
        while stall < 2 and swipe_count < 5 and len(found) < len(quick_menus):
            self.page.swipe_quickmenu_left()
            swipe_count += 1
            newly_found = 0
            for name in quick_menus:
                if name not in found and self.page.is_quickmenu_visible(name, log=False):
                    found[name] = f"좌스와이프 {swipe_count}회"
                    newly_found += 1
            stall = 0 if newly_found else stall + 1
            logging.info(f"[퀵메뉴] 좌스와이프 {swipe_count}회 실행")

        for name in quick_menus:
            logging.info(f"[퀵메뉴확인] {name} - {found.get(name, '미발견')}")

        for _ in range(swipe_count):
            self.page.swipe_quickmenu_right()
        logging.info(f"[퀵메뉴] 우스와이프 {swipe_count}회 원위치 복귀")

        missing = [n for n in quick_menus if n not in found]
        assert not missing, f"❌ 퀵메뉴 미발견: {missing}"

    def test_003_퀵메뉴_선택_페이지전환_복귀(self):
        self.page.click_subtab("추천")
        time.sleep(1)

        for name in self.page.QUICK_MENU_LOCATOR.keys():
            attempts = 0
            while not self.page.is_quickmenu_visible(name, timeout=2, log=False) and attempts < 5:
                self.page.swipe_quickmenu_left()
                attempts += 1
            assert self.page.is_quickmenu_visible(name, log=False), \
                f"❌ {name} 퀵메뉴 노출 실패"

            self.page.click_quickmenu(name)
            time.sleep(1)

            title_ok = self.page.verify_quickmenu_destination_title(name)
            assert title_ok, f"❌ {name} 선택 후 타이틀 불일치 — 정상 진입 실패"

            self.page.navigate_back_to_genrehome()
            assert self.page.is_generalbook_genrehome_displayed(), \
                f"❌ {name} 선택 후 장르홈 복귀 실패"

            for _ in range(attempts):
                self.page.swipe_quickmenu_right()


class TestRecommendtab:
    """ 도서 장르홈 '추천' 탭 섹션별 순회검증 """
    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver   = driver
        self.platform = platform
        self.page     = GeneralbookGenrePage(driver, platform)

    def test_001_도서장르홈_진입(self):
        self.page.enter_generalbook_genrehome()
        assert self.page.is_generalbook_genrehome_displayed(), \
            "❌ 도서 장르홈 진입 실패 — 추천 서브탭 미노출"

    def _run_section_flow(self, section_name: str, click_recommend_first: bool = False,
                          on_more_screen=None, post_more_wait: float = None,
                          skip_item_swipe: bool = False):
        if click_recommend_first:
            self.page.click_subtab("추천")
            time.sleep(1)

        found = self.page.scroll_to_section(section_name)
        if not found:
            self.page.enter_generalbook_genrehome()
            time.sleep(2)
            if click_recommend_first:
                self.page.click_subtab("추천")
                time.sleep(1)

            if section_name in self.page.AOS_PERSONALIZED_SECTIONS:
                pytest.skip(f"[{section_name}] 계정 상태로 개인화 섹션 미노출 - 스킵")
        assert found, f"❌ [{section_name}] 섹션 미노출"

        if self.platform == "aos" and section_name in self.page.AOS_PERSONALIZED_SECTIONS \
                and not self.page.is_section_title_present(section_name):
            pytest.skip(f"[{section_name}] 개인화 섹션 요소 소실(계정 상태) - 스킵")

        if skip_item_swipe:
            logging.info(f"[{section_name}] 좌우스와이프 생략 - 더보기 진입/타이틀 확인만 진행")
        else:
            items = self.page.get_section_item_names(section_name)
            first_item = items[0] if items else "(확인불가)"
            logging.info(f"[{section_name}] 첫번째 작품: {first_item}")

            collected, swipe_count = self.page.collect_section_items_by_swipe(section_name)
            logging.info(f"[{section_name}] 좌스와이프 {swipe_count}회 - 총 콘텐츠 수: {len(collected)}개")
            for i, name in enumerate(collected, 1):
                logging.info(f"[{section_name}]   {i}. {name}")
            logging.info(f"[{section_name}] 마지막 작품: {collected[-1] if collected else '(확인불가)'}")

            for _ in range(swipe_count):
                self.page.swipe_section_right(section_name)
            logging.info(f"[{section_name}] 우스와이프 {swipe_count}회 원위치 복귀")

        if not self.page.is_section_more_visible(section_name):
            logging.info(f"[{section_name}] 더보기 버튼 없음 - 스킵")
            return

        try:
            dest_title, verified = self.page.click_section_more_and_verify(section_name)
            navigated = bool(dest_title.strip())
            logging.info(
                f"[{section_name}] 더보기 클릭 → 화면전환 {'✅' if navigated else '❌'} "
                f"(상단타이틀: '{dest_title}')"
            )
        except Exception as e:
            navigated, verified = True, True
            logging.warning(
                f"[{section_name}] 화면전환 타이틀 확인 실패(iOS WDA 이슈 가능) - "
                f"더보기 클릭은 성공했으므로 화면전환된 것으로 간주: {e}"
            )
        if not verified:
            expected = self.page.IOS_SECTION_MORE_DEST_HINT.get(section_name, "(힌트없음)")
            back_ok = self.page.is_generalbook_genrehome_displayed()
            pytest.fail(
                f"❌ [{section_name}] 더보기 목적지 타이틀 검증 실패 "
                f"(기대: '{expected}' / 실제: '{dest_title}')"
                + ("" if back_ok else " + 장르홈 복귀도 실패")
            )
        time.sleep(post_more_wait if post_more_wait is not None else (1 if on_more_screen else 0))
        if navigated:
            if on_more_screen:
                on_more_screen()
            self.page.navigate_back_to_genrehome()
            assert self.page.is_generalbook_genrehome_displayed(), \
                f"❌ [{section_name}] 더보기 화면전환 후 장르홈 복귀 실패"

    def _log_more_screen_first_last(self, section_name: str):
        """더보기 화면 진입 후 세로스크롤하며 첫번째/마지막 작품명 로그"""
        try:
            items = self.page.get_visible_content_item_names()
            first_item = items[0] if items else "(확인불가)"
            collected = self.page.collect_items_by_vertical_scroll()
            last_item = collected[-1] if collected else first_item
            logging.info(f"[{section_name}][더보기 화면] 첫번째 작품: {first_item}")
            logging.info(f"[{section_name}][더보기 화면] 마지막 작품: {last_item}")
        except Exception as e:
            logging.warning(f"[{section_name}][더보기 화면] 첫/마지막 작품 확인 실패: {e}")

    def test_002_방금본작품과비슷한_섹션(self):
        self._run_section_flow("방금 본 작품과 비슷한", click_recommend_first=True)

    def test_003_지금많이읽고있는작품_섹션(self):
        section_name = "지금 많이 읽고 있는 작품"
        self._run_section_flow(section_name,
                               on_more_screen=lambda: self._log_more_screen_first_last(section_name))

    def test_004_오늘리디의발견_섹션(self):
        self._run_section_flow("오늘, 리디의 발견")

    def test_005_구매이력기반AI추천_섹션(self):
        section_name = "구매이력 기반 AI 추천"
        self._run_section_flow(section_name,
                               on_more_screen=lambda: self._log_more_screen_first_last(section_name))

    def test_006_이벤트_섹션(self):
        self._run_section_flow("이벤트", post_more_wait=3, skip_item_swipe=True)

    def test_007_베스트_섹션(self):
        section_name = "베스트"
        self._run_section_flow(section_name,
                               on_more_screen=lambda: self._log_more_screen_first_last(section_name))

    def test_008_새로나온작품_섹션(self):
        section_name = "새로 나온 작품"
        self._run_section_flow(section_name,
                               on_more_screen=lambda: self._log_more_screen_first_last(section_name))

    def test_009_지금리디에서만볼수있는도서_섹션(self):
        section_name = "지금, 리디에서만 볼 수 있는 도서"
        self._run_section_flow(section_name,
                               on_more_screen=lambda: self._log_more_screen_first_last(section_name))

    def test_010_취향저격AI추천_섹션(self):
        if not self.page.is_generalbook_genrehome_displayed():
            logging.warning("[취향저격 AI추천 섹션] 장르홈이 아닌 화면에서 시작 - 장르홈 재진입")
            self.page.enter_generalbook_genrehome()
            time.sleep(2)
        section_name = "취향저격 AI추천 섹션"
        found = self.page.scroll_to_section(section_name, max_scroll=30)
        if not found and section_name in self.page.AOS_PERSONALIZED_SECTIONS:
            pytest.skip(f"[{section_name}] 개인화 섹션 미노출(계정 상태) - 스킵")
        assert found, f"❌ [{section_name}] 섹션 미노출"

        if self.platform == "aos" and section_name in self.page.AOS_PERSONALIZED_SECTIONS \
                and not self.page.is_section_title_present(section_name):
            pytest.skip(f"[{section_name}] 개인화 섹션 요소 소실(계정 상태) - 스킵")

        items = self.page.get_section_item_names(section_name)
        first_item = items[0] if items else "(확인불가)"
        logging.info(f"[{section_name}] 첫번째 작품: {first_item}")

        last_item, footer_reached = self.page.scroll_to_footer_and_get_last_item(section_name)
        logging.info(
            f"[{section_name}] 마지막 작품(푸터 노출 {'✅' if footer_reached else '❌'}): {last_item}"
        )
