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


class TestComicGenrehome:

    SUBTAB_FIXED = ["추천", "베스트", "신작", "BL"]

    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver   = driver
        self.platform = platform
        self.page     = ComicGenrePage(driver, platform)

    # ── 001: 딥링크 진입 ──────────────────────────────────
    def test_001_만화장르홈_딥링크진입(self):
        self.page.enter_comic_genrehome()
        assert self.page.is_comic_genrehome_displayed(), \
            "❌ 만화 장르홈 진입 실패 — 추천 서브탭 미노출"

    # ── 002: 서브탭 좌우 스와이프 고정 탭 확인 ──────────────
    def test_002_서브탭_좌우스와이프_전체탭확인(self):
        found = {}  # {탭명: 발견 시점 ("초기" or "좌스와이프 N회")}

        # 초기 노출 탭 확인 (고정 4개)
        for tab in self.SUBTAB_FIXED:
            if self.page.is_subtab_visible(tab):
                found[tab] = "초기"
        logging.info(f"[서브탭] 초기 탐색 결과: {list(found.keys()) or '없음'}")

        # 좌 스와이프로 끝까지 이동 (전체 서브탭 노출 목록이 2회 연속 변화 없으면 끝으로 판단, 최대 5회)
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

    # ── 003: 서브탭 순차 이동 (정방향 추천→베스트→신작→BL, 역방향 BL→신작→베스트→추천) ──
    def test_003_서브탭_순차이동_정역방향(self):
        assert self.page.is_big_banner_displayed(), \
            "❌ 추천 서브탭 진입 후 빅배너 미노출"

        # 정방향: 추천 → 베스트 → 신작 → BL
        for tab in ["베스트", "신작", "BL"]:
            self.page.click_subtab(tab)
            time.sleep(1)
            assert self.page.is_subtab_visible(tab), f"❌ {tab} 서브탭 진입 실패 (정방향)"
        logging.info("[서브탭] 정방향 이동 완료: 추천 → 베스트 → 신작 → BL")

        # 역방향: BL → 신작 → 베스트 → 추천
        for tab in ["신작", "베스트", "추천"]:
            self.page.click_subtab(tab)
            time.sleep(1)
            assert self.page.is_subtab_visible(tab), f"❌ {tab} 서브탭 복귀 실패 (역방향)"
        logging.info("[서브탭] 역방향 복귀 완료: BL → 신작 → 베스트 → 추천")

        assert self.page.is_big_banner_displayed(), \
            "❌ 추천 서브탭 복귀 후 빅배너 미노출"

    # ── 004: 빅배너 표시, 아이템 수/문구 확인, 좌우 스와이프 ──
    def test_004_빅배너_표시_및_스와이프(self):
        self.page.click_subtab("추천")
        time.sleep(1.5)

        assert self.page.is_big_banner_displayed(), \
            "❌ 빅배너 미노출"

        # 페이지네이션 인디케이터로 총 개수 확인
        total = self.page.get_big_banner_total_count()
        logging.info(f"[빅배너] 총 {total}개 (캐러셀 인디케이터 기준)")
        assert total > 0, "❌ 빅배너 총 개수 확인 불가"

        # 총 개수만큼 좌스와이프하며 전체 배너 문구 순차 수집
        items = self.page.collect_big_banner_items_by_swipe(max_count=total)
        logging.info(f"[빅배너] 스와이프로 수집한 배너 {len(items)}/{total}개")
        for i, text in enumerate(items, 1):
            logging.info(f"[빅배너]   {i}. {text}")

        self.page.swipe_big_banner_left(times=2)
        assert self.page.is_big_banner_displayed(), \
            "❌ 빅배너 좌 스와이프 후 미노출"

        self.page.swipe_big_banner_right(times=2)
        assert self.page.is_big_banner_displayed(), \
            "❌ 빅배너 우 스와이프 복귀 후 미노출"
