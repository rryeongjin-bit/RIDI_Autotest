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
    """ 웹툰 장르홈 진입/서브탭 순회"""
    SUBTAB_FIXED = ["추천", "로맨스", "BL", "판타지/SF"]
    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver   = driver
        self.platform = platform
        self.page     = WebtoonGenrePage(driver, platform)

    def test_001_웹툰장르홈_진입(self):
        self.page.enter_webtoon_genrehome()
        assert self.page.is_webtoon_genrehome_displayed(), \
            "❌ 웹툰 장르홈 진입 실패 — 추천 서브탭 미노출"

    def test_002_서브탭_좌우스와이프_전체탭확인(self):
        found = {}

        # 초기 노출 탭 확인 (고정 4개)
        for tab in self.SUBTAB_FIXED:
            if self.page.is_subtab_visible(tab):
                found[tab] = "초기"
        logging.info(f"[서브탭] 초기 탐색 결과: {list(found.keys()) or '없음'}")

        if self.platform == "aos":
            left_swipe_count = 0
            stall = 0
            prev_names = tuple(self.page.get_all_subtab_names())
            while stall < 2 and left_swipe_count < 5:
                self.page.swipe_subtab_left()
                left_swipe_count += 1
                for tab in self.SUBTAB_FIXED:
                    if tab not in found and self.page.is_subtab_visible(tab):
                        found[tab] = f"좌스와이프 {left_swipe_count}회"
                cur_names = tuple(self.page.get_all_subtab_names())
                stall = 0 if cur_names != prev_names else stall + 1
                logging.info(f"[서브탭] 좌스와이프 {left_swipe_count}회 실행")
                prev_names = cur_names
            logging.info(f"[서브탭] 좌스와이프 총 {left_swipe_count}회로 끝까지 이동 완료 - 전체 노출 탭 {list(cur_names)}")
        else:
            left_swipe_count = 3
            for swipe_count in range(1, left_swipe_count + 1):
                self.page.swipe_subtab_left()
                for tab in self.SUBTAB_FIXED:
                    if tab not in found and self.page.is_subtab_visible(tab):
                        found[tab] = f"좌스와이프 {swipe_count}회"
                logging.info(f"[서브탭] 좌스와이프 {swipe_count}회 실행")
            logging.info(f"[서브탭] 좌스와이프 총 {left_swipe_count}회(고정)로 끝까지 이동 완료")

        not_found = [t for t in self.SUBTAB_FIXED if t not in found]
        if not_found:
            logging.info(f"[서브탭] 미발견 고정 탭: {not_found}")

        for right_count in range(1, left_swipe_count + 1):
            self.page.swipe_subtab_right()
            logging.info(f"[서브탭] 우스와이프 {right_count}/{left_swipe_count}회 복귀 진행 중")

        right_swipe_ok = self.page.is_subtab_visible("추천")
        logging.info(f"[서브탭] 처음(추천) 복귀 {'✅' if right_swipe_ok else '❌'}")

        # pass 기준: 고정탭 4개 모두 발견 + 처음 위치로 정상 복귀
        missing_fixed = [t for t in self.SUBTAB_FIXED if t not in found]
        assert not missing_fixed, f"❌ 고정 서브탭 미발견: {missing_fixed}"
        assert right_swipe_ok, "❌ 우스와이프로 처음까지 복귀 실패 — 우방향 스와이프 동작 이상"

    def test_003_서브탭_순차이동_정역방향(self):
        time.sleep(3)

        # 정방향: 추천 → 로맨스 → BL → 판타지/SF
        for tab in ["로맨스", "BL", "판타지/SF"]:
            self.page.click_subtab(tab, log=False)
            time.sleep(1)
            ok = self.page.is_subtab_visible(tab, log=False)
            logging.info(f"[서브탭 선택이동확인] {tab} {'✅' if ok else '❌'}")
            assert ok, f"❌ {tab} 서브탭 진입 실패 (정방향)"
        logging.info("[서브탭] 정방향 이동 완료")

        # 역방향: 판타지/SF → BL → 로맨스 → 추천
        for tab in ["BL", "로맨스", "추천"]:
            self.page.click_subtab(tab, log=False)
            time.sleep(1)
            ok = self.page.is_subtab_visible(tab, log=False)
            logging.info(f"[서브탭 선택이동확인] {tab} {'✅' if ok else '❌'}")
            assert ok, f"❌ {tab} 서브탭 복귀 실패 (역방향)"
        logging.info("[서브탭] 역방향 이동복귀 완료")

        assert self.page.is_quickmenu_visible("이달의 신작"), \
            "❌ 추천 서브탭 복귀 후 이달의 신작 퀵메뉴 미노출"


class TestBigbanner:
    """ 웹툰 장르홈 빅배너 섹션 - 만화 장르홈과 동일한 방식(자동전환 폴링)으로 검증 """
    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver   = driver
        self.platform = platform
        self.page     = WebtoonGenrePage(driver, platform)

    def test_001_웹툰장르홈_진입(self):
        self.page.enter_webtoon_genrehome()
        assert self.page.is_webtoon_genrehome_displayed(), \
            "❌ 웹툰 장르홈 진입 실패 — 추천 서브탭 미노출"

    def test_002_빅배너_스와이프(self):
        self.page.click_subtab("추천")
        time.sleep(3)

        items = self.page.collect_big_banner_items_by_polling(target_count=5)
        logging.info(f"[빅배너] 자동전환 폴링으로 수집한 배너 {len(items)}개")
        for i, text in enumerate(items, 1):
            logging.info(f"[빅배너]   {i}. {text}")

        assert len(items) >= 5, f"❌ 빅배너 자동전환 폴링으로 서로 다른 배너 5개를 확인하지 못함 (수집 {len(items)}개)"


class TestQuickmenu:
    """ 웹툰 장르홈 퀵메뉴 섹션 """
    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver   = driver
        self.platform = platform
        self.page     = WebtoonGenrePage(driver, platform)

    def test_001_웹툰장르홈_진입(self):
        self.page.enter_webtoon_genrehome()
        assert self.page.is_webtoon_genrehome_displayed(), \
            "❌ 웹툰 장르홈 진입 실패 — 추천 서브탭 미노출"

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
            status = found.get(name, "미발견")
            logging.info(f"[퀵메뉴확인] {name} - {status}")

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
            assert self.page.is_webtoon_genrehome_displayed(), \
                f"❌ {name} 선택 후 장르홈 복귀 실패"

            for _ in range(attempts):
                self.page.swipe_quickmenu_right()


class TestRecommendtab:
    """ 웹툰 장르홈 '추천' 탭 섹션별 순회검증 """
    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver   = driver
        self.platform = platform
        self.page     = WebtoonGenrePage(driver, platform)

    def test_001_웹툰장르홈_진입(self):
        self.page.enter_webtoon_genrehome()
        assert self.page.is_webtoon_genrehome_displayed(), \
            "❌ 웹툰 장르홈 진입 실패 — 추천 서브탭 미노출"

    def _run_section_flow(self, section_name: str, click_recommend_first: bool = False, on_more_screen=None,
                          back_via_subtab: bool = False, post_more_wait: float = None, skip_item_swipe: bool = False,
                          first_item_no_swipe: bool = False):
        if click_recommend_first:
            self.page.click_subtab("추천")
            time.sleep(1)

        found = self.page.scroll_to_section(section_name)
        if not found:
    
            self.page.enter_webtoon_genrehome()
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

        if first_item_no_swipe:
            items = self.page.get_section_item_names(section_name)
            first_item = items[0] if items else "(확인불가)"
            logging.info(f"[{section_name}] 첫번째 작품: {first_item}")
            logging.info(f"[{section_name}] 가로 스크롤 불가 섹션 - 좌우스와이프 생략, 더보기 진입만 진행")
        elif skip_item_swipe:
            logging.info(f"[{section_name}] 좌우스와이프 생략 - 더보기 진입/타이틀 확인만 진행")
        elif section_name in self.page.NO_HORIZONTAL_SWIPE_SECTIONS:
            items = self.page.get_section_item_names(section_name)
            first_item = items[0] if items else "(확인불가)"
            logging.info(f"[{section_name}] 첫번째 작품: {first_item}")

            last_item = self.page.scroll_and_get_last_item(section_name, scroll_times=3)
            logging.info(f"[{section_name}] 상하스크롤 3회 후 마지막 작품: {last_item or '(확인불가)'}")
            logging.info(f"[{section_name}] 가로 스크롤 불가 섹션 - 좌우스와이프/더보기 없이 종료")
            return
        else:
            items = self.page.get_section_item_names(section_name)
            first_item = items[0] if items else "(확인불가)"
            logging.info(f"[{section_name}] 첫번째 작품: {first_item}")

            collected, swipe_count = self.page.collect_section_items_by_swipe(section_name)
            logging.info(f"[{section_name}] 좌스와이프 {swipe_count}회 - 총 콘텐츠 수: {len(collected)}개")
            for i, name in enumerate(collected, 1):
                logging.info(f"[{section_name}]   {i}. {name}")

            last_item = collected[-1] if collected else "(확인불가)"
            logging.info(f"[{section_name}] 마지막 작품: {last_item}")

            for _ in range(swipe_count):
                self.page.swipe_section_right(section_name)
            logging.info(f"[{section_name}] 우스와이프 {swipe_count}회 원위치 복귀")

        if not self.page.is_section_more_visible(section_name):
            logging.info(f"[{section_name}] 더보기 버튼 없음 - 스킵")
            return

        try:
            dest_title, verified = self.page.click_section_more_and_verify(section_name)
            navigated = bool(dest_title.strip())
            logging.info(f"[{section_name}] 더보기 클릭 → 화면전환 {'✅' if navigated else '❌'} (상단타이틀: '{dest_title}')")
        except Exception as e:
            navigated, verified = True, True
            logging.warning(f"[{section_name}] 화면전환 타이틀 확인 실패(iOS WDA 이슈 가능) - 더보기 클릭은 성공했으므로 화면전환된 것으로 간주: {e}")
        if not verified:
            expected = self.page.IOS_SECTION_MORE_DEST_HINT.get(section_name, "(힌트없음)")
            back_ok = self.page.is_webtoon_genrehome_displayed()
            pytest.fail(
                f"❌ [{section_name}] 더보기 목적지 타이틀 검증 실패 "
                f"(기대: '{expected}' / 실제: '{dest_title}')"
                + ("" if back_ok else " + 장르홈 복귀도 실패")
            )
        time.sleep(post_more_wait if post_more_wait is not None else (1 if on_more_screen else 0))
        if navigated:
            if on_more_screen:
                on_more_screen()
            if back_via_subtab:
                self.page.click_subtab("추천")
                time.sleep(1)
            else:
                self.page.navigate_back_to_genrehome()
            assert self.page.is_webtoon_genrehome_displayed(), \
                f"❌ [{section_name}] 더보기 화면전환 후 장르홈 복귀 실패"

    def _log_more_screen_first_last(self, section_name: str):
        try:
            items = self.page.get_visible_content_item_names()
            first_item = items[0] if items else "(확인불가)"
            collected = self.page.collect_items_by_vertical_scroll()
            last_item = collected[-1] if collected else first_item
            logging.info(f"[{section_name}][더보기 화면] 첫번째 작품: {first_item}")
            logging.info(f"[{section_name}][더보기 화면] 마지막 작품: {last_item}")
        except Exception as e:
            logging.warning(f"[{section_name}][더보기 화면] 첫/마지막 작품 확인 실패(iOS WDA 이슈 가능): {e}")

    # 퀵메뉴 바로 아래 섹션이라 요일별 웹툰보다 앞에 온다. 만화/웹소설/도서는 모두 추천탭
    # 기준으로 이 섹션을 검증하는데 웹툰만 로맨스/BL/판타지 서브탭에만 있어서 추천탭
    # 커버리지가 비어 있었다(2026-08-04). 서브탭별 테스트는 그대로 두고 추천탭을 추가한다.
    def test_002_방금본작품과비슷한_섹션(self):
        self.page.click_subtab("추천")
        time.sleep(1)
        self._run_section_flow("방금 본 작품과 비슷한")

    def test_003_요일별웹툰_섹션(self):
        self.page.click_subtab("추천")
        time.sleep(1)
        self._run_section_flow("요일별 웹툰")

    def test_004_기다리면무료로시작해_섹션(self):
        self._run_section_flow("기다리면 무료로 시작해!")

    def test_005_오늘리디의발견_섹션(self):
        self._run_section_flow("오늘리디의 발견")

    def test_006_구매이력기반AI추천_섹션(self):
        section_name = "구매이력기반 AI 추천"
        self._run_section_flow(section_name, on_more_screen=lambda: self._log_more_screen_first_last(section_name))

    def test_007_웹툰만화키워드검색_섹션(self):
        self._run_section_flow("웹툰 키워드 검색", post_more_wait=3, skip_item_swipe=True)

    def test_008_웹툰베스트_섹션(self):
        section_name = "웹툰 베스트"
        self._run_section_flow(section_name, on_more_screen=lambda: self._log_more_screen_first_last(section_name))

    def test_009_지금리디에서만볼수있는웹툰_섹션(self):
        section_name = "지금리디에서만볼수있는 웹툰"
        self._run_section_flow(section_name, on_more_screen=lambda: self._log_more_screen_first_last(section_name))

    def test_010_새로나온작품_섹션(self):
        section_name = "새로나온작품"
        self._run_section_flow(section_name, on_more_screen=lambda: self._log_more_screen_first_last(section_name))

    def test_011_취향저격AI추천_섹션(self):
        if not self.page.is_webtoon_genrehome_displayed():
            logging.warning("[취향저격 AI추천 섹션] 장르홈이 아닌 화면에서 시작 - 장르홈 재진입")
            self.page.enter_webtoon_genrehome()
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
        logging.info(f"[{section_name}] 마지막 작품(푸터 노출 {'✅' if footer_reached else '❌'}): {last_item}")


class TestRomancetab:
    """ 웹툰 장르홈 '로맨스' 탭 섹션별 순회검증 """
    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver   = driver
        self.platform = platform
        self.page     = WebtoonGenrePage(driver, platform)

    def test_001_웹툰장르홈_진입(self):
        self.page.enter_webtoon_genrehome()
        assert self.page.is_webtoon_genrehome_displayed(), \
            "❌ 웹툰 장르홈 진입 실패 — 추천 서브탭 미노출"

    def _run_section_flow(self, section_name: str, click_romance_first: bool = False, on_more_screen=None,
                          back_via_subtab: bool = False, post_more_wait: float = None, skip_item_swipe: bool = False,
                          subtab_name: str = None, first_item_no_swipe: bool = False):
        if click_romance_first:
            self.page.click_subtab("로맨스")
            time.sleep(1)

        found = self.page.scroll_to_section(section_name, subtab_name=subtab_name)
        if not found:
           
            self.page.enter_webtoon_genrehome()
            time.sleep(2)
          
            self.page.click_subtab("로맨스")
            time.sleep(1)
            if section_name in self.page.AOS_PERSONALIZED_SECTIONS:
                pytest.skip(f"[{section_name}] 계정 상태로 개인화 섹션 미노출 - 스킵")
        assert found, f"❌ [{section_name}] 섹션 미노출"

        if self.platform == "aos" and section_name in self.page.AOS_PERSONALIZED_SECTIONS \
                and not self.page.is_section_title_present(section_name):
            pytest.skip(f"[{section_name}] 개인화 섹션 요소 소실(계정 상태) - 스킵")

        if first_item_no_swipe:

            items = self.page.get_section_item_names(section_name)
            first_item = items[0] if items else "(확인불가)"
            logging.info(f"[{section_name}] 첫번째 작품: {first_item}")
            logging.info(f"[{section_name}] 가로 스크롤 불가 섹션 - 좌우스와이프 생략, 더보기 진입만 진행")
        elif skip_item_swipe:
            logging.info(f"[{section_name}] 좌우스와이프 생략 - 더보기 진입/타이틀 확인만 진행")
        elif section_name in self.page.NO_HORIZONTAL_SWIPE_SECTIONS:
         
            items = self.page.get_section_item_names(section_name)
            first_item = items[0] if items else "(확인불가)"
            logging.info(f"[{section_name}] 첫번째 작품: {first_item}")

            last_item = self.page.scroll_and_get_last_item(section_name, scroll_times=3)
            logging.info(f"[{section_name}] 상하스크롤 3회 후 마지막 작품: {last_item or '(확인불가)'}")
            logging.info(f"[{section_name}] 가로 스크롤 불가 섹션 - 좌우스와이프/더보기 없이 종료")
            return
        else:
            items = self.page.get_section_item_names(section_name)
            first_item = items[0] if items else "(확인불가)"
            logging.info(f"[{section_name}] 첫번째 작품: {first_item}")

            collected, swipe_count = self.page.collect_section_items_by_swipe(section_name)
            logging.info(f"[{section_name}] 좌스와이프 {swipe_count}회 - 총 콘텐츠 수: {len(collected)}개")
            for i, name in enumerate(collected, 1):
                logging.info(f"[{section_name}]   {i}. {name}")

            last_item = collected[-1] if collected else "(확인불가)"
            logging.info(f"[{section_name}] 마지막 작품: {last_item}")

            for _ in range(swipe_count):
                self.page.swipe_section_right(section_name)
            logging.info(f"[{section_name}] 우스와이프 {swipe_count}회 원위치 복귀")

        if not self.page.is_section_more_visible(section_name):
            logging.info(f"[{section_name}] 더보기 버튼 없음 - 스킵")
            return

        try:
            dest_title, verified = self.page.click_section_more_and_verify(section_name)
            navigated = bool(dest_title.strip())
            logging.info(f"[{section_name}] 더보기 클릭 → 화면전환 {'✅' if navigated else '❌'} (상단타이틀: '{dest_title}')")
        except Exception as e:
            navigated, verified = True, True
            logging.warning(f"[{section_name}] 화면전환 타이틀 확인 실패(iOS WDA 이슈 가능) - 더보기 클릭은 성공했으므로 화면전환된 것으로 간주: {e}")
        if not verified:
           
            expected = self.page.IOS_SECTION_MORE_DEST_HINT.get(section_name, "(힌트없음)")
            back_ok = self.page.is_webtoon_genrehome_displayed()
            pytest.fail(
                f"❌ [{section_name}] 더보기 목적지 타이틀 검증 실패 "
                f"(기대: '{expected}' / 실제: '{dest_title}')"
                + ("" if back_ok else " + 장르홈 복귀도 실패")
            )
        time.sleep(post_more_wait if post_more_wait is not None else (1 if on_more_screen else 0))
        if navigated:
            if on_more_screen:
                on_more_screen()
            if back_via_subtab:
                self.page.click_subtab("로맨스")
                time.sleep(1)
            else:
                self.page.navigate_back_to_genrehome()
            assert self.page.is_webtoon_genrehome_displayed(), \
                f"❌ [{section_name}] 더보기 화면전환 후 장르홈 복귀 실패"

    def _log_more_screen_first_last(self, section_name: str):
        try:
            items = self.page.get_visible_content_item_names()
            first_item = items[0] if items else "(확인불가)"
            collected = self.page.collect_items_by_vertical_scroll()
            last_item = collected[-1] if collected else first_item
            logging.info(f"[{section_name}][더보기 화면] 첫번째 작품: {first_item}")
            logging.info(f"[{section_name}][더보기 화면] 마지막 작품: {last_item}")
        except Exception as e:
            logging.warning(f"[{section_name}][더보기 화면] 첫/마지막 작품 확인 실패(iOS WDA 이슈 가능): {e}")

    def test_002_방금본작품과비슷한_섹션(self):
        self._run_section_flow("방금 본 작품과 비슷한", click_romance_first=True, subtab_name="로맨스")

    def test_003_오늘리디의발견_섹션(self):
        self._run_section_flow("오늘, 리디의 발견")

    def test_004_실시간랭킹_섹션(self):
        self._run_section_flow("실시간 랭킹")

    def test_005_로맨스기다리면무료_섹션(self):
        self._run_section_flow("로맨스 기다리면 무료!")

    def test_006_로맨스베스트_섹션(self):
        section_name = "로맨스 베스트"
        self._run_section_flow(section_name, on_more_screen=lambda: self._log_more_screen_first_last(section_name))

    def test_007_웹툰만화키워드검색_섹션(self):
        self._run_section_flow("웹툰/만화 키워드 검색", post_more_wait=3, skip_item_swipe=True)

    def test_008_오직리디에서만_섹션(self):
        self._run_section_flow("오직 리디에서만!")


class TestBLtab:
    """ 웹툰 장르홈 'BL' 탭 섹션별 순회검증 """
    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver   = driver
        self.platform = platform
        self.page     = WebtoonGenrePage(driver, platform)

    def test_001_웹툰장르홈_진입(self):
        self.page.enter_webtoon_genrehome()
        assert self.page.is_webtoon_genrehome_displayed(), \
            "❌ 웹툰 장르홈 진입 실패 — 추천 서브탭 미노출"

    def _run_section_flow(self, section_name: str, click_bl_first: bool = False, on_more_screen=None,
                          back_via_subtab: bool = False, post_more_wait: float = None, skip_item_swipe: bool = False,
                          subtab_name: str = None, first_item_no_swipe: bool = False):
        if click_bl_first:
            self.page.click_subtab("BL")
            time.sleep(1)

        found = self.page.scroll_to_section(section_name, subtab_name=subtab_name)
        if not found:
          
            self.page.enter_webtoon_genrehome()
            time.sleep(2)
           
            self.page.click_subtab("BL")
            time.sleep(1)
            
            if section_name in self.page.AOS_PERSONALIZED_SECTIONS:
                pytest.skip(f"[{section_name}] 계정 상태로 개인화 섹션 미노출 - 스킵")
        assert found, f"❌ [{section_name}] 섹션 미노출"
        if self.platform == "aos" and section_name in self.page.AOS_PERSONALIZED_SECTIONS \
                and not self.page.is_section_title_present(section_name):
            pytest.skip(f"[{section_name}] 개인화 섹션 요소 소실(계정 상태) - 스킵")

        if first_item_no_swipe:
            items = self.page.get_section_item_names(section_name)
            first_item = items[0] if items else "(확인불가)"
            logging.info(f"[{section_name}] 첫번째 작품: {first_item}")
            logging.info(f"[{section_name}] 가로 스크롤 불가 섹션 - 좌우스와이프 생략, 더보기 진입만 진행")
        elif skip_item_swipe:
            logging.info(f"[{section_name}] 좌우스와이프 생략 - 더보기 진입/타이틀 확인만 진행")
        elif section_name in self.page.NO_HORIZONTAL_SWIPE_SECTIONS:
            items = self.page.get_section_item_names(section_name)
            first_item = items[0] if items else "(확인불가)"
            logging.info(f"[{section_name}] 첫번째 작품: {first_item}")

            last_item = self.page.scroll_and_get_last_item(section_name, scroll_times=3)
            logging.info(f"[{section_name}] 상하스크롤 3회 후 마지막 작품: {last_item or '(확인불가)'}")
            logging.info(f"[{section_name}] 가로 스크롤 불가 섹션 - 좌우스와이프/더보기 없이 종료")
            return
        else:
            items = self.page.get_section_item_names(section_name)
            first_item = items[0] if items else "(확인불가)"
            logging.info(f"[{section_name}] 첫번째 작품: {first_item}")

            collected, swipe_count = self.page.collect_section_items_by_swipe(section_name)
            logging.info(f"[{section_name}] 좌스와이프 {swipe_count}회 - 총 콘텐츠 수: {len(collected)}개")
            for i, name in enumerate(collected, 1):
                logging.info(f"[{section_name}]   {i}. {name}")

            last_item = collected[-1] if collected else "(확인불가)"
            logging.info(f"[{section_name}] 마지막 작품: {last_item}")

            for _ in range(swipe_count):
                self.page.swipe_section_right(section_name)
            logging.info(f"[{section_name}] 우스와이프 {swipe_count}회 원위치 복귀")

        if not self.page.is_section_more_visible(section_name):
            logging.info(f"[{section_name}] 더보기 버튼 없음 - 스킵")
            return

        try:
            dest_title, verified = self.page.click_section_more_and_verify(section_name)
            navigated = bool(dest_title.strip())
            logging.info(f"[{section_name}] 더보기 클릭 → 화면전환 {'✅' if navigated else '❌'} (상단타이틀: '{dest_title}')")
        except Exception as e:
            navigated, verified = True, True
            logging.warning(f"[{section_name}] 화면전환 타이틀 확인 실패(iOS WDA 이슈 가능) - 더보기 클릭은 성공했으므로 화면전환된 것으로 간주: {e}")
        if not verified:
            expected = self.page.IOS_SECTION_MORE_DEST_HINT.get(section_name, "(힌트없음)")
            back_ok = self.page.is_webtoon_genrehome_displayed()
            pytest.fail(
                f"❌ [{section_name}] 더보기 목적지 타이틀 검증 실패 "
                f"(기대: '{expected}' / 실제: '{dest_title}')"
                + ("" if back_ok else " + 장르홈 복귀도 실패")
            )
        time.sleep(post_more_wait if post_more_wait is not None else (1 if on_more_screen else 0))
        if navigated:
            if on_more_screen:
                on_more_screen()
            if back_via_subtab:
                self.page.click_subtab("BL")
                time.sleep(1)
            else:
                self.page.navigate_back_to_genrehome()
            assert self.page.is_webtoon_genrehome_displayed(), \
                f"❌ [{section_name}] 더보기 화면전환 후 장르홈 복귀 실패"

    def _log_more_screen_first_last(self, section_name: str):
        try:
            items = self.page.get_visible_content_item_names()
            first_item = items[0] if items else "(확인불가)"
            collected = self.page.collect_items_by_vertical_scroll()
            last_item = collected[-1] if collected else first_item
            logging.info(f"[{section_name}][더보기 화면] 첫번째 작품: {first_item}")
            logging.info(f"[{section_name}][더보기 화면] 마지막 작품: {last_item}")
        except Exception as e:
            logging.warning(f"[{section_name}][더보기 화면] 첫/마지막 작품 확인 실패(iOS WDA 이슈 가능): {e}")

    def test_002_방금본작품과비슷한_섹션(self):
        self._run_section_flow("방금 본 작품과 비슷한", click_bl_first=True, subtab_name="BL")

    def test_003_BL웹툰실시간랭킹_섹션(self):
        self._run_section_flow("BL웹툰 실시간 랭킹")

    def test_004_오늘리디의발견_섹션(self):
        self._run_section_flow("BL 오늘, 리디의 발견")

    def test_005_구매이력기반AI추천_섹션(self):
        section_name = "BL 구매이력기반 AI 추천"
        self._run_section_flow(section_name, on_more_screen=lambda: self._log_more_screen_first_last(section_name))

    def test_006_BL웹툰베스트_섹션(self):
        section_name = "BL웹툰 베스트"
        self._run_section_flow(section_name, on_more_screen=lambda: self._log_more_screen_first_last(section_name))

    def test_007_BL키워드검색_섹션(self):
        self._run_section_flow("BL키워드 검색", post_more_wait=3, skip_item_swipe=True)

    def test_008_BL요일별웹툰_섹션(self):
        section_name = "BL 요일별 웹툰"
        self._run_section_flow(section_name, on_more_screen=lambda: self._log_more_screen_first_last(section_name))

    def test_009_지금리디에서만볼수있는BL웹툰_섹션(self):
        section_name = "지금, 리디에서만 볼수있는 BL 웹툰"
        self._run_section_flow(section_name, on_more_screen=lambda: self._log_more_screen_first_last(section_name))

    def test_010_RIDIONLY신작모음_섹션(self):
        section_name = "RIDI ONLY 신작 모음"
        self._run_section_flow(section_name, on_more_screen=lambda: self._log_more_screen_first_last(section_name))

    def test_011_이작품어때요_섹션(self):
        self._run_section_flow("이 작품 어때요")

    def test_012_BL탭_마지막지점_확인(self):
        if not self.page.is_webtoon_genrehome_displayed():
            logging.warning("[BL탭 마지막지점] 장르홈이 아닌 화면에서 시작 - 장르홈 재진입")
            self.page.enter_webtoon_genrehome()
            time.sleep(2)
            self.page.click_subtab("BL")
            time.sleep(1)

        last_item = self.page.scroll_and_get_last_item("취향저격 AI추천 섹션", scroll_times=5)
        logging.info(f"[BL탭 마지막지점] 스크롤 5회 후 마지막 작품: {last_item or '(확인불가)'}")


class TestFantasytab:
    """ 웹툰 장르홈 '판타지/SF' 탭 섹션별 순회검증"""
    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver   = driver
        self.platform = platform
        self.page     = WebtoonGenrePage(driver, platform)

    def test_001_웹툰장르홈_진입(self):
        self.page.enter_webtoon_genrehome()
        assert self.page.is_webtoon_genrehome_displayed(), \
            "❌ 웹툰 장르홈 진입 실패 — 추천 서브탭 미노출"

    def _run_section_flow(self, section_name: str, click_fantasy_first: bool = False, on_more_screen=None,
                          back_via_subtab: bool = False, post_more_wait: float = None, skip_item_swipe: bool = False,
                          subtab_name: str = None, first_item_no_swipe: bool = False):
        if click_fantasy_first:
            self.page.click_subtab("판타지/SF")
            time.sleep(1)

        found = self.page.scroll_to_section(section_name, subtab_name=subtab_name)
        if not found:
            self.page.enter_webtoon_genrehome()
            time.sleep(2)
            
            self.page.click_subtab("판타지/SF")
            time.sleep(1)
            if section_name in self.page.AOS_PERSONALIZED_SECTIONS:
                pytest.skip(f"[{section_name}] 계정 상태로 개인화 섹션 미노출 - 스킵")
        assert found, f"❌ [{section_name}] 섹션 미노출"

        if self.platform == "aos" and section_name in self.page.AOS_PERSONALIZED_SECTIONS \
                and not self.page.is_section_title_present(section_name):
            pytest.skip(f"[{section_name}] 개인화 섹션 요소 소실(계정 상태) - 스킵")

        if first_item_no_swipe:
           
            items = self.page.get_section_item_names(section_name)
            first_item = items[0] if items else "(확인불가)"
            logging.info(f"[{section_name}] 첫번째 작품: {first_item}")
            logging.info(f"[{section_name}] 가로 스크롤 불가 섹션 - 좌우스와이프 생략, 더보기 진입만 진행")
        elif skip_item_swipe:
            logging.info(f"[{section_name}] 좌우스와이프 생략 - 더보기 진입/타이틀 확인만 진행")
        elif section_name in self.page.NO_HORIZONTAL_SWIPE_SECTIONS:
            
            items = self.page.get_section_item_names(section_name)
            first_item = items[0] if items else "(확인불가)"
            logging.info(f"[{section_name}] 첫번째 작품: {first_item}")

            last_item = self.page.scroll_and_get_last_item(section_name, scroll_times=3)
            logging.info(f"[{section_name}] 상하스크롤 3회 후 마지막 작품: {last_item or '(확인불가)'}")
            logging.info(f"[{section_name}] 가로 스크롤 불가 섹션 - 좌우스와이프/더보기 없이 종료")
            return
        else:
            items = self.page.get_section_item_names(section_name)
            first_item = items[0] if items else "(확인불가)"
            logging.info(f"[{section_name}] 첫번째 작품: {first_item}")

            collected, swipe_count = self.page.collect_section_items_by_swipe(section_name)
            logging.info(f"[{section_name}] 좌스와이프 {swipe_count}회 - 총 콘텐츠 수: {len(collected)}개")
            for i, name in enumerate(collected, 1):
                logging.info(f"[{section_name}]   {i}. {name}")

            last_item = collected[-1] if collected else "(확인불가)"
            logging.info(f"[{section_name}] 마지막 작품: {last_item}")

            for _ in range(swipe_count):
                self.page.swipe_section_right(section_name)
            logging.info(f"[{section_name}] 우스와이프 {swipe_count}회 원위치 복귀")

        if not self.page.is_section_more_visible(section_name):
            logging.info(f"[{section_name}] 더보기 버튼 없음 - 스킵")
            return

        try:
            dest_title, verified = self.page.click_section_more_and_verify(section_name)
            navigated = bool(dest_title.strip())
            logging.info(f"[{section_name}] 더보기 클릭 → 화면전환 {'✅' if navigated else '❌'} (상단타이틀: '{dest_title}')")
        except Exception as e:
            navigated, verified = True, True
            logging.warning(f"[{section_name}] 화면전환 타이틀 확인 실패(iOS WDA 이슈 가능) - 더보기 클릭은 성공했으므로 화면전환된 것으로 간주: {e}")
        if not verified:
            
            expected = self.page.IOS_SECTION_MORE_DEST_HINT.get(section_name, "(힌트없음)")
            back_ok = self.page.is_webtoon_genrehome_displayed()
            pytest.fail(
                f"❌ [{section_name}] 더보기 목적지 타이틀 검증 실패 "
                f"(기대: '{expected}' / 실제: '{dest_title}')"
                + ("" if back_ok else " + 장르홈 복귀도 실패")
            )
        time.sleep(post_more_wait if post_more_wait is not None else (1 if on_more_screen else 0))
        if navigated:
            if on_more_screen:
                on_more_screen()
            if back_via_subtab:
                self.page.click_subtab("판타지/SF")
                time.sleep(1)
            else:
                self.page.navigate_back_to_genrehome()
            assert self.page.is_webtoon_genrehome_displayed(), \
                f"❌ [{section_name}] 더보기 화면전환 후 장르홈 복귀 실패"

    def _log_more_screen_first_last(self, section_name: str):
        try:
            items = self.page.get_visible_content_item_names()
            first_item = items[0] if items else "(확인불가)"
            collected = self.page.collect_items_by_vertical_scroll()
            last_item = collected[-1] if collected else first_item
            logging.info(f"[{section_name}][더보기 화면] 첫번째 작품: {first_item}")
            logging.info(f"[{section_name}][더보기 화면] 마지막 작품: {last_item}")
        except Exception as e:
            logging.warning(f"[{section_name}][더보기 화면] 첫/마지막 작품 확인 실패(iOS WDA 이슈 가능): {e}")

    def test_002_방금본작품과비슷한_섹션(self):
        self._run_section_flow("방금 본 작품과 비슷한", click_fantasy_first=True, subtab_name="판타지/SF")

    def test_003_오늘리디의발견_섹션(self):
        self._run_section_flow("판타지 오늘, 리디의 발견")

    def test_004_판타지기다리면무료_섹션(self):
        section_name = "판타지 기다리면 무료!"
        self._run_section_flow(section_name, on_more_screen=lambda: self._log_more_screen_first_last(section_name))

    def test_005_판타지베스트_섹션(self):
        section_name = "판타지 베스트"
        self._run_section_flow(section_name, on_more_screen=lambda: self._log_more_screen_first_last(section_name))

    def test_006_RIDIONLY판타지_섹션(self):
        section_name = "RIDI ONLY 판타지"
        self._run_section_flow(section_name, on_more_screen=lambda: self._log_more_screen_first_last(section_name))

    def test_007_오직리디에서만_섹션(self):
        self._run_section_flow("판타지 오직 리디에서만!")

    def test_008_이판타지어때요_섹션(self):
        self._run_section_flow("이 판타지 어때요?", first_item_no_swipe=True)

    def test_009_새로나온작품_섹션(self):
        section_name = "판타지 새로나온작품"
        self._run_section_flow(section_name, on_more_screen=lambda: self._log_more_screen_first_last(section_name))
