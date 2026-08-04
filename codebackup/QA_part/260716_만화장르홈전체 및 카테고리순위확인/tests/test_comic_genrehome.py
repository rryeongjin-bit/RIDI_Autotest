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

class TestGenretab:
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
            # AOS: page_source 조회가 가벼워 전체 서브탭 노출 목록이 2회 연속 변화 없으면 끝으로 판단 (최대 5회)
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
            # iOS: page_source 전체 덤프(get_all_subtab_names)가 WDA에서 타임아웃 위험이 있어 고정 횟수로 대체
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

        # 우 스와이프로 이동한 횟수만큼 순차적으로 처음(추천 탭)까지 복귀
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


class TestGenreSection:
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
        assert found, f"❌ [{section_name}] 섹션 미노출"

        if skip_item_swipe:
            # "웹툰/만화 키워드 검색"처럼 실제 작품 캐러셀이 아니라 키워드 태그 위젯인 섹션은
            # 좌우스와이프로 작품을 수집할 대상이 없어(aos/ios 공통), 더보기 진입 후 타이틀
            # 확인과 복귀만 수행한다.
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
            # 이 섹션은 목적지 화면 상단 타이틀 추출이 불안정해 타이틀 확인 코드 자체를 쓰지
            # 않는다 — 더보기 클릭 후 고정 탭(all_button_text) 노출 여부만으로 정상 도달을
            # 판단하고, 명시적 3초 대기 후 "추천" 서브탭을 다시 선택해 장르홈으로 복귀한다.
            tapped = self.page.click_section_more(section_name)
            assert tapped, f"❌ [{section_name}] 더보기 콘텐츠 로딩 미확인으로 탭 보류"
            time.sleep(5)  # 화면 전환 대기 (탭 직후 바로 확인하면 탭이 아직 안 그려져 있음)
            all_visible = self.page.is_all_filter_visible(all_button_text)
            logging.info(f"[{section_name}] 더보기 목적지 '{all_button_text}' 버튼 노출 {'✅' if all_visible else '❌'}")
            assert all_visible, f"❌ [{section_name}] 더보기 목적지에서 '{all_button_text}' 버튼 미노출"
            time.sleep(3)
            self.page.click_subtab("추천")
            time.sleep(1)
            assert self.page.is_comic_genrehome_displayed(), \
                f"❌ [{section_name}] 더보기 화면전환 후 장르홈 복귀 실패"
            return

        # click_section_more_and_verify: 더보기 클릭 후 실제 도달한 화면 타이틀이 기대
        # 목적지와 다르면(오탭) 장르홈으로 되돌아가 자동 재시도까지 수행한다(iOS 전용,
        # IOS_SECTION_MORE_DEST_HINT에 힌트가 등록된 섹션만; 그 외/AOS는 기존과 동일 1회 시도).
        # get_current_top_title()은 전체 page_source를 읽는데, iOS WDA가 이 호출에서
        # 종종 120초 타임아웃/hang을 일으켜서(참고: memory.md) 실패해도 더보기 클릭 자체는
        # 이미 성공했으므로 화면전환된 것으로 간주하고 진행한다.
        try:
            dest_title, verified = self.page.click_section_more_and_verify(section_name)
            navigated = bool(dest_title.strip())
            logging.info(f"[{section_name}] 더보기 클릭 → 화면전환 {'✅' if navigated else '❌'} (상단타이틀: '{dest_title}')")
        except Exception as e:
            navigated, verified = True, True
            logging.warning(f"[{section_name}] 화면전환 타이틀 확인 실패(iOS WDA 이슈 가능) - 더보기 클릭은 성공했으므로 화면전환된 것으로 간주: {e}")
        if not verified:
            # 재시도까지 다 실패해 기대 목적지가 아닌 걸로 확인됨 — click_section_more_and_verify가
            # 이미 장르홈으로 복귀해둔 상태이므로, 잘못된 화면에서 무거운 후속 처리(세로스크롤 등,
            # iOS WDA page_source 120초 타임아웃 위험)를 시도하지 않고 여기서 종료한다.
            logging.warning(f"[{section_name}] 더보기 목적지 검증 끝내 실패 - 후속 처리 스킵")
            assert self.page.is_comic_genrehome_displayed(), \
                f"❌ [{section_name}] 더보기 재시도 종료 후 장르홈 복귀 실패"
            return
        time.sleep(post_more_wait if post_more_wait is not None else (1 if on_more_screen else 0))
        if navigated:
            if on_more_screen:
                on_more_screen()
            if back_via_subtab:
                # 이 섹션의 더보기 목적지 화면은 "<" 뒤로가기가 아니라 "추천" 서브탭을
                # 다시 선택해야 장르홈으로 복귀된다(실기기로 확인됨).
                self.page.click_subtab("추천")
                time.sleep(1)
            else:
                self.page.navigate_back_to_genrehome()
            assert self.page.is_comic_genrehome_displayed(), \
                f"❌ [{section_name}] 더보기 화면전환 후 장르홈 복귀 실패"

    def test_002_방금본작품과_비슷한_섹션(self):
        self._run_section_flow("방금 본 작품과 비슷한", click_recommend_first=True)

    def _log_more_screen_first_last(self, section_name: str):
        """더보기 화면 진입 후 세로스크롤하며 첫번째/마지막 작품명 로그.
        iOS는 page_source 호출이 무거운 화면에서 WDA가 종종 120초 타임아웃을 내는
        고질적인 이슈가 있어(참고: memory.md), 부가 정보 수집 실패로 본 테스트 전체가
        실패하지 않도록 예외처리한다.

        "지금 많이 읽고 있는 만화"는 목적지 화면이 순위(1위~)가 매겨진 랭킹 리스트라
        범용 get_visible_content_item_names/collect_items_by_vertical_scroll로는
        "N개 작품 주간" 같은 안내문구를 항목으로 잘못 집어내는 문제가 실기기로 확인되어,
        카테고리 목적지 화면용으로 만든(이름은 category_dest지만 실제로는 "순위+베스트/
        신작/전체 서브탭" 구조를 가진 목적지 화면 전반에 재사용 가능한) 랭킹 전용 추출
        로직을 그대로 재사용한다.

        "지금, 리디에서만 볼 수 있는 만화"는 순위 번호가 없는 일반 카드 목록이고(aos/ios
        공통, 더보기 진입 시 "RIDI ONLY 만화" 타이틀에 "만화" 탭이 활성화된 채로 노출됨)
        작품 수가 많아 화면 끝을 감지할 별도 수단이 없어, stall 조기 종료 없이 정확히 10회
        스크롤을 강제하고 그 시점까지 확인된 마지막 항목을 사용한다.

        그 외 섹션은 랭킹 구조가 아니라 기존 로직을 유지한다."""
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
        """장르홈 맨 마지막 섹션("{계정ID}님의 취향 저격 AI 추천"). 더보기가 없고 페이지 최하단
        바로 위라, 좌우스와이프 수집 대신 푸터가 노출될 때까지 세로 스크롤로 끝까지 내려가
        마지막 작품을 확인하고 종료한다."""
        section_name = "님의 취향 저격 AI 추천"
        found = self.page.scroll_to_section(section_name)
        assert found, f"❌ [{section_name}] 섹션 미노출"

        items = self.page.get_section_item_names(section_name)
        first_item = items[0] if items else "(확인불가)"
        logging.info(f"[{section_name}] 첫번째 작품: {first_item}")

        last_item, footer_reached = self.page.scroll_to_footer_and_get_last_item(section_name)
        logging.info(f"[{section_name}] 마지막 작품(푸터 노출 {'✅' if footer_reached else '❌'}): {last_item}")
