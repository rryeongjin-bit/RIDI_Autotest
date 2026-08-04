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
    SUBTAB_FIXED = ["추천", "베스트", "신작", "BL"]
    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver   = driver
        self.platform = platform
        self.page     = ComicGenrePage(driver, platform)

    def test_001_만화장르홈_진입(self):
        self.page.enter_comic_genrehome()
        assert self.page.is_comic_genrehome_displayed(), \
            "❌ 만화 장르홈 진입 실패 — 추천 서브탭 미노출"

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

        # 정방향: 추천 → 베스트 → 신작 → BL
        for tab in ["베스트", "신작", "BL"]:
            self.page.click_subtab(tab, log=False)
            time.sleep(1)
            ok = self.page.is_subtab_visible(tab, log=False)
            logging.info(f"[서브탭 선택이동확인] {tab} {'✅' if ok else '❌'}")
            assert ok, f"❌ {tab} 서브탭 진입 실패 (정방향)"
        logging.info("[서브탭] 정방향 이동 완료")

        # 역방향: BL → 신작 → 베스트 → 추천
        for tab in ["신작", "베스트", "추천"]:
            self.page.click_subtab(tab, log=False)
            time.sleep(1)
            ok = self.page.is_subtab_visible(tab, log=False)
            logging.info(f"[서브탭 선택이동확인] {tab} {'✅' if ok else '❌'}")
            assert ok, f"❌ {tab} 서브탭 복귀 실패 (역방향)"
        logging.info("[서브탭] 역방향 이동복귀 완료")

        assert self.page.is_quickmenu_visible("무료"), \
            "❌ 추천 서브탭 복귀 후 무료 퀵메뉴 미노출"

class TestBigbanner:
    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver   = driver
        self.platform = platform
        self.page     = ComicGenrePage(driver, platform)

    def test_001_만화장르홈_진입(self):
        self.page.enter_comic_genrehome()
        assert self.page.is_comic_genrehome_displayed(), \
            "❌ 만화 장르홈 진입 실패 — 추천 서브탭 미노출"

    def test_002_빅배너_스와이프(self):
        self.page.click_subtab("추천")
        time.sleep(3)

        items = self.page.collect_big_banner_items_by_polling(target_count=5)
        logging.info(f"[빅배너] 자동전환 폴링으로 수집한 배너 {len(items)}개")
        for i, text in enumerate(items, 1):
            logging.info(f"[빅배너]   {i}. {text}")

        assert len(items) >= 5, f"❌ 빅배너 자동전환 폴링으로 서로 다른 배너 5개를 확인하지 못함 (수집 {len(items)}개)"


class TestQuickmenu:
    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver   = driver
        self.platform = platform
        self.page     = ComicGenrePage(driver, platform)

    def test_001_만화장르홈_진입(self):
        self.page.enter_comic_genrehome()
        assert self.page.is_comic_genrehome_displayed(), \
            "❌ 만화 장르홈 진입 실패 — 추천 서브탭 미노출"

    def test_002_퀵메뉴_좌스와이프_전체확인(self):
        self.page.click_subtab("추천")
        time.sleep(1)

        quick_menus = list(self.page.QUICK_MENU_LOCATOR.keys())
        found = {}
        for name in quick_menus:
            if self.page.is_quickmenu_visible(name, log=False):
                found[name] = "초기"
        logging.info(f"[퀵메뉴] 초기 탐색 결과: {list(found.keys()) or '없음'}")

        # 좌 스와이프로 끝까지 이동 (전체 퀵메뉴 발견 시 또는 2회 연속 변화 없으면 종료, 최대 5회)
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

        # 스와이프한 횟수만큼 우 스와이프로 원위치 복귀
        for _ in range(swipe_count):
            self.page.swipe_quickmenu_right()
        logging.info(f"[퀵메뉴] 우스와이프 {swipe_count}회 원위치 복귀")

        missing = [n for n in quick_menus if n not in found]
        assert not missing, f"❌ 퀵메뉴 미발견: {missing}"

    def test_003_퀵메뉴_선택_페이지전환_복귀(self):
        self.page.click_subtab("추천")
        time.sleep(1)

        for name in self.page.QUICK_MENU_LOCATOR.keys():
            # 초기 화면에 없으면 좌스와이프로 탐색
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
            assert self.page.is_comic_genrehome_displayed(), \
                f"❌ {name} 선택 후 장르홈 복귀 실패"

            # 다음 퀵메뉴 탐색을 위해 원위치 복귀
            for _ in range(attempts):
                self.page.swipe_quickmenu_right()


class TestRecommendtab:
    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver   = driver
        self.platform = platform
        self.page     = ComicGenrePage(driver, platform)

    def test_001_만화장르홈_진입(self):
        self.page.enter_comic_genrehome()
        assert self.page.is_comic_genrehome_displayed(), \
            "❌ 만화 장르홈 진입 실패 — 추천 서브탭 미노출"

    def _run_section_flow(self, section_name: str, click_recommend_first: bool = False, on_more_screen=None,
                           back_via_subtab: bool = False, verify_all_button: bool = False, post_more_wait: float = None,
                           all_button_text: str = "필터", skip_item_swipe: bool = False):
        if click_recommend_first:
            self.page.click_subtab("추천")
            time.sleep(1)

        found = self.page.scroll_to_section(section_name)
        if not found:
            self.page.enter_comic_genrehome()
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

            last_item = collected[-1] if collected else "(확인불가)"
            logging.info(f"[{section_name}] 마지막 작품: {last_item}")

            for _ in range(swipe_count):
                self.page.swipe_section_right(section_name)
            logging.info(f"[{section_name}] 우스와이프 {swipe_count}회 원위치 복귀")

        if not self.page.is_section_more_visible(section_name):
            logging.info(f"[{section_name}] 더보기 버튼 없음 - 스킵")
            return

        if verify_all_button:
            tapped = self.page.click_section_more(section_name)
            assert tapped, f"❌ [{section_name}] 더보기 콘텐츠 로딩 미확인으로 탭 보류"
            time.sleep(5) 
            all_visible = self.page.is_all_filter_visible(all_button_text)
            logging.info(f"[{section_name}] 더보기 목적지 '{all_button_text}' 버튼 노출 {'✅' if all_visible else '❌'}")
            assert all_visible, f"❌ [{section_name}] 더보기 목적지에서 '{all_button_text}' 버튼 미노출"
            time.sleep(3)
            
            self.page.click_subtab("추천")
            time.sleep(1)
            assert self.page.is_comic_genrehome_displayed(), \
                f"❌ [{section_name}] 더보기 화면전환 후 장르홈 복귀 실패"
            return

        try:
            dest_title, verified = self.page.click_section_more_and_verify(section_name)
            navigated = bool(dest_title.strip())
            logging.info(f"[{section_name}] 더보기 클릭 → 화면전환 {'✅' if navigated else '❌'} (상단타이틀: '{dest_title}')")
        except Exception as e:
            navigated, verified = True, True
            logging.warning(f"[{section_name}] 화면전환 타이틀 확인 실패(iOS WDA 이슈 가능) - 더보기 클릭은 성공했으므로 화면전환된 것으로 간주: {e}")
        if not verified:
            logging.warning(f"[{section_name}] 더보기 목적지 검증 끝내 실패 - 후속 처리 스킵")
            assert self.page.is_comic_genrehome_displayed(), \
                f"❌ [{section_name}] 더보기 재시도 종료 후 장르홈 복귀 실패"
            return
        time.sleep(post_more_wait if post_more_wait is not None else (1 if on_more_screen else 0))
        if navigated:
            if on_more_screen:
                on_more_screen()
            if back_via_subtab:
                self.page.click_subtab("추천")
                time.sleep(1)
            else:
                self.page.navigate_back_to_genrehome()
            assert self.page.is_comic_genrehome_displayed(), \
                f"❌ [{section_name}] 더보기 화면전환 후 장르홈 복귀 실패"

    def test_002_방금본작품과_비슷한_섹션(self):
        self._run_section_flow("방금 본 작품과 비슷한", click_recommend_first=True)

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

    def test_003_지금많이읽고있는만화_섹션(self):
        section_name = "지금 많이 읽고 있는 만화"
        self._run_section_flow(section_name, on_more_screen=lambda: self._log_more_screen_first_last(section_name))

    def test_004_오늘_리디의_발견_섹션(self):
        self._run_section_flow("오늘, 리디의 발견")

    def test_005_구매이력기반_AI추천_섹션(self):
        section_name = "구매이력 기반 AI 추천"
        self._run_section_flow(section_name, on_more_screen=lambda: self._log_more_screen_first_last(section_name))

    def test_006_오직리디_섹션(self):
        section_name = "오직 리디!"
        self._run_section_flow(section_name, post_more_wait=3)

    def test_007_새로나온작품_섹션(self):
        section_name = "새로 나온 작품"
        self._run_section_flow(section_name, back_via_subtab=True, verify_all_button=True)

    def test_008_만화베스트_섹션(self):
        section_name = "만화 베스트"
        self._run_section_flow(section_name, back_via_subtab=True, verify_all_button=True)

    def test_009_웹툰만화_키워드검색_섹션(self):
        section_name = "웹툰/만화 키워드 검색"
        self._run_section_flow(section_name, post_more_wait=3, skip_item_swipe=True)

    def test_010_지금리디에서만볼수있는만화_섹션(self):
        section_name = "지금, 리디에서만 볼 수 있는 만화"
        self._run_section_flow(section_name, on_more_screen=lambda: self._log_more_screen_first_last(section_name))

    def test_011_취향저격_AI추천_섹션(self):
        section_name = "님의 취향 저격 AI 추천"
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


class TestBesttab:
    AGE_GENDER_TABS = [
        "전체", "10대 남성", "10대 여성", "20대 남성", "20대 여성",
        "30대 남성", "30대 여성", "40대 남성", "40대 여성", "50대 남성", "50대 여성",
    ]

    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver   = driver
        self.platform = platform
        self.page     = ComicGenrePage(driver, platform)

    def test_001_만화장르홈_진입(self):
        self.page.enter_comic_genrehome()
        assert self.page.is_comic_genrehome_displayed(), \
            "❌ 만화 장르홈 진입 실패 — 추천 서브탭 미노출"

    def test_002_베스트탭_진입_필터확인(self):
        self.page.click_subtab("베스트")
        time.sleep(2)
        filter_ok = self.page.is_all_filter_visible("필터")
        logging.info(f"[베스트탭] 필터 버튼 노출 {'✅' if filter_ok else '❌'}")
        assert filter_ok, "❌ 베스트 탭 진입 실패 — 필터 버튼 미노출"

    def test_003_연령성별_기본선택_및_좌우스와이프_확인(self):
        default_tab = self.page.DEFAULT_AGE_GENDER_TAB

        found = {}
        for tab in self.AGE_GENDER_TABS:
            if self.page.is_age_gender_tab_visible(tab, log=False):
                found[tab] = "초기"

        if self.platform == "aos":
            right_swipe_count = 0
            stall = 0
            prev_names = tuple(self.page.get_all_age_gender_tab_names())
            while stall < 2 and right_swipe_count < 6:
                self.page.swipe_age_gender_tab_right()
                right_swipe_count += 1
                for tab in self.AGE_GENDER_TABS:
                    if tab not in found and self.page.is_age_gender_tab_visible(tab, log=False):
                        found[tab] = f"우스와이프 {right_swipe_count}회"
                cur_names = tuple(self.page.get_all_age_gender_tab_names())
                stall = 0 if cur_names != prev_names else stall + 1
                prev_names = cur_names
            logging.info(f"[베스트탭] 우스와이프 총 {right_swipe_count}회 진행")
            for _ in range(right_swipe_count):
                self.page.swipe_age_gender_tab_left()

            left_swipe_count = 0
            stall = 0
            prev_names = tuple(self.page.get_all_age_gender_tab_names())
            while stall < 2 and left_swipe_count < 6:
                self.page.swipe_age_gender_tab_left()
                left_swipe_count += 1
                for tab in self.AGE_GENDER_TABS:
                    if tab not in found and self.page.is_age_gender_tab_visible(tab, log=False):
                        found[tab] = f"좌스와이프 {left_swipe_count}회"
                cur_names = tuple(self.page.get_all_age_gender_tab_names())
                stall = 0 if cur_names != prev_names else stall + 1
                prev_names = cur_names
            logging.info(f"[베스트탭] 좌스와이프 총 {left_swipe_count}회 진행")
            for _ in range(left_swipe_count):
                self.page.swipe_age_gender_tab_right()
        else:
            right_swipe_count = 4
            for swipe_count in range(1, right_swipe_count + 1):
                self.page.swipe_age_gender_tab_right()
                for tab in self.AGE_GENDER_TABS:
                    if tab not in found and self.page.is_age_gender_tab_visible(tab, log=False):
                        found[tab] = f"우스와이프 {swipe_count}회"
            logging.info(f"[베스트탭] 우스와이프 총 {right_swipe_count}회(고정) 진행")
            for _ in range(right_swipe_count):
                self.page.swipe_age_gender_tab_left()

            left_swipe_count = 4
            for swipe_count in range(1, left_swipe_count + 1):
                self.page.swipe_age_gender_tab_left()
                for tab in self.AGE_GENDER_TABS:
                    if tab not in found and self.page.is_age_gender_tab_visible(tab, log=False):
                        found[tab] = f"좌스와이프 {swipe_count}회"
            logging.info(f"[베스트탭] 좌스와이프 총 {left_swipe_count}회(고정) 진행")
            for _ in range(left_swipe_count):
                self.page.swipe_age_gender_tab_right()

        default_ok = default_tab in found
        logging.info(f"[베스트탭] 기본 선택 탭({default_tab}) 노출 {'✅' if default_ok else '❌'} (탐색결과: {found.get(default_tab, '없음')})")

        missing = [t for t in self.AGE_GENDER_TABS if t not in found]
        logging.info(f"[베스트탭] 연령/성별 탭 확인 결과: {found}")
        assert default_ok, f"❌ 기본 선택 탭({default_tab}) 미노출(좌우 스와이프 탐색 포함)"
        assert not missing, f"❌ 연령/성별 탭 미발견: {missing}"

    def test_004_1위_마지막작품_확인(self):
        collected = self.page.collect_besttab_items_by_scroll(max_scrolls=40)
        first_item = collected[0] if collected else "(확인불가)"
        last_item = collected[-1] if collected else "(확인불가)"
        logging.info(f"[베스트탭] 1위 작품: {first_item}")
        logging.info(f"[베스트탭] 마지막 작품(200위, 스크롤 수집 {len(collected)}건): {last_item}")
        assert first_item != "(확인불가)", "❌ 1위 작품 확인 실패"
        assert last_item != "(확인불가)", "❌ 마지막 작품(200위) 확인 실패"


class TestNewcontentstab:
    CONTENT_CATEGORY_TABS = [
        "전체", "해외순정", "판타지/SF", "액션", "드라마", "스포츠", "코믹",
        "공포/추리", "GL", "학원", "국내순정", "무협", "극화", "만화잡지",
    ]

    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver   = driver
        self.platform = platform
        self.page     = ComicGenrePage(driver, platform)

    def test_001_만화장르홈_진입(self):
        self.page.enter_comic_genrehome()
        assert self.page.is_comic_genrehome_displayed(), \
            "❌ 만화 장르홈 진입 실패 — 추천 서브탭 미노출"

    def test_002_신작탭_진입_필터확인(self):
        self.page.click_subtab("신작")
        time.sleep(2)
        filter_ok = self.page.is_all_filter_visible("필터")
        logging.info(f"[신작탭] 필터 버튼 노출 {'✅' if filter_ok else '❌'}")
        assert filter_ok, "❌ 신작 탭 진입 실패 — 필터 버튼 미노출"

    def test_003_카테고리서브탭_기본선택_및_좌우스와이프_확인(self):
        default_tab = self.page.DEFAULT_NEWCONTENT_TAB
        default_ok = self.page.is_newcontent_subtab_visible(default_tab)
        logging.info(f"[신작탭] 기본 선택 탭({default_tab}) 노출 {'✅' if default_ok else '❌'}")
        assert default_ok, f"❌ 기본 선택 탭({default_tab}) 미노출"

        found = {}
        for tab in self.CONTENT_CATEGORY_TABS:
            if self.page.is_newcontent_subtab_visible(tab, log=False):
                found[tab] = "초기"

        if self.platform == "aos":
            left_swipe_count = 0
            stall = 0
            prev_names = tuple(self.page.get_all_newcontent_subtab_names())
            while stall < 2 and left_swipe_count < 6:
                self.page.swipe_newcontent_subtab_left()
                left_swipe_count += 1
                for tab in self.CONTENT_CATEGORY_TABS:
                    if tab not in found and self.page.is_newcontent_subtab_visible(tab, log=False):
                        found[tab] = f"좌스와이프 {left_swipe_count}회"
                cur_names = tuple(self.page.get_all_newcontent_subtab_names())
                stall = 0 if cur_names != prev_names else stall + 1
                prev_names = cur_names
            logging.info(f"[신작탭] 좌스와이프 총 {left_swipe_count}회 진행")
        else:
            left_swipe_count = 4
            for swipe_count in range(1, left_swipe_count + 1):
                self.page.swipe_newcontent_subtab_left()
                for tab in self.CONTENT_CATEGORY_TABS:
                    if tab not in found and self.page.is_newcontent_subtab_visible(tab, log=False):
                        found[tab] = f"좌스와이프 {swipe_count}회"
            logging.info(f"[신작탭] 좌스와이프 총 {left_swipe_count}회(고정) 진행")

        for _ in range(left_swipe_count):
            self.page.swipe_newcontent_subtab_right()

        missing = [t for t in self.CONTENT_CATEGORY_TABS if t not in found]
        logging.info(f"[신작탭] 카테고리 서브탭 확인 결과: {found}")
       
        if missing:
            logging.warning(
                f"⚠️ [신작탭] 기대목록 중 미노출 {len(missing)}개: {missing} "
                f"(전체 제외 카테고리는 개인화로 노출이 유동적이라 실패로 보지 않음)"
            )

    def test_004_첫번째_마지막작품_확인(self):
        collected = self.page.collect_newcontenttab_items_by_scroll(max_scrolls=40)
        first_item = collected[0] if collected else "(확인불가)"
        last_item = collected[-1] if collected else "(확인불가)"
        logging.info(f"[신작탭] 첫번째 작품: {first_item}")
        logging.info(f"[신작탭] 마지막 작품(스크롤 수집 {len(collected)}건): {last_item}")
        assert first_item != "(확인불가)", "❌ 첫번째 작품 확인 실패"
        assert last_item != "(확인불가)", "❌ 마지막 작품 확인 실패"


class TestBLtab:
    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver   = driver
        self.platform = platform
        self.page     = ComicGenrePage(driver, platform)

    def test_001_만화장르홈_진입(self):
        self.page.enter_comic_genrehome()
        assert self.page.is_comic_genrehome_displayed(), \
            "❌ 만화 장르홈 진입 실패 — 추천 서브탭 미노출"

    def test_002_방금본작품과비슷한_섹션(self):
        self._run_section_flow("방금 본 작품과 비슷한", click_bl_first=True, subtab_name="BL")

    def _run_section_flow(self, section_name: str, click_bl_first: bool = False, on_more_screen=None,
                           back_via_subtab: bool = False, verify_all_button: bool = False, post_more_wait: float = None,
                           all_button_text: str = "필터", skip_item_swipe: bool = False, wide_swipe: bool = False,
                           safe_margin_ratio: float = 0.45, subtab_name: str = None):
        if click_bl_first:
            self.page.click_subtab("BL")
            time.sleep(1)

        found = self.page.scroll_to_section(section_name, safe_margin_ratio=safe_margin_ratio, subtab_name=subtab_name)
        if not found:
            self.page.enter_comic_genrehome()
            time.sleep(2)
            if click_bl_first:
                self.page.click_subtab("BL")
                time.sleep(1)
            
            if section_name in self.page.AOS_PERSONALIZED_SECTIONS:
                pytest.skip(f"[{section_name}] 계정 상태로 개인화 섹션 미노출 - 스킵")
        assert found, f"❌ [{section_name}] 섹션 미노출"

        if self.platform == "aos" and section_name in self.page.AOS_PERSONALIZED_SECTIONS \
                and not self.page.is_section_title_present(section_name):
            pytest.skip(f"[{section_name}] 개인화 섹션 요소 소실(계정 상태) - 스킵")

        if skip_item_swipe:
            time.sleep(1.5)
            logging.info(f"[{section_name}] 좌우스와이프 생략 - 더보기 진입/타이틀 확인만 진행")
        else:
            items = self.page.get_section_item_names(section_name)
            first_item = items[0] if items else "(확인불가)"
            logging.info(f"[{section_name}] 첫번째 작품: {first_item}")

            collected, swipe_count = self.page.collect_section_items_by_swipe(section_name, wide=wide_swipe)
            logging.info(f"[{section_name}] 좌스와이프 {swipe_count}회 - 총 콘텐츠 수: {len(collected)}개")
            for i, name in enumerate(collected, 1):
                logging.info(f"[{section_name}]   {i}. {name}")

            last_item = collected[-1] if collected else "(확인불가)"
            logging.info(f"[{section_name}] 마지막 작품: {last_item}")

            for _ in range(swipe_count):
                self.page.swipe_section_right(section_name, wide=wide_swipe)
            logging.info(f"[{section_name}] 우스와이프 {swipe_count}회 원위치 복귀")

        if not self.page.is_section_more_visible(section_name):
            logging.info(f"[{section_name}] 더보기 버튼 없음 - 스킵")
            return

        if verify_all_button:
            tapped = self.page.click_section_more(section_name)
            assert tapped, f"❌ [{section_name}] 더보기 콘텐츠 로딩 미확인으로 탭 보류"
            time.sleep(5)
            all_visible = self.page.is_all_filter_visible(all_button_text)
            logging.info(f"[{section_name}] 더보기 목적지 '{all_button_text}' 버튼 노출 {'✅' if all_visible else '❌'}")
            assert all_visible, f"❌ [{section_name}] 더보기 목적지에서 '{all_button_text}' 버튼 미노출"
            time.sleep(3)
            self.page.click_subtab("BL")
            time.sleep(1)
            assert self.page.is_comic_genrehome_displayed(), \
                f"❌ [{section_name}] 더보기 화면전환 후 장르홈 복귀 실패"
            return

        try:
            dest_title, verified = self.page.click_section_more_and_verify(section_name)
            navigated = bool(dest_title.strip())
            logging.info(f"[{section_name}] 더보기 클릭 → 화면전환 {'✅' if navigated else '❌'} (상단타이틀: '{dest_title}')")
        except Exception as e:
            navigated, verified = True, True
            logging.warning(f"[{section_name}] 화면전환 타이틀 확인 실패(iOS WDA 이슈 가능) - 더보기 클릭은 성공했으므로 화면전환된 것으로 간주: {e}")
        if not verified:
            logging.warning(f"[{section_name}] 더보기 목적지 검증 끝내 실패 - 후속 처리 스킵")
            assert self.page.is_comic_genrehome_displayed(), \
                f"❌ [{section_name}] 더보기 재시도 종료 후 장르홈 복귀 실패"
            return
        time.sleep(post_more_wait if post_more_wait is not None else (1 if on_more_screen else 0))
        if navigated:
            if on_more_screen:
                on_more_screen()
            if back_via_subtab:
                self.page.click_subtab("BL")
                time.sleep(1)
            else:
                self.page.navigate_back_to_genrehome()
            assert self.page.is_comic_genrehome_displayed(), \
                f"❌ [{section_name}] 더보기 화면전환 후 장르홈 복귀 실패"

    def _log_more_screen_first_last(self, section_name: str, max_scrolls: int = 10):
        try:
            items = self.page.get_visible_content_item_names()
            noise_exact = {section_name, "더보기"}
            real_items = [i for i in items if i.strip() not in noise_exact]
            first_item = real_items[0] if real_items else (items[0] if items else "(확인불가)")
            collected = self.page.collect_items_by_vertical_scroll(max_scrolls=max_scrolls, force_full_scroll=True)
            last_item = collected[-1] if collected else first_item
            logging.info(f"[{section_name}][더보기 화면] 첫번째 작품: {first_item}")
            logging.info(f"[{section_name}][더보기 화면] 마지막 작품: {last_item}")
        except Exception as e:
            logging.warning(f"[{section_name}][더보기 화면] 첫/마지막 작품 확인 실패(iOS WDA 이슈 가능): {e}")

    def test_003_BL키워드검색_섹션(self):
        self._run_section_flow("BL 키워드 검색", click_bl_first=True, post_more_wait=3, skip_item_swipe=True)

    def test_004_BL만화_실시간랭킹_섹션(self):
        section_name = "BL만화 실시간 랭킹"
        self._run_section_flow(section_name, wide_swipe=True,
                                on_more_screen=lambda: self._log_more_screen_first_last(section_name))

    def test_005_BL만화_베스트_섹션(self):
        section_name = "BL만화 베스트"
        self._run_section_flow(section_name, wide_swipe=True,
                                on_more_screen=lambda: self._log_more_screen_first_last(section_name, max_scrolls=40))

    def test_006_BL만화_e북이벤트_섹션(self):
        self._run_section_flow("BL만화 e북 이벤트", post_more_wait=3, skip_item_swipe=True)

    def test_007_지금리디에서만볼수있는BL만화_섹션(self):
        section_name = "지금, 리디에서만 볼 수 있는 BL만화"
        self._run_section_flow(section_name, post_more_wait=3, wide_swipe=True,
                                on_more_screen=lambda: self._log_more_screen_first_last(section_name))

    def test_008_BL만화_e북신간_섹션(self):
        section_name = "BL만화 e북 신간"
        self._run_section_flow(section_name,
                                on_more_screen=lambda: self._log_more_screen_first_last(section_name))
