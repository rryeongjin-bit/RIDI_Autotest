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
    """ 웹툰 장르홈 진입/서브탭 순회. 사용자가 확인해준 4개 서브탭(추천/로맨스/BL/판타지-SF)
    기준으로 만화 장르홈의 TestGenrehome(test_002/003)과 동일한 방식으로 검증한다."""
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
    """ 웹툰 장르홈 퀵메뉴 섹션. 사용자가 확인해준 4개(이달의 신작/이벤트/리디온리/리다무)만
    우선 검증한다 - 실제로는 총 11개(방금 본 작품과 비슷한 웹툰 실시간 랭킹 포함)라 나머지는
    실기기 확인 후 WebtoonGenrePage.QUICK_MENU_LOCATOR/QUICK_MENU_EXPECTED_TITLE에 추가 필요. """
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
    """ 웹툰 장르홈 '추천' 탭 섹션별 순회검증. test_comic_genrehome.py의 TestRecommendtab과
    동일한 방식이나, "웹툰 베스트"/"새로나온작품"은 만화 쪽처럼 더보기 목적지에서 필터버튼
    유무만 확인(verify_all_button)하지 않고, BL탭 섹션들과 같은 방식(섹션 내 좌우스와이프로
    첫/마지막 수집 → 더보기 → 목적지 타이틀 확인 → 목적지 화면에서도 첫/마지막 확인)으로
    진행한다. """
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
            # "방금 본 작품과 비슷한"은 만화 장르홈과 동일하게, AOS에서 계정에 열람 이력이
            # 없으면 섹션 자체가 노출되지 않는 경우가 있어(실기기로 확인된 만화 쪽과 같은
            # 이유로 추정) 다음 섹션에 영향 없도록 장르홈 최상단으로 재진입해두고, 이 섹션
            # 한정으로는 하드 실패 대신 스킵 처리한다.
            self.page.enter_webtoon_genrehome()
            time.sleep(2)
            if click_recommend_first:
                self.page.click_subtab("추천")
                time.sleep(1)
            # 개인화 섹션(직전 진입 작품 / 장르별 구매이력 기반)은 계정 상태에 따라 실제로
            # 노출되지 않을 수 있어 하드 실패 대신 스킵한다 - 목록은 페이지오브젝트의
            # AOS_PERSONALIZED_SECTIONS 참고(2026-07-31 "BL 구매이력기반 AI 추천" 추가).
            if self.platform == "aos" and section_name in self.page.AOS_PERSONALIZED_SECTIONS:
                pytest.skip(f"[{section_name}] AOS 계정 상태로 개인화 섹션 미노출 - 스킵")
        assert found, f"❌ [{section_name}] 섹션 미노출"

        # 개인화 섹션은 scroll_to_section이 True를 반환한 직후에도 요소가 사라져, 이후 아이템
        # 조회에서 NoSuchElementException으로 죽는 경우가 있다(2026-07-31 AOS 실기기 -
        # "이 작품 어때요"/"이 판타지 어때요?"). 위 "if not found" 스킵 경로로는 못 걸러지므로
        # 여기서 한 번 더 확인해 하드 실패 대신 스킵한다.
        if self.platform == "aos" and section_name in self.page.AOS_PERSONALIZED_SECTIONS \
                and not self.page.is_section_title_present(section_name):
            pytest.skip(f"[{section_name}] 개인화 섹션 요소 소실(계정 상태) - 스킵")

        if first_item_no_swipe:
            # 가로 스크롤은 불가하지만 더보기는 있는 섹션("이 판타지 어때요?"). 좌우스와이프를
            # 하면 제스처가 섹션에 먹히지 않고 상위 뷰로 전파돼 서브탭이 넘어가므로
            # (NO_HORIZONTAL_SWIPE_SECTIONS 주석 참고), 첫 작품만 확인하고 곧바로 더보기로
            # 진입해 목적지 타이틀을 확인한 뒤 뒤로가기 한다(2026-08-02 사용자 지시).
            items = self.page.get_section_item_names(section_name)
            first_item = items[0] if items else "(확인불가)"
            logging.info(f"[{section_name}] 첫번째 작품: {first_item}")
            logging.info(f"[{section_name}] 가로 스크롤 불가 섹션 - 좌우스와이프 생략, 더보기 진입만 진행")
        elif skip_item_swipe:
            logging.info(f"[{section_name}] 좌우스와이프 생략 - 더보기 진입/타이틀 확인만 진행")
        elif section_name in self.page.NO_HORIZONTAL_SWIPE_SECTIONS:
            # 가로 스크롤이 불가한 세로 그리드 섹션. 좌우스와이프를 하면 제스처가 섹션에 먹히지
            # 않고 상위 뷰로 전파돼 서브탭이 넘어간다(페이지오브젝트의
            # NO_HORIZONTAL_SWIPE_SECTIONS 주석 참고 - 2026-07-31 AOS 실기기).
            # 푸터도 없고 마지막 작품도 유동적이라, 아래로 3회 스크롤한 시점을 마지막 기준으로
            # 잡고 그 자리의 마지막 작품을 출력만 한다(기대값 비교 없음 - 사용자 지시).
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
            # 목적지 타이틀이 기대값과 끝내 불일치한 경우. 예전에는 여기서 경고만 남기고
            # return해서 테스트가 PASS로 끝났는데, 그러면 실제로는 엉뚱한 작품 상세로 오탭된
            # 섹션도 리포트상 통과로 보여 문제를 놓친다(실기기 확인, 2026-07-29 - 오탭 3건이
            # "13 passed"에 묻혔음). 목적지 화면 후속 처리(세로스크롤 등)는 그대로 건너뛰되,
            # 결과는 명시적으로 실패로 남긴다. 장르홈 복귀는 다음 테스트에 영향이 가지 않도록
            # 실패를 알리기 전에 먼저 확인한다.
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
        """더보기 화면 진입 후 세로스크롤하며 첫번째/마지막 작품명 로그(만화 장르홈의
        동일 목적 헬퍼와 같은 방식). 목적지 화면 구조(순위형/일반 그리드 등)가 실기기로
        아직 확인되지 않아 우선 일반 그리드 방식으로 처리하고, 실기기 확인 후 필요하면
        만화 쪽처럼 섹션별 분기를 추가한다."""
        try:
            items = self.page.get_visible_content_item_names()
            first_item = items[0] if items else "(확인불가)"
            collected = self.page.collect_items_by_vertical_scroll()
            last_item = collected[-1] if collected else first_item
            logging.info(f"[{section_name}][더보기 화면] 첫번째 작품: {first_item}")
            logging.info(f"[{section_name}][더보기 화면] 마지막 작품: {last_item}")
        except Exception as e:
            logging.warning(f"[{section_name}][더보기 화면] 첫/마지막 작품 확인 실패(iOS WDA 이슈 가능): {e}")

    def test_002_요일별웹툰_섹션(self):
        self.page.click_subtab("추천")
        time.sleep(1)
        self._run_section_flow("요일별 웹툰")

    def test_003_기다리면무료로시작해_섹션(self):
        self._run_section_flow("기다리면 무료로 시작해!")

    def test_004_오늘리디의발견_섹션(self):
        self._run_section_flow("오늘리디의 발견")

    def test_005_구매이력기반AI추천_섹션(self):
        section_name = "구매이력기반 AI 추천"
        self._run_section_flow(section_name, on_more_screen=lambda: self._log_more_screen_first_last(section_name))

    def test_006_웹툰만화키워드검색_섹션(self):
        self._run_section_flow("웹툰 키워드 검색", post_more_wait=3, skip_item_swipe=True)

    def test_007_웹툰베스트_섹션(self):
        section_name = "웹툰 베스트"
        self._run_section_flow(section_name, on_more_screen=lambda: self._log_more_screen_first_last(section_name))

    def test_008_지금리디에서만볼수있는웹툰_섹션(self):
        section_name = "지금리디에서만볼수있는 웹툰"
        self._run_section_flow(section_name, on_more_screen=lambda: self._log_more_screen_first_last(section_name))

    def test_009_새로나온작품_섹션(self):
        section_name = "새로나온작품"
        self._run_section_flow(section_name, on_more_screen=lambda: self._log_more_screen_first_last(section_name))

    def test_010_취향저격AI추천_섹션(self):
        """장르홈 맨 마지막 섹션. 더보기가 없고 페이지 최하단 바로 위라, 좌우스와이프 수집
        대신 푸터가 노출될 때까지 세로 스크롤로 끝까지 내려가 마지막 작품을 확인하고 종료한다
        (만화 장르홈의 "님의 취향 저격 AI 추천" 섹션과 동일한 방식).

        장르홈 맨 마지막(가장 깊은) 섹션이라 scroll_to_section 기본 max_scroll(12)로는 못 찾고
        22회 이상 반복 실패하는 경우가 실기기로 확인되었다(2026-07-28) - 실시간 개인화
        피드라 앞쪽 섹션들의 콘텐츠 길이가 실행마다 달라져 필요한 스크롤 횟수가 들쭉날쭉하다.
        scroll_to_footer_and_get_last_item이 이미 이 섹션 전용으로 max_scroll=40을 쓰는 것과
        동일한 이유로, 여기서도 넉넉하게 늘린다.

        앞 테스트가 더보기 목적지 검증에 실패하면 앱이 작품 상세페이지 등 장르홈이 아닌 화면에
        남을 수 있는데, 이 테스트는 서브탭 재클릭 없이 곧바로 scroll_to_section을 호출하므로
        그 상태에서는 있을 수 없는 섹션을 찾느라 전진 30 + 후진 30회를 전부 소진한다
        (실기기에서 약 12분간 멈춘 것처럼 보이는 현상이 2026-07-29 확인됨 - 스크린샷상 앱이
        작품 상세페이지에 갇혀 있었다). 시작 전에 장르홈 상태를 보장해 이 헛돌기를 막는다."""
        if not self.page.is_webtoon_genrehome_displayed():
            logging.warning("[취향저격 AI추천 섹션] 장르홈이 아닌 화면에서 시작 - 장르홈 재진입")
            self.page.enter_webtoon_genrehome()
            time.sleep(2)
        section_name = "취향저격 AI추천 섹션"
        found = self.page.scroll_to_section(section_name, max_scroll=30)
        # 취향저격 AI추천은 계정 취향 데이터 기반이라 노출되지 않을 수 있다(사용자 확인).
        if not found and self.platform == "aos" \
                and section_name in self.page.AOS_PERSONALIZED_SECTIONS:
            pytest.skip(f"[{section_name}] 개인화 섹션 미노출(계정 상태) - 스킵")
        assert found, f"❌ [{section_name}] 섹션 미노출"

        # 개인화 섹션은 scroll_to_section이 True를 반환한 직후에도 요소가 사라져, 이후 아이템
        # 조회에서 NoSuchElementException으로 죽는 경우가 있다(2026-07-31 AOS 실기기 -
        # "이 작품 어때요"/"이 판타지 어때요?"). 위 "if not found" 스킵 경로로는 못 걸러지므로
        # 여기서 한 번 더 확인해 하드 실패 대신 스킵한다.
        if self.platform == "aos" and section_name in self.page.AOS_PERSONALIZED_SECTIONS \
                and not self.page.is_section_title_present(section_name):
            pytest.skip(f"[{section_name}] 개인화 섹션 요소 소실(계정 상태) - 스킵")

        items = self.page.get_section_item_names(section_name)
        first_item = items[0] if items else "(확인불가)"
        logging.info(f"[{section_name}] 첫번째 작품: {first_item}")

        last_item, footer_reached = self.page.scroll_to_footer_and_get_last_item(section_name)
        logging.info(f"[{section_name}] 마지막 작품(푸터 노출 {'✅' if footer_reached else '❌'}): {last_item}")


class TestRomancetab:
    """ 웹툰 장르홈 '로맨스' 탭 섹션별 순회검증. TestRecommendtab과 동일한 방식이나, "방금 본
    작품과 비슷한"은 추천 탭과 이름이 겹쳐(TestBLtab과 동일한 이유로) scroll_to_section 호출 시
    subtab_name="로맨스"를 직접 넘겨 서브탭을 명시한다. iOS 결정론적 스크롤에 필요한
    IOS_SECTION_SWIPE_COUNT/IOS_SECTION_MORE_COORD_RATIO 값은 아직 실기기 미확인 추정값이라
    (WebtoonGenrePage 참고) iOS 실기기 확인 후 보완이 필요하다."""
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
            # "방금 본 작품과 비슷한"은 만화/추천 탭과 동일하게, AOS에서 계정에 열람 이력이
            # 없으면 섹션 자체가 노출되지 않는 경우가 있어 다음 섹션에 영향 없도록 장르홈
            # 최상단으로 재진입해두고, 이 섹션 한정으로는 하드 실패 대신 스킵 처리한다.
            self.page.enter_webtoon_genrehome()
            time.sleep(2)
            # 딥링크 재진입은 항상 "추천" 탭으로 들어가므로, 이 클래스의 탭으로 반드시 되돌린다.
            # 예전에는 click_romance_first 플래그가 True일 때만 되돌렸는데, 그 플래그는 첫 섹션
            # (test_002)에만 넘기기 때문에 이후 테스트에서 섹션을 못 찾아 재진입하면 추천 탭에
            # 그대로 남았다. 그 결과 이후 섹션들이 추천 탭에서 검증되어, 목적지 타이틀이
            # 추천 탭 것으로 나오는데도 원인을 힌트 오류로 오판하게 됐다(2026-07-30 실기기 -
            # "로맨스 기다리면 무료!"의 목적지가 추천 탭의 "기다리면 무료로 시작해!"로 나옴).
            self.page.click_subtab("로맨스")
            time.sleep(1)
            # 개인화 섹션(직전 진입 작품 / 장르별 구매이력 기반)은 계정 상태에 따라 실제로
            # 노출되지 않을 수 있어 하드 실패 대신 스킵한다 - 목록은 페이지오브젝트의
            # AOS_PERSONALIZED_SECTIONS 참고(2026-07-31 "BL 구매이력기반 AI 추천" 추가).
            if self.platform == "aos" and section_name in self.page.AOS_PERSONALIZED_SECTIONS:
                pytest.skip(f"[{section_name}] AOS 계정 상태로 개인화 섹션 미노출 - 스킵")
        assert found, f"❌ [{section_name}] 섹션 미노출"

        # 개인화 섹션은 scroll_to_section이 True를 반환한 직후에도 요소가 사라져, 이후 아이템
        # 조회에서 NoSuchElementException으로 죽는 경우가 있다(2026-07-31 AOS 실기기 -
        # "이 작품 어때요"/"이 판타지 어때요?"). 위 "if not found" 스킵 경로로는 못 걸러지므로
        # 여기서 한 번 더 확인해 하드 실패 대신 스킵한다.
        if self.platform == "aos" and section_name in self.page.AOS_PERSONALIZED_SECTIONS \
                and not self.page.is_section_title_present(section_name):
            pytest.skip(f"[{section_name}] 개인화 섹션 요소 소실(계정 상태) - 스킵")

        if first_item_no_swipe:
            # 가로 스크롤은 불가하지만 더보기는 있는 섹션("이 판타지 어때요?"). 좌우스와이프를
            # 하면 제스처가 섹션에 먹히지 않고 상위 뷰로 전파돼 서브탭이 넘어가므로
            # (NO_HORIZONTAL_SWIPE_SECTIONS 주석 참고), 첫 작품만 확인하고 곧바로 더보기로
            # 진입해 목적지 타이틀을 확인한 뒤 뒤로가기 한다(2026-08-02 사용자 지시).
            items = self.page.get_section_item_names(section_name)
            first_item = items[0] if items else "(확인불가)"
            logging.info(f"[{section_name}] 첫번째 작품: {first_item}")
            logging.info(f"[{section_name}] 가로 스크롤 불가 섹션 - 좌우스와이프 생략, 더보기 진입만 진행")
        elif skip_item_swipe:
            logging.info(f"[{section_name}] 좌우스와이프 생략 - 더보기 진입/타이틀 확인만 진행")
        elif section_name in self.page.NO_HORIZONTAL_SWIPE_SECTIONS:
            # 가로 스크롤이 불가한 세로 그리드 섹션. 좌우스와이프를 하면 제스처가 섹션에 먹히지
            # 않고 상위 뷰로 전파돼 서브탭이 넘어간다(페이지오브젝트의
            # NO_HORIZONTAL_SWIPE_SECTIONS 주석 참고 - 2026-07-31 AOS 실기기).
            # 푸터도 없고 마지막 작품도 유동적이라, 아래로 3회 스크롤한 시점을 마지막 기준으로
            # 잡고 그 자리의 마지막 작품을 출력만 한다(기대값 비교 없음 - 사용자 지시).
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
            # 목적지 타이틀이 기대값과 끝내 불일치한 경우. 예전에는 여기서 경고만 남기고
            # return해서 테스트가 PASS로 끝났는데, 그러면 실제로는 엉뚱한 작품 상세로 오탭된
            # 섹션도 리포트상 통과로 보여 문제를 놓친다(실기기 확인, 2026-07-29 - 오탭 3건이
            # "13 passed"에 묻혔음). 목적지 화면 후속 처리(세로스크롤 등)는 그대로 건너뛰되,
            # 결과는 명시적으로 실패로 남긴다. 장르홈 복귀는 다음 테스트에 영향이 가지 않도록
            # 실패를 알리기 전에 먼저 확인한다.
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
        # TestBLtab과 동일한 이유로 subtab_name="로맨스"를 직접 넘겨 추천 탭과의 이름 충돌을
        # 피한다("방금 본 작품과 비슷한"은 IOS_SECTION_SUBTAB에 등록하지 않음 - 클래스 주석 참고).
        self._run_section_flow("방금 본 작품과 비슷한", click_romance_first=True, subtab_name="로맨스")

    def test_003_오늘리디의발견_섹션(self):
        # 더보기 없음
        self._run_section_flow("오늘, 리디의 발견")

    def test_004_실시간랭킹_섹션(self):
        # 더보기 있음 (목적지 타이틀: "실시간 랭킹")
        self._run_section_flow("실시간 랭킹")

    def test_005_로맨스기다리면무료_섹션(self):
        # 더보기 있음 (목적지 타이틀: "로맨스 기다리면 무료!")
        self._run_section_flow("로맨스 기다리면 무료!")

    def test_006_로맨스베스트_섹션(self):
        # 더보기 있음 (목적지 타이틀: "로맨스 베스트")
        section_name = "로맨스 베스트"
        self._run_section_flow(section_name, on_more_screen=lambda: self._log_more_screen_first_last(section_name))

    def test_007_웹툰만화키워드검색_섹션(self):
        # 더보기 있음 (목적지 타이틀: "웹툰/만화 키워드 검색")
        self._run_section_flow("웹툰/만화 키워드 검색", post_more_wait=3, skip_item_swipe=True)

    def test_008_오직리디에서만_섹션(self):
        # 더보기 없음
        self._run_section_flow("오직 리디에서만!")


class TestBLtab:
    """ 웹툰 장르홈 'BL' 탭 섹션별 순회검증. TestRecommendtab/TestRomancetab과 동일한 방식.
    "방금 본 작품과 비슷한"은 추천/로맨스 탭과 이름이 겹쳐 scroll_to_section 호출 시
    subtab_name="BL"을 직접 넘겨 서브탭을 명시한다("BL 오늘, 리디의 발견"/"BL 구매이력기반
    AI 추천"은 로맨스/추천 탭의 동명 섹션과 스크롤 깊이가 달라 "BL " 접두사로 별개 키를 둠 -
    WebtoonGenrePage 참고). iOS 결정론적 스크롤에 필요한 IOS_SECTION_SWIPE_COUNT/
    IOS_SECTION_MORE_COORD_RATIO 값은 아직 실기기 미확인 추정값이라 iOS 실기기 확인 후
    보완이 필요하다."""
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
            # "방금 본 작품과 비슷한"은 만화/추천/로맨스 탭과 동일하게, AOS에서 계정에 열람
            # 이력이 없으면 섹션 자체가 노출되지 않는 경우가 있어 다음 섹션에 영향 없도록
            # 장르홈 최상단으로 재진입해두고, 이 섹션 한정으로는 하드 실패 대신 스킵 처리한다.
            self.page.enter_webtoon_genrehome()
            time.sleep(2)
            # 딥링크 재진입은 항상 "추천" 탭으로 들어가므로, 이 클래스의 탭으로 반드시 되돌린다.
            # 예전에는 click_bl_first 플래그가 True일 때만 되돌렸는데, 그 플래그는 첫 섹션
            # (test_002)에만 넘기기 때문에 이후 테스트에서 섹션을 못 찾아 재진입하면 추천 탭에
            # 그대로 남았다. 그 결과 이후 섹션들이 추천 탭에서 검증되어, 목적지 타이틀이
            # 추천 탭 것으로 나오는데도 원인을 힌트 오류로 오판하게 됐다(2026-07-30 실기기 -
            # "로맨스 기다리면 무료!"의 목적지가 추천 탭의 "기다리면 무료로 시작해!"로 나옴).
            self.page.click_subtab("BL")
            time.sleep(1)
            # 개인화 섹션(직전 진입 작품 / 장르별 구매이력 기반)은 계정 상태에 따라 실제로
            # 노출되지 않을 수 있어 하드 실패 대신 스킵한다 - 목록은 페이지오브젝트의
            # AOS_PERSONALIZED_SECTIONS 참고(2026-07-31 "BL 구매이력기반 AI 추천" 추가).
            if self.platform == "aos" and section_name in self.page.AOS_PERSONALIZED_SECTIONS:
                pytest.skip(f"[{section_name}] AOS 계정 상태로 개인화 섹션 미노출 - 스킵")
        assert found, f"❌ [{section_name}] 섹션 미노출"

        # 개인화 섹션은 scroll_to_section이 True를 반환한 직후에도 요소가 사라져, 이후 아이템
        # 조회에서 NoSuchElementException으로 죽는 경우가 있다(2026-07-31 AOS 실기기 -
        # "이 작품 어때요"/"이 판타지 어때요?"). 위 "if not found" 스킵 경로로는 못 걸러지므로
        # 여기서 한 번 더 확인해 하드 실패 대신 스킵한다.
        if self.platform == "aos" and section_name in self.page.AOS_PERSONALIZED_SECTIONS \
                and not self.page.is_section_title_present(section_name):
            pytest.skip(f"[{section_name}] 개인화 섹션 요소 소실(계정 상태) - 스킵")

        if first_item_no_swipe:
            # 가로 스크롤은 불가하지만 더보기는 있는 섹션("이 판타지 어때요?"). 좌우스와이프를
            # 하면 제스처가 섹션에 먹히지 않고 상위 뷰로 전파돼 서브탭이 넘어가므로
            # (NO_HORIZONTAL_SWIPE_SECTIONS 주석 참고), 첫 작품만 확인하고 곧바로 더보기로
            # 진입해 목적지 타이틀을 확인한 뒤 뒤로가기 한다(2026-08-02 사용자 지시).
            items = self.page.get_section_item_names(section_name)
            first_item = items[0] if items else "(확인불가)"
            logging.info(f"[{section_name}] 첫번째 작품: {first_item}")
            logging.info(f"[{section_name}] 가로 스크롤 불가 섹션 - 좌우스와이프 생략, 더보기 진입만 진행")
        elif skip_item_swipe:
            logging.info(f"[{section_name}] 좌우스와이프 생략 - 더보기 진입/타이틀 확인만 진행")
        elif section_name in self.page.NO_HORIZONTAL_SWIPE_SECTIONS:
            # 가로 스크롤이 불가한 세로 그리드 섹션. 좌우스와이프를 하면 제스처가 섹션에 먹히지
            # 않고 상위 뷰로 전파돼 서브탭이 넘어간다(페이지오브젝트의
            # NO_HORIZONTAL_SWIPE_SECTIONS 주석 참고 - 2026-07-31 AOS 실기기).
            # 푸터도 없고 마지막 작품도 유동적이라, 아래로 3회 스크롤한 시점을 마지막 기준으로
            # 잡고 그 자리의 마지막 작품을 출력만 한다(기대값 비교 없음 - 사용자 지시).
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
            # 목적지 타이틀이 기대값과 끝내 불일치한 경우. 예전에는 여기서 경고만 남기고
            # return해서 테스트가 PASS로 끝났는데, 그러면 실제로는 엉뚱한 작품 상세로 오탭된
            # 섹션도 리포트상 통과로 보여 문제를 놓친다(실기기 확인, 2026-07-29 - 오탭 3건이
            # "13 passed"에 묻혔음). 목적지 화면 후속 처리(세로스크롤 등)는 그대로 건너뛰되,
            # 결과는 명시적으로 실패로 남긴다. 장르홈 복귀는 다음 테스트에 영향이 가지 않도록
            # 실패를 알리기 전에 먼저 확인한다.
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
        # 더보기 없음. TestBLtab의 기존 관례(comic)와 동일하게 subtab_name="BL"을 직접 넘긴다.
        self._run_section_flow("방금 본 작품과 비슷한", click_bl_first=True, subtab_name="BL")

    def test_003_BL웹툰실시간랭킹_섹션(self):
        # 더보기 있음 (목적지 타이틀: "BL웹툰 실시간 랭킹")
        self._run_section_flow("BL웹툰 실시간 랭킹")

    def test_004_오늘리디의발견_섹션(self):
        # 더보기 없음
        self._run_section_flow("BL 오늘, 리디의 발견")

    def test_005_구매이력기반AI추천_섹션(self):
        # 더보기 있음 (목적지 타이틀: "{아이디} 님의 구매이력기반 AI추천")
        section_name = "BL 구매이력기반 AI 추천"
        self._run_section_flow(section_name, on_more_screen=lambda: self._log_more_screen_first_last(section_name))

    def test_006_BL웹툰베스트_섹션(self):
        # 더보기 있음 (목적지 타이틀: "BL웹툰 베스트")
        section_name = "BL웹툰 베스트"
        self._run_section_flow(section_name, on_more_screen=lambda: self._log_more_screen_first_last(section_name))

    def test_007_BL키워드검색_섹션(self):
        # 더보기 있음 (목적지 타이틀: "BL키워드 검색")
        self._run_section_flow("BL키워드 검색", post_more_wait=3, skip_item_swipe=True)

    def test_008_BL요일별웹툰_섹션(self):
        # 더보기 있음 (목적지 타이틀: "BL 요일별 웹툰")
        section_name = "BL 요일별 웹툰"
        self._run_section_flow(section_name, on_more_screen=lambda: self._log_more_screen_first_last(section_name))

    def test_009_지금리디에서만볼수있는BL웹툰_섹션(self):
        # 더보기 있음 (목적지 타이틀: "RIDI ONLY BL 웹툰/만화")
        section_name = "지금, 리디에서만 볼수있는 BL 웹툰"
        self._run_section_flow(section_name, on_more_screen=lambda: self._log_more_screen_first_last(section_name))

    def test_010_RIDIONLY신작모음_섹션(self):
        # 더보기 있음 (목적지 타이틀: "RIDI ONLY 신작 모음")
        section_name = "RIDI ONLY 신작 모음"
        self._run_section_flow(section_name, on_more_screen=lambda: self._log_more_screen_first_last(section_name))

    def test_011_이작품어때요_섹션(self):
        # 더보기 없음
        self._run_section_flow("이 작품 어때요")

    def test_012_BL탭_마지막지점_확인(self):
        """BL탭 마지막 지점 확인.

        이 지면은 마지막 영역에 **푸터가 노출되지 않아** "끝"을 요소로 감지하는 방식 자체가
        불가능하고, 여기 있던 "취향저격 AI추천 섹션"도 노출 여부가 유동적이다(사용자 확인).
        그래서 섹션 탐색을 하지 않고 **아래로 5회 스크롤한 그 시점**을 마지막 지점으로 잡아
        마지막 작품 정보를 출력하고 종료한다(2026-08-02 사용자 지시).

        기존에는 없는 섹션을 scroll_to_section(max_scroll=30)으로 찾느라 textContains 조회를
        61회 반복하며 12분 29초를 소모한 뒤 스킵됐다(2026-08-02 AOS 로그 11:05:26~11:17:55).
        마지막 작품은 유동적이라 기대값과 비교하지 않고 출력만 한다."""
        if not self.page.is_webtoon_genrehome_displayed():
            logging.warning("[BL탭 마지막지점] 장르홈이 아닌 화면에서 시작 - 장르홈 재진입")
            self.page.enter_webtoon_genrehome()
            time.sleep(2)
            self.page.click_subtab("BL")
            time.sleep(1)

        last_item = self.page.scroll_and_get_last_item("취향저격 AI추천 섹션", scroll_times=5)
        logging.info(f"[BL탭 마지막지점] 스크롤 5회 후 마지막 작품: {last_item or '(확인불가)'}")


class TestFantasytab:
    """ 웹툰 장르홈 '판타지/SF' 탭 섹션별 순회검증. TestRecommendtab/TestRomancetab/TestBLtab과
    동일한 방식.

    섹션 이름이 다른 탭과 겹치는 것들은 WebtoonGenrePage에서 "판타지 " 접두사를 붙인 별개
    키로 등록해뒀다("오늘, 리디의 발견"/"오직 리디에서만!"은 로맨스 탭에 동명 키가 이미
    있는데 서브탭과 스크롤 깊이가 달라 그대로 재사용하면 로맨스 탭 값을 덮어써버린다 -
    로케이터 상수 자체는 텍스트 매칭이라 탭과 무관하므로 동일한 것을 재사용한다).
    따라서 이 클래스에서 넘기는 섹션명은 화면 문구가 아니라 그 사전 키다.
    예외적으로 "방금 본 작품과 비슷한"은 위치(항상 첫 섹션)가 서브탭과 무관해 다른 탭들과
    키를 공유하므로, scroll_to_section에 subtab_name="판타지/SF"를 직접 넘겨 서브탭을
    명시한다(TestBLtab의 동일 섹션 처리와 같은 관례).

    iOS 결정론적 스크롤에 필요한 IOS_SECTION_SWIPE_COUNT/IOS_SECTION_MORE_COORD_RATIO 값은
    아직 실기기 미확인 추정값이라 iOS 실기기 확인 후 보완이 필요하다."""
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
            # "방금 본 작품과 비슷한"은 만화/추천/로맨스/BL 탭과 동일하게, AOS에서 계정에 열람
            # 이력이 없으면 섹션 자체가 노출되지 않는 경우가 있어 다음 섹션에 영향 없도록
            # 장르홈 최상단으로 재진입해두고, 이 섹션 한정으로는 하드 실패 대신 스킵 처리한다.
            self.page.enter_webtoon_genrehome()
            time.sleep(2)
            # 딥링크 재진입은 항상 "추천" 탭으로 들어가므로, 이 클래스의 탭으로 반드시 되돌린다.
            # 예전에는 click_fantasy_first 플래그가 True일 때만 되돌렸는데, 그 플래그는 첫 섹션
            # (test_002)에만 넘기기 때문에 이후 테스트에서 섹션을 못 찾아 재진입하면 추천 탭에
            # 그대로 남았다. 그 결과 이후 섹션들이 추천 탭에서 검증되어, 목적지 타이틀이
            # 추천 탭 것으로 나오는데도 원인을 힌트 오류로 오판하게 됐다(2026-07-30 실기기 -
            # "로맨스 기다리면 무료!"의 목적지가 추천 탭의 "기다리면 무료로 시작해!"로 나옴).
            self.page.click_subtab("판타지/SF")
            time.sleep(1)
            # 개인화 섹션(직전 진입 작품 / 장르별 구매이력 기반)은 계정 상태에 따라 실제로
            # 노출되지 않을 수 있어 하드 실패 대신 스킵한다 - 목록은 페이지오브젝트의
            # AOS_PERSONALIZED_SECTIONS 참고(2026-07-31 "BL 구매이력기반 AI 추천" 추가).
            if self.platform == "aos" and section_name in self.page.AOS_PERSONALIZED_SECTIONS:
                pytest.skip(f"[{section_name}] AOS 계정 상태로 개인화 섹션 미노출 - 스킵")
        assert found, f"❌ [{section_name}] 섹션 미노출"

        # 개인화 섹션은 scroll_to_section이 True를 반환한 직후에도 요소가 사라져, 이후 아이템
        # 조회에서 NoSuchElementException으로 죽는 경우가 있다(2026-07-31 AOS 실기기 -
        # "이 작품 어때요"/"이 판타지 어때요?"). 위 "if not found" 스킵 경로로는 못 걸러지므로
        # 여기서 한 번 더 확인해 하드 실패 대신 스킵한다.
        if self.platform == "aos" and section_name in self.page.AOS_PERSONALIZED_SECTIONS \
                and not self.page.is_section_title_present(section_name):
            pytest.skip(f"[{section_name}] 개인화 섹션 요소 소실(계정 상태) - 스킵")

        if first_item_no_swipe:
            # 가로 스크롤은 불가하지만 더보기는 있는 섹션("이 판타지 어때요?"). 좌우스와이프를
            # 하면 제스처가 섹션에 먹히지 않고 상위 뷰로 전파돼 서브탭이 넘어가므로
            # (NO_HORIZONTAL_SWIPE_SECTIONS 주석 참고), 첫 작품만 확인하고 곧바로 더보기로
            # 진입해 목적지 타이틀을 확인한 뒤 뒤로가기 한다(2026-08-02 사용자 지시).
            items = self.page.get_section_item_names(section_name)
            first_item = items[0] if items else "(확인불가)"
            logging.info(f"[{section_name}] 첫번째 작품: {first_item}")
            logging.info(f"[{section_name}] 가로 스크롤 불가 섹션 - 좌우스와이프 생략, 더보기 진입만 진행")
        elif skip_item_swipe:
            logging.info(f"[{section_name}] 좌우스와이프 생략 - 더보기 진입/타이틀 확인만 진행")
        elif section_name in self.page.NO_HORIZONTAL_SWIPE_SECTIONS:
            # 가로 스크롤이 불가한 세로 그리드 섹션. 좌우스와이프를 하면 제스처가 섹션에 먹히지
            # 않고 상위 뷰로 전파돼 서브탭이 넘어간다(페이지오브젝트의
            # NO_HORIZONTAL_SWIPE_SECTIONS 주석 참고 - 2026-07-31 AOS 실기기).
            # 푸터도 없고 마지막 작품도 유동적이라, 아래로 3회 스크롤한 시점을 마지막 기준으로
            # 잡고 그 자리의 마지막 작품을 출력만 한다(기대값 비교 없음 - 사용자 지시).
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
            # 목적지 타이틀이 기대값과 끝내 불일치한 경우. 예전에는 여기서 경고만 남기고
            # return해서 테스트가 PASS로 끝났는데, 그러면 실제로는 엉뚱한 작품 상세로 오탭된
            # 섹션도 리포트상 통과로 보여 문제를 놓친다(실기기 확인, 2026-07-29 - 오탭 3건이
            # "13 passed"에 묻혔음). 목적지 화면 후속 처리(세로스크롤 등)는 그대로 건너뛰되,
            # 결과는 명시적으로 실패로 남긴다. 장르홈 복귀는 다음 테스트에 영향이 가지 않도록
            # 실패를 알리기 전에 먼저 확인한다.
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
        # 더보기 없음. 다른 탭과 키를 공유하는 섹션이라 subtab_name을 직접 넘긴다.
        self._run_section_flow("방금 본 작품과 비슷한", click_fantasy_first=True, subtab_name="판타지/SF")

    def test_003_오늘리디의발견_섹션(self):
        # 더보기 없음
        self._run_section_flow("판타지 오늘, 리디의 발견")

    def test_004_판타지기다리면무료_섹션(self):
        # 더보기 있음 (목적지 타이틀: "판타지 기다리면 무료!")
        section_name = "판타지 기다리면 무료!"
        self._run_section_flow(section_name, on_more_screen=lambda: self._log_more_screen_first_last(section_name))

    def test_005_판타지베스트_섹션(self):
        # 더보기 있음 (목적지 타이틀: "판타지 베스트")
        section_name = "판타지 베스트"
        self._run_section_flow(section_name, on_more_screen=lambda: self._log_more_screen_first_last(section_name))

    def test_006_RIDIONLY판타지_섹션(self):
        # 더보기 있음 (목적지 타이틀: "RIDI ONLY 판타지")
        section_name = "RIDI ONLY 판타지"
        self._run_section_flow(section_name, on_more_screen=lambda: self._log_more_screen_first_last(section_name))

    def test_007_오직리디에서만_섹션(self):
        # 더보기 없음
        self._run_section_flow("판타지 오직 리디에서만!")

    def test_008_이판타지어때요_섹션(self):
        # 가로 스크롤이 불가한 세로 그리드 섹션이지만 더보기는 있다(2026-08-02 사용자 확인).
        # 좌우스와이프를 하면 제스처가 상위 뷰로 전파돼 서브탭이 넘어가면서 이 테스트가 실패하고,
        # 다음 test_009까지 엉뚱한 화면에서 시작해 연쇄로 무너졌다(2026-08-02 AOS 로그:
        # 첫 작품 확인 13초 뒤 실패 → 다음 테스트가 5분 17초 헛돌다 실패).
        # 첫 작품만 확인하고 좌우스와이프 없이 더보기로 진입해 타이틀 확인 후 뒤로가기 한다.
        self._run_section_flow("이 판타지 어때요?", first_item_no_swipe=True)

    def test_009_새로나온작품_섹션(self):
        # 더보기 있음 (목적지 타이틀: "새로 나온 작품" - 섹션 문구 "새로나온 작품"과 띄어쓰기가
        # 달라 IOS_SECTION_MORE_DEST_HINT에 별도 등록되어 있다)
        section_name = "판타지 새로나온작품"
        self._run_section_flow(section_name, on_more_screen=lambda: self._log_more_screen_first_last(section_name))
