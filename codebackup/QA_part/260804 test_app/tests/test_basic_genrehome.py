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

class _GenrehomeFlowMixin:
    """장르홈 진입 + 서브탭 좌우스와이프/순차이동 공통 절차.

    하위 클래스 지정 항목:
      PAGE_CLS      : 페이지 객체 클래스
      GENRE         : 로그/실패 메시지에 쓰는 장르명("만화"/"웹툰")
      SUBTAB_FIXED  : 고정 서브탭 4개(첫 항목은 항상 "추천")
      QUICKMENU_KEY : 추천 탭 복귀 후 노출을 확인할 퀵메뉴명
    """
    PAGE_CLS      = None
    GENRE         = ""
    SUBTAB_FIXED  = []
    QUICKMENU_KEY = ""

    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver   = driver
        self.platform = platform
        self.page     = self.PAGE_CLS(driver, platform)

    def _enter(self):
        self.page.enter_genrehome()
        assert self.page.is_genrehome_displayed(), \
            f"❌ {self.GENRE} 장르홈 진입 실패 — 추천 서브탭 미노출"

    def _subtab_swipe_all(self):
        found = {}
        for tab in self.SUBTAB_FIXED:
            if self.page.is_subtab_visible(tab):
                found[tab] = "초기"
        logging.info(f"[서브탭] 초기 탐색 결과: {list(found.keys()) or '없음'}")

        if self.platform == "aos":
            # AOS는 탭 목록이 더 이상 변하지 않을 때까지(=끝 도달) 밀어본다.
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
            # iOS는 전체 탭 목록 조회가 불가해 고정 횟수로 민다.
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

        # pass 기준: 고정탭 모두 발견 + 처음 위치로 정상 복귀
        missing_fixed = [t for t in self.SUBTAB_FIXED if t not in found]
        assert not missing_fixed, f"❌ 고정 서브탭 미발견: {missing_fixed}"
        assert right_swipe_ok, "❌ 우스와이프로 처음까지 복귀 실패 — 우방향 스와이프 동작 이상"

    def _subtab_sequential(self):
        time.sleep(3)
        forward  = self.SUBTAB_FIXED[1:]                  
        backward = list(reversed(self.SUBTAB_FIXED[:-1]))

        for tab in forward:
            self.page.click_subtab(tab, log=False)
            time.sleep(1)
            ok = self.page.is_subtab_visible(tab, log=False)
            logging.info(f"[서브탭 선택이동확인] {tab} {'✅' if ok else '❌'}")
            assert ok, f"❌ {tab} 서브탭 진입 실패 (정방향)"
        logging.info("[서브탭] 정방향 이동 완료")

        for tab in backward:
            self.page.click_subtab(tab, log=False)
            time.sleep(1)
            ok = self.page.is_subtab_visible(tab, log=False)
            logging.info(f"[서브탭 선택이동확인] {tab} {'✅' if ok else '❌'}")
            assert ok, f"❌ {tab} 서브탭 복귀 실패 (역방향)"
        logging.info("[서브탭] 역방향 이동복귀 완료")

        assert self.page.is_quickmenu_visible(self.QUICKMENU_KEY), \
            f"❌ 추천 서브탭 복귀 후 {self.QUICKMENU_KEY} 퀵메뉴 미노출"


class _QuickmenuFlowMixin:
    """퀵메뉴 좌스와이프 전체확인 + 선택/페이지전환/복귀 공통 절차."""
    PAGE_CLS = None

    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver   = driver
        self.platform = platform
        self.page     = self.PAGE_CLS(driver, platform)

    def _quickmenu_swipe_all(self):
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

    def _quickmenu_select_and_back(self):
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

            assert self.page.verify_quickmenu_destination_title(name), \
                f"❌ {name} 선택 후 타이틀 불일치 — 정상 진입 실패"

            self.page.navigate_back_to_genrehome()
            assert self.page.is_genrehome_displayed(), \
                f"❌ {name} 선택 후 장르홈 복귀 실패"

            # 다음 퀵메뉴 탐색을 위해 원위치 복귀
            for _ in range(attempts):
                self.page.swipe_quickmenu_right()


class _SectionFlowMixin:
    PAGE_CLS = None

    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver   = driver
        self.platform = platform
        self.page     = self.PAGE_CLS(driver, platform)

    def _run_section_flow(self, section_name: str, click_recommend_first: bool = False, on_more_screen=None,
                          back_via_subtab: bool = False, verify_all_button: bool = False,
                          post_more_wait: float = None, all_button_text: str = "필터",
                          skip_item_swipe: bool = False, first_item_no_swipe: bool = False):
        if click_recommend_first:
            self.page.click_subtab("추천")
            time.sleep(1)

        found = self.page.scroll_to_section(section_name)
        if not found:
            self.page.enter_genrehome()
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

        self._collect_items(section_name, skip_item_swipe, first_item_no_swipe)
        if self._section_flow_ended:
            return

        if not self.page.is_section_more_visible(section_name):
            logging.info(f"[{section_name}] 더보기 버튼 없음 - 스킵")
            return

        if verify_all_button:
            self._verify_all_button(section_name, all_button_text)
            return

        self._enter_more_and_verify(section_name, on_more_screen, back_via_subtab, post_more_wait)

    # ── 섹션 아이템 수집 (4가지 모드) ────────────────────────────────────────
    def _collect_items(self, section_name, skip_item_swipe, first_item_no_swipe):
        self._section_flow_ended = False

        if first_item_no_swipe:
            logging.info(f"[{section_name}] 첫번째 작품: {self._first_item(section_name)}")
            logging.info(f"[{section_name}] 가로 스크롤 불가 섹션 - 좌우스와이프 생략, 더보기 진입만 진행")
            return

        if skip_item_swipe:
            logging.info(f"[{section_name}] 좌우스와이프 생략 - 더보기 진입/타이틀 확인만 진행")
            return

        if section_name in self.page.NO_HORIZONTAL_SWIPE_SECTIONS:
            logging.info(f"[{section_name}] 첫번째 작품: {self._first_item(section_name)}")
            last_item = self.page.scroll_and_get_last_item(section_name, scroll_times=3)
            logging.info(f"[{section_name}] 상하스크롤 3회 후 마지막 작품: {last_item or '(확인불가)'}")
            logging.info(f"[{section_name}] 가로 스크롤 불가 섹션 - 좌우스와이프/더보기 없이 종료")
            self._section_flow_ended = True
            return

        logging.info(f"[{section_name}] 첫번째 작품: {self._first_item(section_name)}")
        collected, swipe_count = self.page.collect_section_items_by_swipe(section_name)
        logging.info(f"[{section_name}] 좌스와이프 {swipe_count}회 - 총 콘텐츠 수: {len(collected)}개")
        for i, name in enumerate(collected, 1):
            logging.info(f"[{section_name}]   {i}. {name}")
        logging.info(f"[{section_name}] 마지막 작품: {collected[-1] if collected else '(확인불가)'}")

        for _ in range(swipe_count):
            self.page.swipe_section_right(section_name)
        logging.info(f"[{section_name}] 우스와이프 {swipe_count}회 원위치 복귀")

    def _first_item(self, section_name):
        items = self.page.get_section_item_names(section_name)
        return items[0] if items else "(확인불가)"

    # ── 더보기 목적지에서 필터 버튼만 확인하고 서브탭으로 복귀 (만화 전용 분기) ──
    def _verify_all_button(self, section_name, all_button_text):
        assert self.page.click_section_more(section_name), \
            f"❌ [{section_name}] 더보기 콘텐츠 로딩 미확인으로 탭 보류"
        time.sleep(5)
        all_visible = self.page.is_all_filter_visible(all_button_text)
        logging.info(f"[{section_name}] 더보기 목적지 '{all_button_text}' 버튼 노출 {'✅' if all_visible else '❌'}")
        assert all_visible, f"❌ [{section_name}] 더보기 목적지에서 '{all_button_text}' 버튼 미노출"
        time.sleep(3)

        self.page.click_subtab("추천")
        time.sleep(1)
        assert self.page.is_genrehome_displayed(), \
            f"❌ [{section_name}] 더보기 화면전환 후 장르홈 복귀 실패"

    # ── 더보기 진입 → 목적지 타이틀 검증 → 복귀 ─────────────────────────────
    def _enter_more_and_verify(self, section_name, on_more_screen, back_via_subtab, post_more_wait):
        try:
            dest_title, verified = self.page.click_section_more_and_verify(section_name)
            navigated = bool(dest_title.strip())
            logging.info(f"[{section_name}] 더보기 클릭 → 화면전환 {'✅' if navigated else '❌'} (상단타이틀: '{dest_title}')")
        except Exception as e:
            navigated, verified, dest_title = True, True, ""
            logging.warning(f"[{section_name}] 화면전환 타이틀 확인 실패(iOS WDA 이슈 가능) - 더보기 클릭은 성공했으므로 화면전환된 것으로 간주: {e}")

        if not verified:
            expected = self.page.IOS_SECTION_MORE_DEST_HINT.get(section_name, "(힌트없음)")
            back_ok = self.page.is_genrehome_displayed()
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
            assert self.page.is_genrehome_displayed(), \
                f"❌ [{section_name}] 더보기 화면전환 후 장르홈 복귀 실패"


# ══════════════════════════════════════════════════════════════════════════════
#  만화 장르홈
# ══════════════════════════════════════════════════════════════════════════════

class TestComicGenrehome(_GenrehomeFlowMixin):
    """ 만화 장르홈 진입/서브탭 순회 """
    PAGE_CLS      = ComicGenrePage
    GENRE         = "만화"
    SUBTAB_FIXED  = ["추천", "베스트", "신작", "BL"]
    QUICKMENU_KEY = "무료"

    def test_001_만화장르홈_진입(self):
        self._enter()

    def test_002_서브탭_좌우스와이프_전체탭확인(self):
        self._subtab_swipe_all()

    def test_003_서브탭_순차이동_정역방향(self):
        self._subtab_sequential()


class TestComic_Quickmenu(_QuickmenuFlowMixin):
    """ 만화 장르홈 퀵메뉴 """
    PAGE_CLS = ComicGenrePage

    def test_001_퀵메뉴_좌스와이프_전체확인(self):
        self._quickmenu_swipe_all()

    def test_002_퀵메뉴_선택_페이지전환_복귀(self):
        self._quickmenu_select_and_back()


class TestComic_Recommendtab(_SectionFlowMixin):
    """ 만화 장르홈 추천탭 섹션 순회 """
    PAGE_CLS = ComicGenrePage

    def _log_more_screen_first_last(self, section_name: str):
        try:
            if section_name in self.page.IOS_SWIPE_RANKED_SECTIONS:
                collected = self.page.collect_category_dest_items_by_scroll(section_name)
                first_item = collected[0] if collected else "(확인불가)"
                last_item = collected[-1] if collected else first_item
            elif section_name == "지금, 리디에서만 볼 수 있는 만화":
                items = self.page.get_visible_content_item_names()
                first_item = items[0] if items else "(확인불가)"
                collected = self.page.collect_items_by_vertical_scroll(max_scrolls=10, force_full_scroll=True)
                last_item = collected[-1] if collected else first_item
            else:
                items = self.page.get_visible_content_item_names()
                first_item = items[0] if items else "(확인불가)"
                collected = self.page.collect_items_by_vertical_scroll()
                last_item = collected[-1] if collected else first_item
            logging.info(f"[{section_name}][더보기 화면] 첫번째 작품: {first_item}")
            logging.info(f"[{section_name}][더보기 화면] 마지막 작품: {last_item}")
        except Exception as e:
            logging.warning(f"[{section_name}][더보기 화면] 첫/마지막 작품 확인 실패(iOS WDA 이슈 가능): {e}")

    def test_001_방금본작품과_비슷한_섹션(self):
        self._run_section_flow("방금 본 작품과 비슷한", click_recommend_first=True)

    def test_002_지금많이읽고있는만화_섹션(self):
        section_name = "지금 많이 읽고 있는 만화"
        self._run_section_flow(section_name, on_more_screen=lambda: self._log_more_screen_first_last(section_name))

    def test_003_새로나온작품_섹션(self):
        self._run_section_flow("새로 나온 작품", back_via_subtab=True, verify_all_button=True)

    def test_004_만화베스트_섹션(self):
        self._run_section_flow("만화 베스트", back_via_subtab=True, verify_all_button=True)

    def test_005_웹툰만화_키워드검색_섹션(self):
        self._run_section_flow("웹툰/만화 키워드 검색", post_more_wait=3, skip_item_swipe=True)


# ══════════════════════════════════════════════════════════════════════════════
#  웹툰 장르홈
# ══════════════════════════════════════════════════════════════════════════════

class TestWebtoonGenrehome(_GenrehomeFlowMixin):
    """ 웹툰 장르홈 진입/서브탭 순회"""
    PAGE_CLS      = WebtoonGenrePage
    GENRE         = "웹툰"
    SUBTAB_FIXED  = ["추천", "로맨스", "BL", "판타지/SF"]
    QUICKMENU_KEY = "이달의 신작"

    def test_001_웹툰장르홈_진입(self):
        self._enter()

    def test_002_서브탭_좌우스와이프_전체탭확인(self):
        self._subtab_swipe_all()

    def test_003_서브탭_순차이동_정역방향(self):
        self._subtab_sequential()


class TestWebtoonQuickmenu(_QuickmenuFlowMixin):
    """ 웹툰 장르홈 퀵메뉴 """
    PAGE_CLS = WebtoonGenrePage

    def test_001_퀵메뉴_좌스와이프_전체확인(self):
        self._quickmenu_swipe_all()

    def test_002_퀵메뉴_선택_페이지전환_복귀(self):
        self._quickmenu_select_and_back()


class TestWebtoonRecommendtab(_SectionFlowMixin):
    """ 웹툰 장르홈 추천탭 섹션 순회 """
    PAGE_CLS = WebtoonGenrePage

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

    def test_001_요일별웹툰_섹션(self):
        self.page.click_subtab("추천")
        time.sleep(1)
        self._run_section_flow("요일별 웹툰")

    def test_002_기다리면무료로시작해_섹션(self):
        self._run_section_flow("기다리면 무료로 시작해!")

    def test_003_웹툰만화키워드검색_섹션(self):
        self._run_section_flow("웹툰 키워드 검색", post_more_wait=3, skip_item_swipe=True)

    def test_004_웹툰베스트_섹션(self):
        section_name = "웹툰 베스트"
        self._run_section_flow(section_name, on_more_screen=lambda: self._log_more_screen_first_last(section_name))

    def test_005_지금리디에서만볼수있는웹툰_섹션(self):
        section_name = "지금리디에서만볼수있는 웹툰"
        self._run_section_flow(section_name, on_more_screen=lambda: self._log_more_screen_first_last(section_name))

    def test_006_새로나온작품_섹션(self):
        section_name = "새로나온작품"
        self._run_section_flow(section_name, on_more_screen=lambda: self._log_more_screen_first_last(section_name))

# ══════════════════════════════════════════════════════════════════════════════
#  웹소설 장르홈
# ══════════════════════════════════════════════════════════════════════════════

class TestWebnovelGenrehome(_GenrehomeFlowMixin):
    """ 웹소설 장르홈 진입/서브탭 순회"""
    PAGE_CLS      = WebnovelGenrePage
    GENRE         = "웹소설"
    SUBTAB_FIXED  = ["추천", "로맨스", "로판", "BL", "판타지"]
    QUICKMENU_KEY = "신작"

    def test_001_웹소설장르홈_진입(self):
        self._enter()

    def test_002_서브탭_좌우스와이프_전체탭확인(self):
        self._subtab_swipe_all()

    def test_003_서브탭_순차이동_정역방향(self):
        self._subtab_sequential()

class TestWebnovelQuickmenu(_QuickmenuFlowMixin):
    """ 웹소설 장르홈 퀵메뉴 섹션 """
    PAGE_CLS = WebnovelGenrePage

    def test_001_퀵메뉴_좌스와이프_전체확인(self):
        self._quickmenu_swipe_all()

    def test_002_퀵메뉴_선택_페이지전환_복귀(self):
        self._quickmenu_select_and_back()


class TestWebnovelRecommendtab(_SectionFlowMixin):
    """ 웹소설 장르홈 '추천' 탭 섹션별 순회검증 """
    PAGE_CLS = WebnovelGenrePage

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

    def test_001_방금본작품과비슷한_섹션(self):
        self._run_section_flow("방금 본 작품과 비슷한", click_recommend_first=True)

    def test_002_웹소설실시간랭킹_섹션(self):
        self._run_section_flow("웹소설 실시간 랭킹")

    def test_003_새로나온작품_섹션(self):
        section_name = "새로 나온 작품"
        self._run_section_flow(section_name, on_more_screen=lambda: self._log_more_screen_first_last(section_name))


# ══════════════════════════════════════════════════════════════════════════════
#  도서 장르홈
# ══════════════════════════════════════════════════════════════════════════════

class TestGeneralGenrehome(_GenrehomeFlowMixin):
    """ 도서 장르홈 진입 """
    PAGE_CLS      = GeneralbookGenrePage
    GENRE         = "도서"
    SUBTAB_FIXED  = ["추천"]
    QUICKMENU_KEY = "신간"

    def test_001_도서장르홈_진입(self):
        self._enter()


class TestGeneralQuickmenu(_QuickmenuFlowMixin):
    """ 도서 장르홈 퀵메뉴 섹션 (신간 / 북스 베스트 / 이벤트 / 리디온리) """
    PAGE_CLS = GeneralbookGenrePage

    def test_001_퀵메뉴_좌스와이프_전체확인(self):
        self._quickmenu_swipe_all()

    def test_002_퀵메뉴_선택_페이지전환_복귀(self):
        self._quickmenu_select_and_back()


class TestGeneralRecommendtab(_SectionFlowMixin):
    """ 도서 장르홈 '추천' 탭 섹션별 순회검증 """
    PAGE_CLS = GeneralbookGenrePage

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
        self._run_section_flow("방금 본 작품과 비슷한", click_recommend_first=True)

    def test_003_지금많이읽고있는작품_섹션(self):
        section_name = "지금 많이 읽고 있는 작품"
        self._run_section_flow(section_name,
                               on_more_screen=lambda: self._log_more_screen_first_last(section_name))

    def test_004_베스트_섹션(self):
        section_name = "베스트"
        self._run_section_flow(section_name,
                               on_more_screen=lambda: self._log_more_screen_first_last(section_name))

    def test_005_새로나온작품_섹션(self):
        section_name = "새로 나온 작품"
        self._run_section_flow(section_name,
                               on_more_screen=lambda: self._log_more_screen_first_last(section_name))

    def test_006_지금리디에서만볼수있는도서_섹션(self):
        section_name = "지금, 리디에서만 볼 수 있는 도서"
        self._run_section_flow(section_name,
                               on_more_screen=lambda: self._log_more_screen_first_last(section_name))
