from pages.base_page import *
from locators.contentshome import *
from locators.genrehome import *
from locators.common import *
from data.test_data import *

class MainhomePage(BasePage):
    def is_genrehome_displayed(self) -> bool:
        locator = AOS_GenrehomeLocators.COMIC_RECOMMEND_TAB if self.platform == "aos" \
                  else IOS_GenrehomeLocators.COMIC_NEW_QUICK
        return self.is_present(locator)
    
    def click_cart_icon(self):
        if self.platform == "aos":
            self.tap_coordinate(1006, 156)
        else:
            self.tap_coordinate(363, 69)


class ComicGenrePage(BasePage):
    SUBTAB_LOCATOR = {
        "추천":  "SUBTAB_RECOMMEND",
        "베스트": "SUBTAB_BEST",
        "신작":  "SUBTAB_NEW",
        "BL":   "SUBTAB_BL",
    }

    def _loc(self, attr: str):
        cls = AOS_COMIC_GENRE if self.platform == "aos" else IOS_COMIC_GENRE
        return getattr(cls, attr)

    def enter_comic_genrehome(self):
        self.open_deeplink(DeepLinks.COMIC_RECOMMEND_HOME)
        # watchdog로 --reset=skip 상태에서 특정 클래스부터 재시작하면 TestLaunchApp/
        # reset_app(둘 다 --reset=full일 때만 동작)을 거치지 않아 알림/트래킹 팝업을
        # 아무도 체크하지 않는 문제가 실기기로 확인되어(2026-07-23), 진입할 때마다
        # --reset 값과 무관하게 항상 확인하도록 여기서 재사용한다. 팝업이 없으면
        # _dismiss_ios_system_alert() 내부에서 조용히 무시된다.
        self._dismiss_ios_system_alert()
        self._dismiss_ios_system_alert()
        self.log.info("[진입] 만화 장르홈 진입")

    def is_comic_genrehome_displayed(self) -> bool:
        return self.is_present(self._loc("SUBTAB_RECOMMEND"))

    def click_main_tab(self):
        self.click(self._loc("MAIN_TAB"))
        self.log.info("[메인탭] 만화 탭 클릭")

    #서브탭 
    def _subtab_y(self) -> int:
        return int(self.driver.get_window_size()["height"] * 0.12)

    def swipe_subtab_left(self):
        w = self.driver.get_window_size()["width"]
        y = self._subtab_y()
        self.driver.swipe(int(w * 0.80), y, int(w * 0.20), y, 500)
        time.sleep(0.4)

    def swipe_subtab_right(self):
        w = self.driver.get_window_size()["width"]
        y = self._subtab_y()
        self.driver.swipe(int(w * 0.20), y, int(w * 0.80), y, 500)
        time.sleep(0.4)

    def is_subtab_visible(self, tab_name: str, timeout: int = 3, log: bool = True) -> bool:
        attr = self.SUBTAB_LOCATOR[tab_name]
        if self.platform == "ios":
            result = self.is_element_present(self._loc(attr), timeout=timeout)
        else:
            result = self.is_present(self._loc(attr), timeout=timeout)
        if log:
            self.log.info(f"[서브탭확인] {tab_name} {'✅' if result else '❌'}")
        return result

    def click_subtab(self, tab_name: str, log: bool = True):
        attr = self.SUBTAB_LOCATOR[tab_name]
        locator = self._loc(attr)
        if self.platform == "ios":
            self.wait_for_element(locator)
            self.find_element(locator).click()
        else:
            self.click(locator)
        if log:
            self.log.info(f"[서브탭클릭] {tab_name}")

    #빅배너
    def is_big_banner_displayed(self) -> bool:
        if self.platform == "ios":
            items = self.get_big_banner_items()
            if items:
                self.log.info(f"[빅배너] ✅ 확인 ({len(items)}개)")
                return True
            self.log.warning("[빅배너] ❌ 미확인")
            return False
        size = self.driver.get_window_size()
        h = size["height"]
        els = self.find_elements(self._loc("BIG_BANNER"))
        for el in els:
            try:
                y = el.location.get("y", 0)
                if h * 0.12 < y < h * 0.65:
                    self.log.info(f"[빅배너] ✅ 확인 (y={y})")
                    return True
            except Exception:
                pass
        self.log.warning("[빅배너] ❌ 미확인")
        return False

    def get_big_banner_items(self) -> list:
        """빅배너 렌더링 완료 아이템 목록 반환"""
        if self.platform == "aos":
            size = self.driver.get_window_size()
            h = size["height"]
            seen = set()
            items = []
            for el in self.find_elements(self._loc("BIG_BANNER")):
                try:
                    y = el.location.get("y", 0)
                    el_h = el.size.get("height", 0)
                    if not (h * 0.12 < y < h * 0.65) or el_h < h * 0.25:
                        continue
                    desc = (el.get_attribute("content-desc") or "").strip()
                    if desc and desc not in seen:
                        seen.add(desc)
                        items.append(desc)
                except Exception:
                    pass
            return items

        # 전체 page_source 덤프(driver.page_source)는 이 화면에서 WDA가 반복적으로 120초
        # 타임아웃을 일으켜(_get_ios_section_content와 동일한 이유), 대신 BIG_BANNER 로케이터로
        # 가벼운 타겟 조회만 수행하고 좌표/크기로 실제 배너 카드만 가려낸다(AOS 분기와 동일 방식).
        seen = set()
        items = []
        for el in self.find_elements(self._loc("BIG_BANNER")):
            try:
                y = el.location.get("y", -1)
                h = el.size.get("height", 0)
                w = el.size.get("width", 0)
                name = (el.get_attribute("name") or "").strip()
                if 155 <= y <= 215 and 300 <= h <= 400 and 380 <= w <= 430 and name:
                    clean = name.replace("\n", " / ")
                    if clean not in seen:
                        seen.add(clean)
                        items.append(clean)
            except Exception:
                pass
        return items

    def get_all_subtab_names(self) -> list:
        """page_source에서 전체 서브탭 이름 추출 """
        if self.platform == "aos":
            import re
            bounds_pattern = re.compile(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]')
            subtab_y = self._subtab_y()
            y_tolerance = int(self.driver.get_window_size()["height"] * 0.03)
            items = []
            seen = set()
            import xml.etree.ElementTree as ET
            root = ET.fromstring(self.driver.page_source)
            for elem in root.iter():
                text = (elem.get("text") or "").strip()
                if not text:
                    continue
                m = bounds_pattern.match(elem.get("bounds", ""))
                if not m:
                    continue
                x1, y1, x2, y2 = map(int, m.groups())
                y_center = (y1 + y2) // 2
                if abs(y_center - subtab_y) <= y_tolerance and text not in seen:
                    seen.add(text)
                    items.append((x1, text))
            items.sort(key=lambda t: t[0])
            return [name for _, name in items]

        import xml.etree.ElementTree as ET
        source = self.driver.page_source
        root = ET.fromstring(source)
        items = []
        seen = set()
        for elem in root.iter():
            y = int(elem.get("y", -1))
            h = int(elem.get("height", 0))
            name = (elem.get("name") or "").strip()
            accessible = elem.get("accessible", "false")
            x = int(elem.get("x", 0))
            if 110 <= y <= 135 and 20 <= h <= 50 and accessible == "true" and name:
                words = name.split()
                mid = len(words) // 2
                if mid > 0 and words[:mid] == words[mid:]:
                    clean = " ".join(words[:mid])
                else:
                    clean = name
                if clean not in seen:
                    seen.add(clean)
                    items.append((x, clean))
        items.sort(key=lambda t: t[0])
        return [name for _, name in items]

    def _big_banner_screenshot_hash(self) -> int:
        """iOS 전용: 빅배너 영역 스크린샷의 average hash(64bit) 반환.
        iOS는 빅배너가 자동재생 중일 때 class-chain 접근성 조회(get_big_banner_items)가
        실기기로 확인한 결과 항상 0건만 반환해(WDA가 이 화면에서 접근성 트리 조회 자체를
        못함) 텍스트/카운터를 읽을 수 없다. OCR도 시도해봤으나 배너 20개가 각각 다른
        일러스트 위에 그림자 낀 반투명 텍스트라 신뢰도 있게 못 읽어(실기기 검증됨), 텍스트
        추출은 포기하고 화면 내용 자체의 변화를 이미지 해시로 판별한다."""
        from PIL import Image
        import io
        png = self.driver.get_screenshot_as_png()
        img = Image.open(io.BytesIO(png))
        w, h = img.size
        box = (int(w * 0.03), int(h * 0.18), int(w * 0.97), int(h * 0.62))
        small = img.crop(box).convert("L").resize((8, 8), Image.LANCZOS)
        pixels = list(small.tobytes())
        avg = sum(pixels) / len(pixels)
        bits = "".join("1" if p > avg else "0" for p in pixels)
        return int(bits, 2)

    def collect_big_banner_variants_by_polling(self, target_count: int = 5, interval: float = 4.0,
                                                max_polls: int = 15, hash_threshold: int = 10) -> list:
        """iOS 전용: 빅배너 영역 스크린샷 해시를 4초 간격으로 비교해, 이전에 본 해시들과
        해밍 거리가 hash_threshold를 넘는(=충분히 다른 화면인) 변형이 target_count개
        관측되면 종료한다. (수집한 해시 목록, 처음 관측된 순서 유지) 반환."""
        seen_hashes = []
        for _ in range(max_polls):
            h = self._big_banner_screenshot_hash()
            if all(bin(h ^ prev).count("1") > hash_threshold for prev in seen_hashes):
                seen_hashes.append(h)
            if len(seen_hashes) >= target_count:
                break
            time.sleep(interval)
        return seen_hashes

    def collect_big_banner_items_by_polling(self, target_count: int = 5, interval: float = 4.0, max_polls: int = 15) -> list:
        """빅배너는 자동전환(autoplay)되는 캐러셀이라 스와이프로 직접 넘기려 하면 자동전환과
        충돌해 오히려 불안정해진다. 스와이프 없이 일정 간격으로 그 순간 노출된 배너를 그대로
        확인해, 서로 다른 배너 target_count개가 확인되면 종료한다.
        AOS는 접근성 요소에서 배너 텍스트를 그대로 추출하지만(중복 제거, 처음 확인된 순서
        유지), iOS는 자동재생 중 접근성 조회가 불가해(위 _big_banner_screenshot_hash 참고)
        화면 해시 변화로 대체하고, 실제 텍스트 대신 변형 식별용 문자열을 반환한다."""
        if self.platform == "ios":
            hashes = self.collect_big_banner_variants_by_polling(target_count, interval, max_polls)
            return [f"배너 변형 {i + 1} (hash={h:016x})" for i, h in enumerate(hashes)]

        seen = set()
        ordered_items = []
        for _ in range(max_polls):
            for text in self.get_big_banner_items():
                if text not in seen:
                    seen.add(text)
                    ordered_items.append(text)
            if len(ordered_items) >= target_count:
                break
            time.sleep(interval)
        return ordered_items

    #퀵메뉴
    QUICK_MENU_LOCATOR = {
        "무료":      "FREE_QUICK",
        "이벤트":     "EVENT_QUICK",
        "최저가 세트":  "LOWEST_PRICE_QUICK",
        "월간 캘린더": "MONTHLY_CALENDER_QUICK",
        "리디온리":   "RIDIONLY_QUICK",
    }

    def _quickmenu_y(self) -> int:
        if getattr(self, "_quickmenu_y_cache", None) is not None:
            return self._quickmenu_y_cache
        fallback = int(self.driver.get_window_size()["height"] * 0.65)
        try:
            y = self.find_element(self._loc("FREE_QUICK")).location.get("y", fallback)
        except Exception:
            y = fallback
        self._quickmenu_y_cache = y
        return y

    def swipe_quickmenu_left(self):
        w = self.driver.get_window_size()["width"]
        y = self._quickmenu_y()
        self.driver.swipe(int(w * 0.80), y, int(w * 0.20), y, 500)
        time.sleep(0.4)

    def swipe_quickmenu_right(self):
        w = self.driver.get_window_size()["width"]
        y = self._quickmenu_y()
        self.driver.swipe(int(w * 0.20), y, int(w * 0.80), y, 500)
        time.sleep(0.4)

    def is_quickmenu_visible(self, menu_name: str, timeout: int = 3, log: bool = True) -> bool:
        attr = self.QUICK_MENU_LOCATOR[menu_name]
        if self.platform == "ios":
            result = self.is_element_present(self._loc(attr), timeout=timeout)
        else:
            result = self.is_present(self._loc(attr), timeout=timeout)
        if log:
            self.log.info(f"[퀵메뉴확인] {menu_name} {'✅' if result else '❌'}")
        return result

    def click_quickmenu(self, menu_name: str, log: bool = True):
        attr = self.QUICK_MENU_LOCATOR[menu_name]
        locator = self._loc(attr)
        if self.platform == "ios":
            self.wait_for_element(locator)
            self.find_element(locator).click()
        else:
            self.click(locator)
        if log:
            self.log.info(f"[퀵메뉴클릭] {menu_name}")

    PERSISTENT_TAB_LABELS = {
        "만화", "웹툰", "웹소설", "도서", "리디샵", "셀렉트",
        "내 서재", "검색", "홈", "알림", "MY",
        "리디", "리디 (S)",  # iOS 하위 화면 좌상단 "◀ 리디" 뒤로가기 브레드크럼 라벨 (실제 페이지 타이틀 아님)
        # "리디 (S)"는 새 기기/빌드(QA iPhone 16e)에서 브레드크럼에 붙는 환경 표기(스테이징 추정)
        "STAGE", "S\nT\nA\nG\nE", "S T A G E",  # 화면 우측에 항상 떠 있는 STAGE 이벤트 띠지
        # (세로로 한 글자씩 표기되며 화면/맥락에 따라 줄바꿈 또는 공백으로 구분됨)
        "CANARY", "C\nA\nN\nA\nR\nY", "C A N A R Y",  # 새 기기(QA iPhone 16e)/빌드에서는 같은 자리에 STAGE 대신 CANARY 띠지로 노출됨
        "topCarouselSafeArea",  # 일부 더보기 목적지 화면(웹툰/만화 키워드 검색, 지금 리디에서만
        # 볼 수 있는 만화 등) 최상단(y=0)에 있는 상단 캐러셀 세이프에어리어의 내부 식별자 이름.
        # 실제 페이지 타이틀보다 y가 작아 get_current_top_title()이 이 값을 잘못 1순위로
        # 반환해 목적지 타이틀 검증이 계속 실패하던 원인이었다(실기기 확인).
        "오늘, 리디의 발견",  # 이 섹션은 더보기 버튼이 없어(실기기 확인) 자기 자신의 목적지
        # 화면이 존재하지 않는데도, 인접한 다른 섹션("구매이력 기반 AI 추천" 등)의 더보기
        # 목적지 화면 최상단에 이 문구가 잘못 후보로 잡혀 엉뚱한 타이틀로 반환되는 문제가
        # AOS 실기기로 확인되었다.
    }

    # get_current_top_title()에서 정확히 일치하는 고정 라벨(PERSISTENT_TAB_LABELS)뿐 아니라,
    # "수직 스크롤 막대, N페이지"처럼 뒤에 가변 페이지 번호가 붙는 내부 접근성 라벨(스크롤
    # 인디케이터)도 실기기로 확인되어("지금, 리디에서만 볼 수 있는 만화" 등에서 재현) 접두어
    # 기준으로 걸러낸다.
    NOISE_LABEL_PREFIXES = ("수직 스크롤 막대",)

    def _is_noise_top_title_candidate(self, text: str) -> bool:
        if text in self.PERSISTENT_TAB_LABELS or text.startswith(self.NOISE_LABEL_PREFIXES):
            return True
        # 화면 우측 상단 장바구니/알림 개수 배지가 실제 타이틀보다 y좌표가 미세하게 작아
        # get_current_top_title()이 잘못 1순위로 뽑는 경우가 실기기로 확인됨(계정의 장바구니/
        # 알림 상태에 따라 배지가 뜨거나 안 뜨거나 해서 간헐적으로만 재현됨) - 실제 타이틀은
        # 절대 숫자 단독으로 나오지 않으므로 1~2자리 숫자만 있는 텍스트는 노이즈로 제외한다.
        import re
        if re.fullmatch(r'\d{1,2}', text):
            return True
        # 목적지 화면 전환 직후, 이전 화면(장르홈)의 빅배너 요소가 접근성 트리에서 아직
        # 제거되지 않고 남아있어(y좌표가 실제 타이틀보다 작음) get_current_top_title()이
        # 잘못 1순위로 뽑는 경우가 실기기로 확인됨(예: "BL 키워드 검색" 목적지에서 배너
        # "인외의 순애는\n언제나 압승"이 진짜 타이틀보다 먼저 잡힘). 실제 목적지 타이틀은
        # 항상 한 줄인 반면, 이 배너 캡션은 줄바꿈이 있는 2줄 텍스트라는 확실한 차이가 있어
        # 줄바꿈 포함 텍스트는 노이즈로 제외한다.
        if "\n" in text:
            return True
        # "BL 키워드 검색"/"BL만화 실시간 랭킹" 등 일부 목적지 화면은 실제 타이틀이 개별
        # 요소로 잡히지 않고, 상단 탭바(만화/웹툰/...)가 아이콘+라벨 요소가 겹쳐 각 탭명이
        # 두 번씩 연달아 이어진 "만화 만화 웹툰 웹툰 ..." 형태의 텍스트가 실제 타이틀보다
        # 먼저(y/x가 더 작게) 후보로 잡히는 문제가 실기기로 확인됨. 이 패턴은 공백으로 나눈
        # 단어가 항상 연속 두 개씩 동일한 게 특징이라(실제 타이틀은 이런 형태로 나올 수
        # 없음) 이 규칙 하나로 범용적으로 제외한다.
        words = text.split()
        if len(words) >= 2 and len(words) % 2 == 0 and all(
            words[i] == words[i + 1] for i in range(0, len(words), 2)
        ):
            return True
        return False

    def get_current_top_title(self) -> str:
        """현재 화면 최상단(헤더 영역) 텍스트 반환 (범용, 좌표기반)
        상단에 항상 떠 있는 카테고리 탭바(만화/웹툰/...)는 페이지별 타이틀이 아니므로 제외
        """
        import xml.etree.ElementTree as ET
        h = self.driver.get_window_size()["height"]
        root = ET.fromstring(self.driver.page_source)
        candidates = []
        if self.platform == "aos":
            import re
            bounds_pattern = re.compile(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]')
            for elem in root.iter():
                text = (elem.get("text") or "").strip()
                if not text or self._is_noise_top_title_candidate(text):
                    continue
                m = bounds_pattern.match(elem.get("bounds", ""))
                if not m:
                    continue
                x1, y1, _, _ = map(int, m.groups())
                # 서브탭 바(추천/베스트 등, 화면 상단 약 11%)는 항상 떠 있는 고정 UI라 제외
                if y1 < h * 0.09:
                    candidates.append((y1, x1, text))
        else:
            for elem in root.iter():
                name = (elem.get("name") or "").strip()
                # 이 화면에서 페이지 전체 텍스트가 하나의 블롭 요소에 뭉쳐서 노출되는 경우,
                # 그 블롭의 y좌표가 0(최상단)이라 실제 타이틀처럼 후보에 잡힐 수 있음.
                # 실제 타이틀은 항상 짧으므로 비정상적으로 긴 텍스트는 블롭으로 간주해 제외한다.
                if not name or self._is_noise_top_title_candidate(name) or len(name) > 60:
                    continue
                y = int(elem.get("y", -1))
                if 0 <= y < h * 0.09:
                    x = int(elem.get("x", 0))
                    candidates.append((y, x, name))
        candidates.sort(key=lambda t: (t[0], t[1]))
        if not candidates:
            return ""
        title = candidates[0][2]
        # "BL만화 e북 이벤트" 등 일부 목적지 화면은 실제 타이틀("이벤트") 뒤에 스크롤바
        # 접근성 설명("수직 스크롤 막대, 13페이지 수평 스크롤 막대, 1페이지")이 그대로
        # 이어붙어 노출되는 문제가 실기기로 확인되어(힌트 포함 여부 판정 자체는 정상
        # 동작하지만 로그가 지저분해짐), 반환 전에 제거한다.
        import re
        title = re.sub(r'\s*(수직|수평) 스크롤 막대,?\s*\d*페이지', '', title).strip()
        return title

    def navigate_back_to_genrehome(self):
        """퀵메뉴 등 하위 화면에서 장르홈으로 뒤로가기"""
        if self.platform == "aos":
            self.driver.back()
        else:
            self.tap_coordinate(20, 69)
        time.sleep(1)
        self.log.info("[뒤로가기] 장르홈 복귀 시도")

    QUICK_MENU_EXPECTED_TITLE = {
        "무료":      "무료",
        "이벤트":     "이벤트",
        "최저가 세트":  "최저가 세트",
        "월간 캘린더": "만화 캘린더",  # 연/월이 동적으로 붙어 포함 여부로 비교 (예: "2026년 7월 만화 캘린더")
        "리디온리":   "RIDI ONLY 만화",
    }

    def verify_quickmenu_destination_title(self, menu_name: str, timeout: int = 6, interval: float = 1.0) -> bool:
        """퀵메뉴 선택 후 진입한 화면의 타이틀이 기대값을 포함하는지 비교 (목적지별 로딩 속도가 달라 재시도).
        페이지 전환 직후 콘텐츠가 아직 로딩 중일 수 있어(더보기 화면과 동일한 이유) 확인 전 5초 대기한다."""
        time.sleep(5)
        expected = self.QUICK_MENU_EXPECTED_TITLE.get(menu_name, "")
        actual = ""
        elapsed = 0.0
        while elapsed <= timeout:
            actual = self.get_current_top_title()
            if expected and expected in actual:
                self.log.info(f"[퀵메뉴타이틀검증] {menu_name} 기대:'{expected}' 실제:'{actual}' ✅")
                return True
            time.sleep(interval)
            elapsed += interval
        self.log.info(f"[퀵메뉴타이틀검증] {menu_name} 기대:'{expected}' 실제:'{actual}' ❌")
        return False

    #섹션별 (방금 본 작품과 비슷한 / 지금 많이 읽고 있는 만화 / 오늘, 리디의 발견 / 구매이력 기반 AI 추천)
    SECTION_LOCATOR = {
        "방금 본 작품과 비슷한":    "SECTION_SIMILAR_RECENT",
        "지금 많이 읽고 있는 만화": "SECTION_READING_NOW",
        "오늘, 리디의 발견":       "SECTION_TODAY_DISCOVERY",
        "구매이력 기반 AI 추천":   "SECTION_AI_PURCHASE",
        # 아래는 장르홈 하단에 이어지는 섹션들. AOS는 UiAutomator textContains 기반 범용
        # is_present 스크롤이 그대로 통하지만, iOS는 위 4개와 동일하게 화면 전체가 하나의
        # 블롭에 뭉쳐 노출되어(실기기 확인됨) IOS_SECTION_SWIPE_COUNT 결정론적 스크롤이 필요하다.
        "오직 리디!":                    "SECTION_RIDI_ONLY",
        "새로 나온 작품":                 "SECTION_NEW_ARRIVALS",
        "만화 베스트":                    "SECTION_BEST",
        "와 비슷한":                      "SECTION_SIMILAR_WORK",  # "<열혈강호>와 비슷한" 등 노출작품에 따라 앞부분이 바뀌는 동적 섹션명 — 고정 접미사만으로 식별
        "웹툰/만화 키워드 검색":            "SECTION_KEYWORD_SEARCH",
        "이벤트":                        "SECTION_EVENT",
        "3분기 애니 원작 총집합!":          "SECTION_SEASONAL",
        "만화를 특가 세트로!":             "SECTION_SPECIAL_SET",
        "앞권 무료로 맛보기!":             "SECTION_FREE_PREVIEW",
        "지금, 리디에서만 볼 수 있는 만화":  "SECTION_RIDI_EXCLUSIVE",
        "2026 상반기 베스트 만화는?":       "SECTION_HALF_YEAR_BEST",
        "인생에 스포츠 만화는 필수입니다.":  "SECTION_SPORTS",
        "그날 인류는 떠올렸다.":           "SECTION_HUMANITY",
        "만화는 리디! 제대로 즐기는 법":    "SECTION_RIDI_GUIDE",
        "별점 5점만점 명예의 전당":         "SECTION_HALL_OF_FAME",
        "역대 만화 대상 수상작 모아보기":    "SECTION_AWARD",
        "이벤트 더 보기":                 "SECTION_EVENT_MORE",
        "님의 취향 저격 AI 추천":          "SECTION_AI_TASTE",  # "41q...님의 취향 저격 AI 추천" 등 계정ID 접두사 제외 고정 접미사로 식별
        # BL 서브탭 전용 섹션 (실기기 확인)
        "BL 키워드 검색":                "SECTION_BL_KEYWORD_SEARCH",
        "BL만화 실시간 랭킹":             "SECTION_BL_RANKING",
        "BL만화 베스트":                 "SECTION_BL_BEST",
        "BL만화 e북 이벤트":              "SECTION_BL_EVENT",
        "지금, 리디에서만 볼 수 있는 BL만화": "SECTION_BL_RIDI_EXCLUSIVE",
        "BL만화 e북 신간":                "SECTION_BL_NEW_ARRIVALS",
    }

    def _iter_text_elements(self):
        """page_source를 파싱해 (y1, x1, y2, x2, text) 목록 반환 (플랫폼 공통 포맷)"""
        import xml.etree.ElementTree as ET
        root = ET.fromstring(self.driver.page_source)
        items = []
        if self.platform == "aos":
            import re
            bounds_pattern = re.compile(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]')
            for elem in root.iter():
                text = (elem.get("text") or "").strip()
                if not text or text in self.PERSISTENT_TAB_LABELS:
                    continue
                m = bounds_pattern.match(elem.get("bounds", ""))
                if not m:
                    continue
                x1, y1, x2, y2 = map(int, m.groups())
                items.append((y1, x1, y2, x2, text))
        else:
            for elem in root.iter():
                text = (elem.get("name") or "").strip()
                if not text or text in self.PERSISTENT_TAB_LABELS:
                    continue
                x1 = int(elem.get("x", 0))
                y1 = int(elem.get("y", -1))
                x2 = x1 + int(elem.get("width", 0))
                y2 = y1 + int(elem.get("height", 0))
                items.append((y1, x1, y2, x2, text))
        return items

    def _section_title_rect(self, section_name: str) -> dict:
        attr = self.SECTION_LOCATOR[section_name]
        el = self.find_element(self._loc(attr))
        loc, size = el.location, el.size
        return {"top": loc["y"], "bottom": loc["y"] + size["height"]}

    # AOS 장르홈은 세로 스크롤 컨테이너(android.widget.ScrollView) 하나와, 그 안에 섹션별
    # 가로 캐러셀(android.widget.HorizontalScrollView)이 여러 개 중첩되어 있다(실기기
    # page_source로 확인됨). `UiSelector().scrollable(true)`만 쓰면 조건에 맞는 첫 위젯이
    # 상황에 따라 세로 컨테이너가 아니라 화면에 걸쳐있는 가로 캐러셀로 잡힐 수 있어(특히 섹션이
    # 화면 하단에 걸친 경우 실기기로 재현됨), 그 가로 캐러셀에 스크롤을 시도하면 이미 끝까지
    # 스크롤된 상태라 제스처가 스크롤 대신 탭으로 처리되어 그 자리의 작품이 실수로 선택/진입되는
    # 사고로 이어진다. className으로 세로 ScrollView를 명시해 이 오탐을 방지한다.
    AOS_VERTICAL_SCROLLVIEW_SELECTOR = 'new UiSelector().className("android.widget.ScrollView")'

    def _vertical_swipe_up(self):
        """세로 스크롤 전용. AOS는 실기기(SM-S937N)에서 원시 좌표 스와이프(driver.swipe)와
        mobile: scrollGesture 둘 다 스크롤을 전혀 일으키지 않는 것이 스크린샷 비교로 여러 번
        확인되어(제스처가 아예 씹힘), Android 표준 스크롤 위젯 API인 UiScrollable로 대체한다
        — 이 방식은 실기기로 스크린샷 비교 검증 완료(반복 호출해도 계속 앞으로 진행됨).
        iOS는 기존 원시 스와이프가 계속 정상 동작해 그대로 유지한다."""
        if self.platform == "aos":
            self.driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                f'new UiScrollable({self.AOS_VERTICAL_SCROLLVIEW_SELECTOR}).scrollForward()'
            )
        else:
            size = self.driver.get_window_size()
            x = int(size["width"] * 0.5)
            self.driver.swipe(x, int(size["height"] * 0.90), x, int(size["height"] * 0.60), 800)
        time.sleep(1)

    def _small_nudge_up(self):
        """타이틀 바로 아래 아이템 행을 렌더링 영역 안으로 끌어오기 위한 소폭 스크롤.
        AOS는 UiScrollable.scrollForward(N)이 이 시점에는 정수 인자값에 따라 완전히 안 움직이거나
        (예: 1) 화면 여러 개를 건너뛸 정도로 과하게 움직이는(예: 인자 없음, 8) 등 세밀한 조정이
        불가능함이 실기기로 확인되어, 원시 좌표 스와이프(driver.swipe)로 대체한다 — 소폭 이동
        용도로는 실기기 스크린샷 비교로 안정적으로 동작 확인됨."""
        size = self.driver.get_window_size()
        x = int(size["width"] * 0.5)
        if self.platform == "aos":
            self.driver.swipe(x, int(size["height"] * 0.60), x, int(size["height"] * 0.42), 800)
        else:
            self.driver.swipe(x, int(size["height"] * 0.85), x, int(size["height"] * 0.70), 600)
        time.sleep(0.8)

    def _small_nudge_down_ios(self):
        """_small_nudge_up의 반대 방향 (iOS에서 과하게 넘어갔을 때 되돌리는 용도, 동일 안전 영역 내)"""
        size = self.driver.get_window_size()
        x = int(size["width"] * 0.5)
        self.driver.swipe(x, int(size["height"] * 0.70), x, int(size["height"] * 0.85), 600)
        time.sleep(0.8)

    def _vertical_swipe_down_ios(self):
        """_vertical_swipe_up의 반대 방향 전체 스크롤. test_003~005처럼 서브탭을 재클릭하지
        않고 이전 테스트가 남긴 스크롤 위치에서 이어서 scroll_to_section을 호출하는 경우,
        목표 섹션을 이미 지나쳐버렸을 수 있어 위로 되돌아가며 재탐색하는 용도로 쓴다.

        AOS는 "방금 본 작품과 비슷한"처럼 개인화 데이터가 없어 아예 노출되지 않는 섹션을
        찾으려다 12회 전진 스크롤을 다 써버리면, 그 상태가 다음 테스트로 그대로 이어져
        이후 섹션들이 이미 지나친 위치에서 계속 못 찾는 연쇄 실패로 이어지는 문제가 실기기로
        확인되어(TestBLtab test_002 이후 전부 실패), iOS 전용이던 이 되돌리기 스크롤을
        AOS(UiScrollable scrollBackward)에도 동일하게 적용한다. 이름은 기존 호출부와의 호환을
        위해 유지."""
        if self.platform == "aos":
            self.driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                f'new UiScrollable({self.AOS_VERTICAL_SCROLLVIEW_SELECTOR}).scrollBackward()'
            )
            time.sleep(1)
            return
        size = self.driver.get_window_size()
        x = int(size["width"] * 0.5)
        self.driver.swipe(x, int(size["height"] * 0.60), x, int(size["height"] * 0.90), 800)
        time.sleep(1)

    # iOS는 이 영역 텍스트가 개별 요소로 분리되지 않고 하나의 XCUIElementTypeOther에 뭉쳐서 노출되어
    # (_section_title_rect가 실제 타이틀 위치가 아닌 뭉친 블롭 전체의 좌표를 반환) 좌표를 동적으로 계산할 수
    # 없다. 실기기 스크린샷으로 실측한 화면비율 좌표를 하드코딩해서 AOS와 동일한 흐름을 흉내낸다.
    IOS_SECTION_ROW_Y_RATIO = {
        "방금 본 작품과 비슷한":    0.521,
        "지금 많이 읽고 있는 만화": 0.395,
        "오늘, 리디의 발견":       0.695,
        "구매이력 기반 AI 추천":   0.404,
        "오직 리디!":                    0.55,
        "새로 나온 작품":                 0.60,
        "만화 베스트":                    0.60,
        "와 비슷한":                      0.65,
        "웹툰/만화 키워드 검색":            0.62,
        "이벤트":                        0.62,
        "3분기 애니 원작 총집합!":          0.60,
        "만화를 특가 세트로!":             0.58,
        "앞권 무료로 맛보기!":             0.75,
        "지금, 리디에서만 볼 수 있는 만화":  0.70,
        "2026 상반기 베스트 만화는?":       0.65,
        "인생에 스포츠 만화는 필수입니다.":  0.60,
        "그날 인류는 떠올렸다.":           0.57,
        "만화는 리디! 제대로 즐기는 법":    0.73,
        "별점 5점만점 명예의 전당":         0.72,
        "역대 만화 대상 수상작 모아보기":    0.68,
        "이벤트 더 보기":                 0.63,
        "님의 취향 저격 AI 추천":          0.63,
    }
    IOS_SECTION_MORE_COORD_RATIO = {
        "지금 많이 읽고 있는 만화": (0.915, 0.328),
        "구매이력 기반 AI 추천":   (0.915, 0.284),
        "오직 리디!":                    (0.932, 0.490),
        "새로 나온 작품":                 (0.932, 0.484),
        "만화 베스트":                    (0.932, 0.545),
        "웹툰/만화 키워드 검색":            (0.932, 0.539),
        "이벤트":                        (0.932, 0.551),
        "3분기 애니 원작 총집합!":          (0.932, 0.537),
        "만화를 특가 세트로!":             (0.932, 0.498),
        "앞권 무료로 맛보기!":             (0.932, 0.671),
        "지금, 리디에서만 볼 수 있는 만화":  (0.932, 0.618),
        "2026 상반기 베스트 만화는?":       (0.932, 0.557),
        "인생에 스포츠 만화는 필수입니다.":  (0.932, 0.517),
        "그날 인류는 떠올렸다.":           (0.932, 0.482),
        "만화는 리디! 제대로 즐기는 법":    (0.932, 0.660),
        "별점 5점만점 명예의 전당":         (0.932, 0.640),
        "역대 만화 대상 수상작 모아보기":    (0.932, 0.603),
        "이벤트 더 보기":                 (0.932, 0.563),
        # "이 작품을 주목!" / "와 비슷한" / "님의 취향 저격 AI 추천"은 더보기 버튼 자체가 없음
        # BL 서브탭 전용 섹션 (실기기 확인, 섹션별로 진행 중). "방금 본 작품과 비슷한"이
        # BL탭 첫 섹션으로 추가된 뒤(계정에 열람 이력이 있으면 실제 콘텐츠로 렌더링됨),
        # 그 아래 있는 이 두 섹션이 화면상 더 아래로 밀려 기존 좌표가 STAGE 이벤트 띠지
        # 근처의 엉뚱한 책 카드를 오탭하는 문제가 실기기로 확인되어(더보기 목적지 타이틀이
        # 빈 값이거나 책 제목으로 잡힘) 재보정한다.
        "BL 키워드 검색":                (0.910, 0.662),
        "BL만화 실시간 랭킹":             (0.910, 0.672),
        "BL만화 베스트":                 (0.913, 0.502),
        "BL만화 e북 이벤트":              (0.913, 0.531),
        "지금, 리디에서만 볼 수 있는 BL만화": (0.913, 0.553),
        "BL만화 e북 신간":                (0.913, 0.506),
    }
    # BL 서브탭처럼 "추천" 서브탭이 아닌 다른 서브탭에 속한 섹션은 여기 등록한다.
    # _ios_scroll_to_section_deterministic이 결정론적 스크롤 전에 어느 서브탭을 눌러야
    # 하는지 판단하는 데 쓰인다 - 등록 안 된 섹션은 기존과 동일하게 "추천"으로 간주.
    IOS_SECTION_SUBTAB = {
        "BL 키워드 검색":                "BL",
        "BL만화 실시간 랭킹":             "BL",
        "BL만화 베스트":                 "BL",
        "BL만화 e북 이벤트":              "BL",
        "지금, 리디에서만 볼 수 있는 BL만화": "BL",
        "BL만화 e북 신간":                "BL",
    }
    # 더보기 클릭 후 실제 도달해야 하는 목적지 화면 타이틀에 포함되어야 하는 힌트 문자열.
    # "구매이력 기반 AI 추천"의 실제 타이틀은 "{아이디}님의 구매이력 기반 AI 추천"처럼 계정별로
    # 앞부분(계정ID)만 유동적이고 뒷부분은 고정이라, 그 고정 접미사로 확인한다. 아래 신규 섹션들은
    # 계정ID 등 유동 접두사가 없어 섹션명 자체가 곧 목적지 타이틀이다.
    IOS_SECTION_MORE_DEST_HINT = {
        "지금 많이 읽고 있는 만화": "지금 많이 읽고 있는 만화",
        "구매이력 기반 AI 추천":   "구매이력 기반 AI 추천",
        # "오직 리디!"의 더보기 목적지 화면 실제 타이틀은 "오직 리디!"가 아니라 "이벤트"다
        # (실기기로 확인됨 — 이 섹션이 이벤트 목록 화면으로 연결됨).
        "오직 리디!":                    "이벤트",
        # "새로 나온 작품"/"만화 베스트"는 목적지 화면 타이틀 추출이 불안정해 힌트를 두지
        # 않는다 — 테스트 쪽에서 타이틀 대신 "전체" 필터 탭 노출 여부로 검증한다
        # (is_all_filter_visible, verify_all_button 참고).
        "웹툰/만화 키워드 검색":            "웹툰/만화 키워드 검색",
        "이벤트":                        "이벤트",
        "3분기 애니 원작 총집합!":          "3분기 애니 원작 총집합!",
        "만화를 특가 세트로!":             "만화를 특가 세트로!",
        "앞권 무료로 맛보기!":             "앞권 무료로 맛보기!",
        # "지금, 리디에서만 볼 수 있는 만화"의 더보기 목적지 실제 타이틀은 섹션명이 아니라
        # "RIDI ONLY 만화"다(aos/ios 공통, "만화" 탭이 활성화된 채로 노출됨 — 실기기 확인됨).
        "지금, 리디에서만 볼 수 있는 만화":  "RIDI ONLY 만화",
        "2026 상반기 베스트 만화는?":       "2026 상반기 베스트 만화는?",
        "인생에 스포츠 만화는 필수입니다.":  "인생에 스포츠 만화는 필수입니다.",
        "그날 인류는 떠올렸다.":           "그날 인류는 떠올렸다.",
        "만화는 리디! 제대로 즐기는 법":    "만화는 리디! 제대로 즐기는 법",
        "별점 5점만점 명예의 전당":         "별점 5점만점 명예의 전당",
        "역대 만화 대상 수상작 모아보기":    "역대 만화 대상 수상작 모아보기",
        "이벤트 더 보기":                 "이벤트 더 보기",
        # BL 서브탭 전용 섹션 (실기기 확인, 섹션별로 진행 중)
        "BL 키워드 검색":                "BL 키워드 검색",
        "BL만화 실시간 랭킹":             "BL만화 실시간 랭킹",
        "BL만화 베스트":                 "BL만화 베스트",
        # "BL만화 e북 이벤트"의 더보기 목적지 실제 타이틀은 섹션명이 아니라 "이벤트"다
        # ("오직 리디!"와 동일한 이벤트 목록 화면으로 연결됨 — 실기기 확인됨).
        "BL만화 e북 이벤트":              "이벤트",
        # "지금, 리디에서만 볼 수 있는 BL만화"의 더보기 목적지 실제 타이틀은 섹션명이 아니라
        # "RIDI ONLY BL 웹툰/만화"다("BL 만화" 탭이 활성화된 채로 노출됨 — 실기기 확인됨).
        "지금, 리디에서만 볼 수 있는 BL만화": "RIDI ONLY BL 웹툰/만화",
        "BL만화 e북 신간":                "BL만화 e북 신간",
    }
    # "방금 본 작품과 비슷한"/"지금 많이 읽고 있는 만화"/"오늘, 리디의 발견"/"구매이력 기반 AI 추천"은
    # is_present 기반 스크롤 판별이 통하지 않아(아래 scroll_to_section 설명 참고) 절대 최상단에서부터
    # 고정 스와이프 횟수로 도달한다. 값은 (절대 최상단 도달 후 배너 영역을 벗어나기 위한 1회 탈출
    # 스와이프) + (추가 큰 스와이프 횟수). "구매이력 기반 AI 추천"은 화면 우측에 항상 떠 있는
    # STAGE 이벤트 띠지가 타이틀/더보기 행과 겹치는 스크롤 깊이(6회)에서는 오탭이 반복돼,
    # 띠지가 완전히 아래로 내려가 겹치지 않는 깊이(7회)까지 더 내려간다. 아래 신규 섹션들도
    # 실기기(Appium MCP)로 최상단부터 순서대로 스와이프하며 실측한 값이다.
    IOS_SECTION_SWIPE_COUNT = {
        "방금 본 작품과 비슷한":    1,
        "지금 많이 읽고 있는 만화": 3,
        "오늘, 리디의 발견":       4,
        "구매이력 기반 AI 추천":   7,
        "오직 리디!":                    8,
        "새로 나온 작품":                 9,
        "만화 베스트":                    12,
        "와 비슷한":                      14,
        "웹툰/만화 키워드 검색":            16,
        "이벤트":                        17,
        "3분기 애니 원작 총집합!":          18,
        "만화를 특가 세트로!":             20,
        "앞권 무료로 맛보기!":             21,
        "지금, 리디에서만 볼 수 있는 만화":  23,
        "2026 상반기 베스트 만화는?":       27,
        "인생에 스포츠 만화는 필수입니다.":  29,
        "그날 인류는 떠올렸다.":           31,
        "만화는 리디! 제대로 즐기는 법":    32,
        "별점 5점만점 명예의 전당":         33,
        "역대 만화 대상 수상작 모아보기":    35,
        "이벤트 더 보기":                 37,
        "님의 취향 저격 AI 추천":          38,
        # BL 서브탭 전용 섹션 (실기기 확인, 섹션별로 진행 중) - "배너/퀵메뉴 영역을 벗어나는
        # 첫 스와이프" 이후 추가로 필요한 스와이프 횟수
        # "BL 키워드 검색"은 "방금 본 작품과 비슷한"이 실제 콘텐츠로 렌더링되는 계정에서
        # 기존 0회로는 섹션이 화면 맨 아래 거의 잘린 채로만 보여 더보기 오탭으로 이어져
        # (실기기 확인) 1회로 상향한다.
        "BL 키워드 검색":                1,
        "BL만화 실시간 랭킹":             2,
        # "BL만화 실시간 랭킹"이 매 진입마다 콘텐츠(순위 항목)가 바뀌는 실시간 섹션이라
        # 아래 섹션들 위치가 실행마다 미묘하게 밀리는 것이 실기기로 확인됨 - 안전 마진을
        # 위해 다른 정적 섹션들보다 여유있게 잡음.
        "BL만화 베스트":                 5,
        "BL만화 e북 이벤트":              7,
        "지금, 리디에서만 볼 수 있는 BL만화": 9,
        "BL만화 e북 신간":                11,
    }
    # 섹션 콘텐츠 블롭에서 "다음 섹션이 시작되는 지점"을 잘라내기 위한 마커들.
    # "더보기"는 여기 넣지 않는다 — 더보기 버튼이 있는 모든 섹션은 타이틀 바로 뒤에 자신의
    # "더보기"가 오므로(아이템보다 앞), 범용 마커로 넣으면 모든 섹션의 콘텐츠가 추출 시작
    # 지점에서 바로 잘려 항상 빈 문자열이 되는 문제가 있었다(실기기로 확인, 아래
    # _get_ios_section_content의 앵커 처리로 대신 해결).
    IOS_SECTION_END_MARKERS = [
        "방금 본 작품과 비슷한", "지금 많이 읽고 있는 만화", "오늘, 리디의 발견",
        "구매이력 기반 AI 추천", "오직 리디!", "새로 나온 작품",
        "이 작품을 주목", "만화 베스트", "와 비슷한", "웹툰/만화 키워드 검색",
        "이벤트 더 보기", "이벤트", "3분기 애니 원작 총집합!", "만화를 특가 세트로!",
        "앞권 무료로 맛보기!", "지금, 리디에서만 볼 수 있는 만화", "NEW | 7월의 주목 신작!",
        "2026 상반기 베스트 만화는?", "인생에 스포츠 만화는 필수입니다.",
        "그날 인류는 떠올렸다.", "만화는 리디! 제대로 즐기는 법", "별점 5점만점 명예의 전당",
        "역대 만화 대상 수상작 모아보기", "님의 취향 저격 AI 추천", "리디(주)",
        # BL 서브탭 전용 섹션
        "BL 키워드 검색", "BL만화 실시간 랭킹", "BL만화 베스트", "BL만화 e북 이벤트",
        "지금, 리디에서만 볼 수 있는 BL만화", "BL만화 e북 신간",
    ]

    def _get_ios_section_content(self, section_name: str) -> str:
        """iOS는 이 영역 텍스트가 개별 요소로 안 잡히고 하나의 블롭(XCUIElementTypeOther)에
        화면 노출 순서 그대로 이어붙여져서 노출된다. 좌표 대신 문자열 파싱으로 해당 섹션 이름
        직후 ~ 다음 마커 전까지의 원문 조각을 추출한다 (개별 아이템 구분은 아니지만 실제 노출된
        콘텐츠 원문). 전체 page_source 덤프(_iter_text_elements)는 자동재생 배너가 있는 이
        화면에서 WDA가 반복적으로 120초 타임아웃/hang을 일으켜, 대신 해당 블롭 요소 하나만
        직접 조회한다 (scroll_to_section의 is_present와 동일하게 가벼운 타겟 조회).

        더보기 버튼이 있는 섹션은 앵커를 "{섹션명} 더보기"로 잡는다 — 더보기 버튼이 타이틀
        바로 뒤, 실제 아이템들보다 앞에 오는 접근성 순서라 섹션명만 앵커로 쓰면 그 뒤에 오는
        "더보기" 텍스트에서 곧바로 다음 섹션으로 오인돼 잘리기 때문. 부가효과로 "이벤트"처럼
        섹션명이 퀵메뉴 라벨(무료/이벤트/최저가 세트/월간 캘린더)에도 동일 문자열로 포함돼
        앞쪽의 잘못된 위치를 찾아버리는 경우도, 퀵메뉴 라벨 뒤에는 "더보기"가 없어 이 앵커가
        자동으로 올바른(진짜 섹션 타이틀) 위치를 찾아낸다."""
        try:
            attr = self.SECTION_LOCATOR[section_name]
            # _wait_ios_section_loaded가 콘텐츠 로딩 완료까지 반복 폴링하는 정상적인
            # 흐름에서, find_element(예외 시 ERROR 로그)를 쓰면 로딩 대기 중 매 시도마다
            # "요소 없음" ERROR가 반복 출력되어 실제 문제처럼 보이는 로그 노이즈가 실기기로
            # 확인되어, 예외를 던지지 않는 find_elements로 조용히 존재 확인한다.
            found = self.find_elements(self._loc(attr))
            blob = found[0].get_attribute("name") if found else ""
            blob = blob or ""
            if not blob:
                return ""
            anchor = f"{section_name} 더보기" if section_name in self.IOS_SECTION_MORE_COORD_RATIO else section_name
            idx = blob.find(anchor)
            after = blob[idx + len(anchor):]
            end = len(after)
            for marker in self.IOS_SECTION_END_MARKERS:
                if marker == section_name:
                    continue
                pos = after.find(marker)
                if pos != -1:
                    end = min(end, pos)
            return after[:end].strip()
        except Exception as e:
            self.log.warning(f"[_get_ios_section_content] {section_name} 콘텐츠 추출 실패: {e}")
            return ""

    @staticmethod
    def _split_ios_ranked_items(content: str) -> list:
        """"지금 많이 읽고 있는 만화"처럼 "{순위} {제목} ... {평점} ({평가수})"가 이어붙은
        랭킹 블롭 문자열을, 각 항목이 ") {다음 순위} " 뒤에서 시작한다는 규칙으로 순위별
        항목으로 분리한다."""
        import re
        bounds = [0] + [m.start(1) for m in re.finditer(r'\)\s+(\d{1,3})\s', content)]
        bounds.append(len(content))
        items = []
        for i in range(len(bounds) - 1):
            seg = content[bounds[i]:bounds[i + 1]].strip()
            if seg:
                items.append(seg)
        return items

    def _split_ios_card_items(self, section_name: str, content: str) -> list:
        """"{제목} {저자} {평점} ({평가수})"가 순위 번호 없이 이어붙은 일반 카드 리스트
        블롭을, "(평가수)" 뒤에서 다음 카드가 시작한다는 규칙으로 개별 항목으로 분리한다.
        이 패턴이 아예 없는 콘텐츠(프로모션 배너형 섹션 등)나 IOS_SECTION_NO_CARD_SPLIT에
        등록된 섹션(카드마다 평가수 뒤에 태그 등 부가 메타데이터가 더 붙어 경계 규칙이 안
        맞는 경우)은 분리되지 않고 원문 그대로 한 덩어리로 반환된다."""
        if not content:
            return []
        if section_name in self.IOS_SECTION_NO_CARD_SPLIT:
            return [content]
        import re
        bounds = [0] + [m.end() for m in re.finditer(r'\(\d[\d,]*\)', content)]
        if bounds[-1] != len(content):
            bounds.append(len(content))
        items = []
        for i in range(len(bounds) - 1):
            seg = content[bounds[i]:bounds[i + 1]].strip()
            if seg:
                items.append(seg)
        return items

    def _ios_scroll_to_section_deterministic(self, section_name: str, subtab_name: str = "추천") -> bool:
        """iOS 전용: is_present 기반 스크롤 판별이 통하지 않는 섹션("방금 본 작품과 비슷한",
        "지금 많이 읽고 있는 만화", "오늘, 리디의 발견")을 위한 결정론적 스크롤.

        이 화면은 스크롤 위치와 무관하게 페이지 전체 텍스트가 하나의 접근성 블롭 요소에 뭉쳐서
        노출되어(x=0,y=0,전체화면 크기 bounds), textContains 기반 is_present가 스크롤을 전혀
        안 해도 항상 True를 반환한다 — 즉 "존재 확인으로 스크롤 완료 판단"이 원천적으로 불가능하다.
        게다가 최상단(빅배너+퀵메뉴가 보이는 상태)에서는 느린 드래그가 배너/퀵메뉴 캐러셀에
        제스처를 뺏겨 스크롤이 전혀 먹히지 않는다.

        따라서 매번 딥링크로 절대 최상단부터 다시 시작해, 배너 영역을 벗어나는 첫 스와이프 +
        섹션별로 실기기에서 실측한 고정 횟수의 추가 스와이프로 원하는 스크롤 깊이에 도달한다.
        실기기(Appium MCP)로 동일 좌표/횟수를 그대로 재현하면 매번 정확히 도달하는 것으로
        확인되어 좌표값 자체는 정확하다. 다만 "더보기" 자체는 iOS 접근성 트리에 개별 요소로
        존재하지 않아(전체가 블롭 하나) 버튼의 실제 좌표(rect)를 직접 조회할 방법이 없으므로,
        유일하게 신뢰 가능한 위치 확인 수단인 "섹션 콘텐츠 텍스트가 블롭에 채워졌는가"
        (_wait_ios_section_loaded)의 결과를 그대로 반환해, 호출측이 이 확인 없이는 좌표 탭을
        강행하지 않도록 한다.

        딥링크 재진입 직후 빅배너가 아직 로딩/전환 애니메이션 중일 때 스와이프를 시작하면
        스크롤 이동 거리가 매번 미세하게 달라져(특히 스와이프 횟수가 많은 섹션일수록 오차가
        누적됨) 목적지를 지나치거나 못 미치는 문제가 있었다. 화면이 완전히 정지한 뒤에
        스와이프를 시작하도록 충분히 대기한다.

        실기기로 직접 확인한 결과, 이미 장르홈 화면에 있는 상태에서 딥링크로 재진입해도
        스크롤 위치가 최상단으로 리셋되지 않는다 (앱이 "이미 이 화면"으로 판단해 그대로 유지).
        재시도가 반복될수록 이전 위치 위에 스와이프가 누적돼 엉뚱한 섹션까지 밀려 내려가는
        사고로 이어졌다 — 상태바를 탭하면(iOS 표준 동작) 최상단 스크롤뷰가 즉시 맨 위로
        리셋되는 것을 실기기로 확인해, 스와이프 시작 전에 항상 이 방법으로 절대 위치를
        보정한다.

        subtab_name: 섹션이 속한 서브탭("추천" 기본값, BL 등 다른 서브탭 섹션은
        IOS_SECTION_SUBTAB에 등록되어 scroll_to_section 호출측에서 결정해 전달한다)."""
        self.enter_comic_genrehome()
        time.sleep(2.5)
        self.click_subtab(subtab_name, log=False)
        time.sleep(2)

        size = self.driver.get_window_size()
        x = int(size["width"] * 0.5)
        h = size["height"]

        # 딥링크 재진입이 스크롤을 리셋해주지 않으므로, 상태바 탭으로 절대 최상단을 보정한다.
        self.tap_coordinate(x, 10)
        time.sleep(1)

        # 배너/퀵메뉴 캐러셀 영역을 벗어나는 첫 스와이프 (배너 아래 지점에서 시작)
        self.driver.swipe(x, int(h * 0.746), x, int(h * 0.533), 600)
        time.sleep(1.3)

        for _ in range(self.IOS_SECTION_SWIPE_COUNT.get(section_name, 0)):
            self.driver.swipe(x, int(h * 0.829), x, int(h * 0.592), 600)
            time.sleep(1.3)

        # 네트워크 응답이 느리면 콘텐츠 로딩이 10초를 훌쩍 넘기는 경우가 실기기에서 확인되어,
        # 섣불리 포기하지 않도록 기본(10초)보다 훨씬 넉넉하게 기다린다.
        return self._wait_ios_section_loaded(section_name, timeout=30.0)

    def _wait_ios_section_loaded(self, section_name: str, timeout: float = 10.0, interval: float = 1.0) -> bool:
        """네트워크가 느리면 스크롤을 다 마친 시점에도 목표 섹션이 스켈레톤(빈 로딩 placeholder)
        상태라 실제 콘텐츠 텍스트가 블롭에 아직 채워지지 않은 경우가 있다. 이 상태에서 좌표
        기반으로 더보기를 탭하면 실제 콘텐츠가 로드되며 레이아웃이 밀려 오탭으로 이어진다.
        섹션의 실제 콘텐츠 문자열이 블롭에 채워질 때까지(스켈레톤 탈출) 짧게 재확인하며 대기한다."""
        attr = self.SECTION_LOCATOR.get(section_name)
        if not attr:
            return True
        elapsed = 0.0
        while elapsed <= timeout:
            try:
                if self._get_ios_section_content(section_name):
                    return True
            except Exception:
                pass
            time.sleep(interval)
            elapsed += interval
        self.log.warning(f"[_wait_ios_section_loaded] {section_name} 콘텐츠 로딩 대기 시간초과({timeout}s) - 스켈레톤 상태일 수 있음")
        return False

    def scroll_to_section(self, section_name: str, max_scroll: int = 12, safe_margin_ratio: float = 0.45,
                           subtab_name: str = None) -> bool:
        """섹션 타이틀이 보이고, 아이템 행도 렌더링될 만큼 스크롤.
        safe_margin_ratio: AOS 보정 스크롤 종료 기준(타이틀 하단이 화면의 이 비율보다 위에
        있어야 종료). 일부 섹션은 기본값(0.45)만으로는 화면 하단에 걸친 채로 남아 더보기
        탭 오차로 이어져("BL만화 실시간 랭킹" 등 실기기 확인됨), 호출측에서 더 낮은 값을
        넘겨 더 확실하게 위로 끌어올릴 수 있게 한다. 기본값은 기존 동작과 동일.
        subtab_name: "방금 본 작품과 비슷한"처럼 여러 서브탭(추천/BL 등)에 동일한 이름으로
        존재하는 섹션은 IOS_SECTION_SUBTAB 사전 하나로 서브탭을 구분할 수 없어(호출하는
        테스트 클래스에 따라 다름), 이 값이 주어지면 사전 조회보다 우선한다."""
        if self.platform == "ios" and section_name in self.IOS_SECTION_SWIPE_COUNT:
            resolved_subtab = subtab_name or self.IOS_SECTION_SUBTAB.get(section_name, "추천")
            self._ios_scroll_to_section_deterministic(section_name, resolved_subtab)
            return True

        attr = self.SECTION_LOCATOR[section_name]
        locator = self._loc(attr)
        found = False
        for _ in range(max_scroll):
            if self.is_present(locator, timeout=2):
                found = True
                break
            self._vertical_swipe_up()
        if not found:
            found = self.is_present(locator, timeout=2)

        if not found:
            # 아래로만 스크롤해서 못 찾았다면, 서브탭 재클릭 없이 이전 테스트의 스크롤 위치를
            # 이어받는 케이스(test_003~005)에서 이미 섹션을 지나쳐버린 경우일 수 있다.
            # 위로 되돌아가며 재탐색한다. AOS도 "방금 본 작품과 비슷한"처럼 개인화 데이터가
            # 없어 아예 없는 섹션을 찾다 전진 스크롤을 다 써버리면 이후 테스트까지 연쇄로
            # 못 찾는 문제가 실기기로 확인되어(원래 iOS 전용이었음) 동일하게 적용한다.
            for _ in range(max_scroll):
                self._vertical_swipe_down_ios()
                if self.is_present(locator, timeout=2):
                    found = True
                    break

        if not found:
            return False

        if self.platform == "ios":
            # iOS는 _section_title_rect가 뭉친 블롭 좌표를 반환해 AOS 방식(rect 기반) 미세조정은
            # 못 쓰지만, is_present가 True로 뜬 시점엔 섹션이 화면 하단에 걸쳐만 있는 경우가 많아
            # 좌우스와이프 전에 화면 안쪽으로 들어오도록 소폭 추가 스크롤 1회는 항상 수행한다.
            self._small_nudge_up()
            if not self.is_present(locator, timeout=2):
                # 너무 많이 넘어가서 섹션이 사라졌으면 되돌림
                self._small_nudge_down_ios()
            return True

        # 타이틀이 화면 하단에 걸쳐 있으면 아이템 행이 아직 렌더링 안 됐을 수 있어 소폭 추가 스크롤.
        # ("오늘, 리디의 발견" 섹션에서 이 보정 스크롤이 다른 화면으로 이탈시키던 문제는
        # _small_nudge_up의 스크롤 대상 위젯 모호성이 근본 원인이었고 이미 그쪽에서 수정됨 -
        # 매 섹션마다 별도 이탈 감지를 반복할 필요가 없어 제거함.)
        h = self.driver.get_window_size()["height"]
        for _ in range(3):
            rect = self._section_title_rect(section_name)
            if rect["bottom"] < h * safe_margin_ratio:
                break
            self._small_nudge_up()
            if not self.is_present(locator, timeout=2):
                break
        return True

    def _section_item_row_y(self, section_name: str):
        """섹션 타이틀 바로 아래에서 가장 먼저 나오는 아이템 행의 y좌표(스와이프/조회 기준) 반환.
        타이틀과 같은 줄에 붙어있는 "총 N권" 같은 배지 텍스트를 아이템으로 오인하지 않도록
        타이틀 바로 아래 60px 이내는 제외한다."""
        if self.platform == "ios":
            ratio = self.IOS_SECTION_ROW_Y_RATIO.get(section_name, 0.5)
            return int(self.driver.get_window_size()["height"] * ratio)
        rect = self._section_title_rect(section_name)
        top = rect["bottom"] + 60
        candidates = [e for e in self._iter_text_elements() if top < e[0] < rect["bottom"] + 900]
        if not candidates:
            return None
        return min(c[0] for c in candidates)

    def swipe_section_left(self, section_name: str, wide: bool = False):
        """wide=True는 순위 항목이 많은 섹션(BL만화 실시간 랭킹/베스트 등)에서 스와이프
        횟수는 유지한 채 1회당 이동 폭만 넓히기 위한 옵션 - 기본값은 기존 폭(0.80~0.20) 그대로라
        다른 호출부에 영향 없다."""
        w = self.driver.get_window_size()["width"]
        y = self._section_item_row_y(section_name) or (self._section_title_rect(section_name)["bottom"] + 100)
        start, end = (0.90, 0.10) if wide else (0.80, 0.20)
        self.driver.swipe(int(w * start), y, int(w * end), y, 500)
        time.sleep(0.5)

    def swipe_section_right(self, section_name: str, wide: bool = False):
        w = self.driver.get_window_size()["width"]
        y = self._section_item_row_y(section_name) or (self._section_title_rect(section_name)["bottom"] + 100)
        start, end = (0.10, 0.90) if wide else (0.20, 0.80)
        self.driver.swipe(int(w * start), y, int(w * end), y, 500)
        time.sleep(0.5)

    def get_section_item_names(self, section_name: str) -> list:
        """현재 화면에 보이는 섹션 아이템들의 대표 텍스트(카드 첫 줄) 목록 반환 (x좌표 순)"""
        if self.platform == "ios":
            content = self._get_ios_section_content(section_name)
            if section_name in self.IOS_SWIPE_RANKED_SECTIONS:
                # 랭킹 리스트는 순위별로 분리해, 1위/마지막 순위 항목이 개별적으로 확인되게 한다.
                return self._split_ios_ranked_items(content)
            # 개별 아이템 좌표 구분은 불가하지만, "(평가수)" 경계로 카드 단위 분리를 시도한다
            # (프로모션 배너형 섹션 등 이 패턴이 없거나 안 맞는 섹션은 한 덩어리로 반환됨).
            return self._split_ios_card_items(section_name, content)
        top_y = self._section_item_row_y(section_name)
        if top_y is None:
            return []
        band = [e for e in self._iter_text_elements() if abs(e[0] - top_y) <= 40]
        band.sort(key=lambda e: e[1])
        names, last_x = [], None
        for y1, x1, y2, x2, text in band:
            if last_x is not None and x1 - last_x < 100:
                continue
            names.append(text.replace("\n", " "))
            last_x = x1
        return names

    # "지금 많이 읽고 있는 만화"는 다른 섹션과 달리 순위(1위~)가 매겨진 랭킹 리스트 UI로,
    # 실기기로 확인한 결과 좌우 스와이프로 페이지가 실제 전환되며 다음 순위가 노출된다
    # (다른 섹션들의 "블롭은 스와이프해도 안 바뀐다"는 일반 원칙과 다름).
    IOS_SWIPE_RANKED_SECTIONS = {"지금 많이 읽고 있는 만화"}
    # "구매이력 기반 AI 추천"은 카드마다 평점(개수) 뒤에 "비슷한 작품"/"#태그" 같은 부가
    # 메타데이터가 더 붙어있어(실기기로 확인됨), "(평가수) 뒤가 곧 다음 카드"라는
    # _split_ios_card_items의 경계 규칙이 안 맞아 항목이 태그 조각으로 잘못 쪼개진다.
    # 안전하게 분리하지 않고 블롭 원문 그대로 한 덩어리로 취급한다.
    IOS_SECTION_NO_CARD_SPLIT = {"구매이력 기반 AI 추천"}

    def collect_section_items_by_swipe(self, section_name: str, max_swipes: int = 6, wide: bool = False):
        """섹션을 좌스와이프하며 아이템을 중복없이 순서대로 수집. (수집목록, 스와이프횟수) 반환.
        wide=True는 순위 항목이 많은 섹션에서 스와이프 횟수(max_swipes)는 그대로 두고 1회당
        이동 폭만 넓히기 위한 옵션(swipe_section_left/right로 그대로 전달) - 기본값은 기존과
        동일해 다른 호출부에 영향 없다."""
        if self.platform == "ios" and section_name in self.IOS_SWIPE_RANKED_SECTIONS:
            seen, ordered = set(), []
            for item in self._split_ios_ranked_items(self._get_ios_section_content(section_name)):
                if item not in seen:
                    seen.add(item)
                    ordered.append(item)

            stall = 0
            swipe_count = 0
            while swipe_count < max_swipes and (swipe_count < 3 or stall < 2):
                self.swipe_section_left(section_name, wide=wide)
                swipe_count += 1
                newly = 0
                for item in self._split_ios_ranked_items(self._get_ios_section_content(section_name)):
                    if item not in seen:
                        seen.add(item)
                        ordered.append(item)
                        newly += 1
                stall = 0 if newly else stall + 1
            return ordered, swipe_count

        if self.platform == "ios":
            # 실기기 확인 결과 블롭은 스와이프해도 내용이 안 바뀌는 경우가 많지만, 좌우스와이프
            # 동작 자체는 섹션별로 최소 5회 무조건 수행한다(사용자 지시 — 서브탭 누수 등
            # 이전에 확인된 위험을 감수하고서라도 스와이프 동작 자체를 항상 검증하길 원함).
            # 일부 섹션("오직 리디!" 등 프로모션 배너형)은 스와이프할수록 블롭에 새 배너가
            # 계속 이어붙는 "누적 성장형" 구조라(실기기로 확인됨), 매번 전체 블롭을 다시
            # 분리하면 이미 본 접두사가 매번 새 항목처럼 겹쳐 보이는 문제가 있었다. 그래서
            # 이전에 읽은 블롭과 비교해 새로 늘어난 부분(delta)만 카드 단위로 분리해 추가한다.
            seen, ordered = set(), []
            last_content = ""

            def add_new_content(content):
                nonlocal last_content
                if not content or content == last_content:
                    return
                delta = content[len(last_content):].strip() if content.startswith(last_content) else content
                last_content = content
                for item in self._split_ios_card_items(section_name, delta):
                    # 스와이프를 여러 번 반복하면 블롭이 화면 하단 탭바("도구 막대 내 서재
                    # 검색 홈 알림 MY")까지 누적해 마지막 카드 뒤에 그대로 붙는 문제가
                    # 실기기로 확인되어("BL만화 e북 신간" 마지막 작품 오탐), 제외한다.
                    if "도구 막대" in item:
                        continue
                    if item not in seen:
                        seen.add(item)
                        ordered.append(item)

            add_new_content(self._get_ios_section_content(section_name))

            swipe_count = 5
            for _ in range(swipe_count):
                self.swipe_section_left(section_name, wide=wide)
                add_new_content(self._get_ios_section_content(section_name))
            return ordered, swipe_count

        seen, ordered = set(), []
        for name in self.get_section_item_names(section_name):
            if name not in seen:
                seen.add(name)
                ordered.append(name)

        stall = 0
        swipe_count = 0
        while stall < 2 and swipe_count < max_swipes:
            self.swipe_section_left(section_name, wide=wide)
            swipe_count += 1
            newly = 0
            for name in self.get_section_item_names(section_name):
                if name not in seen:
                    seen.add(name)
                    ordered.append(name)
                    newly += 1
            stall = 0 if newly else stall + 1
        return ordered, swipe_count

    def is_section_more_visible(self, section_name: str) -> bool:
        """섹션 타이틀과 같은 행에 있는 [더보기] 버튼 존재 여부 (다른 섹션 더보기와 혼동 방지)"""
        if self.platform == "ios":
            return section_name in self.IOS_SECTION_MORE_COORD_RATIO
        rect = self._section_title_rect(section_name)
        return any(
            text == "더보기" and y1 < rect["bottom"] and y2 > rect["top"]
            for y1, x1, y2, x2, text in self._iter_text_elements()
        )

    def click_section_more(self, section_name: str) -> bool:
        """섹션 타이틀과 같은 행의 [더보기] 버튼 클릭. iOS는 콘텐츠 로딩이 확인되지 않으면
        (더보기 실제 위치를 신뢰할 수 없는 상태이므로) 탭을 강행하지 않고 False를 반환한다 —
        호출측(click_section_more_and_verify)이 장르홈에 그대로 머문 채 재시도한다."""
        if self.platform == "ios":
            # collect_section_items_by_swipe가 좌우로 왕복 스와이프(최대 16회)를 수행하는 동안
            # 세로 스크롤 위치가 미세하게 밀릴 수 있어, 더보기 좌표가 실제 버튼을 벗어나 바로
            # 아래 책 표지를 오탭하는 사고가 있었다. 탭 직전에 결정론적 스크롤을 한 번 더 수행해
            # 좌표 기준 위치를 항상 깨끗하게 재보정한 뒤 탭한다.
            if section_name in self.IOS_SECTION_SWIPE_COUNT:
                subtab_name = self.IOS_SECTION_SUBTAB.get(section_name, "추천")
                if not self._ios_scroll_to_section_deterministic(section_name, subtab_name):
                    self.log.warning(f"[섹션더보기클릭] {section_name} 콘텐츠 로딩 미확인 - 탭 보류")
                    return False
            ratio = self.IOS_SECTION_MORE_COORD_RATIO[section_name]
            size = self.driver.get_window_size()
            self.tap_coordinate(int(size["width"] * ratio[0]), int(size["height"] * ratio[1]))
            self.log.info(f"[섹션더보기클릭] {section_name} (iOS 좌표 기반)")
            return True
        rect = self._section_title_rect(section_name)
        for y1, x1, y2, x2, text in self._iter_text_elements():
            if text == "더보기" and y1 < rect["bottom"] and y2 > rect["top"]:
                self.tap_coordinate((x1 + x2) // 2, (y1 + y2) // 2)
                self.log.info(f"[섹션더보기클릭] {section_name}")
                return True
        raise RuntimeError(f"[click_section_more] {section_name} 더보기 버튼 위치를 찾지 못함")

    def click_section_more_and_verify(self, section_name: str, max_attempts: int = 3) -> tuple:
        """더보기 클릭 후 실제 도달한 화면의 타이틀을 확인해, 기대한 목적지가 아니면(WDA 터치
        이벤트 유실이나 배너 애니메이션 타이밍에 따른 스크롤 오차 누적으로 인한 오탭) 장르홈으로
        되돌아가 재시도한다. iOS 좌표 하드코딩 방식의 근본적 한계(is_present로 스크롤 완료를
        검증할 수 없음)를 결과 검증으로 보완하는 안전장치. 힌트가 등록된 섹션명이면 AOS/iOS
        동일하게 검증 및 재시도에 참여하고, 힌트가 없는 섹션은 기존과 동일하게 1회만 시도한다.
        (목적지 타이틀, 기대한 목적지가 맞는지 검증 성공 여부) 튜플 반환 — 검증에 끝내 실패하면
        호출측에서 목적지 화면 후속 처리(세로스크롤 등 무거운 작업)를 건너뛸 수 있도록
        verified=False로 알려준다."""
        hint = self.IOS_SECTION_MORE_DEST_HINT.get(section_name)
        dest_title = ""
        for attempt in range(max_attempts if hint else 1):
            if not self.click_section_more(section_name):
                # 콘텐츠 로딩이 확인 안 돼 탭 자체를 하지 않은 경우 — 장르홈을 벗어난 적이
                # 없으므로 뒤로가기 없이 바로 다음 시도로 넘어간다.
                continue
            time.sleep(5)
            try:
                dest_title = self.get_current_top_title()
            except Exception as e:
                dest_title = ""
                self.log.warning(f"[{section_name}] 목적지 타이틀 확인 실패(iOS WDA 이슈 가능): {e}")
            if not hint or hint in dest_title:
                return dest_title, True
            if hint:
                # 접근성 트리 기반 확인이 실패해도 곧바로 재시도하지 않고 화면 스크린샷을
                # OCR로 직접 읽어 기대 타이틀 문구가 실제로 노출되는지 한 번 더 확인한다.
                # 여기서 확인되면 오탭이 아니라 타이틀 추출 자체의 실패였던 것 - 인식된
                # 실제 OCR 텍스트를 dest_title로 사용해 이후 로그에서도 실제 화면 상태를
                # 알 수 있게 한다. 원래 iOS 전용이었으나(접근성 요소값 추출이 이 화면에서
                # 불안정한 경우가 있어 - 빈 값, 하단 탭바 텍스트, 랭킹 아이템명 등 엉뚱한
                # 값이 잡힘 - "BL 키워드 검색", "BL만화 실시간 랭킹" 등 실기기 확인됨),
                # AOS도 "BL만화 실시간 랭킹" 더보기를 눌러도 접근성 트리에 남은 이전 화면
                # ("BL 키워드 검색") 잔여 요소 때문에 요소 기반 확인이 속는 경우가 실기기로
                # 확인되어 - 실제 탭 자체는 맞았을 수 있음 - 동일하게 적용한다. 화면
                # 스크린샷은 접근성 트리와 무관하게 실제 렌더링 결과이므로 이 잔여 문제에
                # 영향받지 않는다.
                ocr_text = self._get_ocr_top_title()
                # "BL" 등 영문 접두어는 이 앱 폰트 스타일 때문에 OCR이 자주 오인식하지만
                # ("BL만화 실시간 랭킹" → "8Ｌ.만화 실시간 랭킹" 등 실기기 확인됨) 한글
                # 부분은 안정적으로 인식되므로, 한글 문자만 추출해 비교한다.
                hint_kor = self._korean_only(hint)
                if ocr_text and hint_kor and hint_kor in self._korean_only(ocr_text):
                    self.log.info(f"[{section_name}] 요소 기반 타이틀 추출 실패 - OCR로 '{hint}' 확인됨(실제 텍스트: '{ocr_text}')")
                    return ocr_text, True
            self.log.warning(
                f"[{section_name}] 더보기 목적지 불일치(시도 {attempt + 1}/{max_attempts}) "
                f"기대 힌트:'{hint}' 실제타이틀:'{dest_title}' - 장르홈 복귀 후 재시도"
            )
            self.navigate_back_to_genrehome()
            time.sleep(1)
        return dest_title, False

    def _is_text_visible_on_screen(self, expected_text: str, top_ratio: float = 0.12, from_bottom: bool = False) -> bool:
        """상단 타이틀(또는 하단 푸터) 접근성 요소 추출이 실패/부정확한 경우의 폴백. 화면
        상단(또는 from_bottom=True 시 하단) 영역만 스크린샷으로 캡처해 OCR로 텍스트를 읽어
        기대 문구가 실제로 보이는지 확인한다. 목적지 화면의 상단 타이틀바/하단 푸터는 배너와
        달리 단색 배경 위 텍스트라(빅배너 OCR 시도와 달리) 실기기 확인 결과 OCR 신뢰도가
        충분하다."""
        try:
            import pytesseract
            from PIL import Image
            import io
            png = self.driver.get_screenshot_as_png()
            img = Image.open(io.BytesIO(png))
            w, h = img.size
            if from_bottom:
                crop = img.crop((0, int(h * (1 - top_ratio)), w, h))
            else:
                crop = img.crop((0, 0, w, int(h * top_ratio)))
            text = pytesseract.image_to_string(crop, lang="kor+eng").strip()
            return expected_text.replace(" ", "") in text.replace(" ", "").replace("\n", "")
        except Exception as e:
            self.log.warning(f"[_is_text_visible_on_screen] OCR 확인 실패: {e}")
            return False

    def is_all_filter_visible(self, expected_text: str = "필터") -> bool:
        """더보기 목적지(카테고리 리스트) 화면에 기대하는 필터/탭 텍스트가 노출되는지 확인.
        "새로 나온 작품"과 "만화 베스트" 더보기 목적지 화면 둘 다 공통으로 "필터" 버튼이
        있어(실기기 확인됨), 두 섹션 모두 이 버튼 하나로 통일해서 정상 도달 여부를 판단한다.

        iOS는 이 화면 전체 텍스트가 하나의 접근성 블롭(XCUIElementTypeOther)에 뭉쳐서
        노출되지만("전체"/"필터" 모두 XCUIElementTypeStaticText/Button이 아님이 실기기로
        확인됨 — 기존 타입 제약 로케이터가 항상 실패했던 원인), 카테고리 화면과 동일하게
        블롭과 별개로 정확한 이름의 리프 요소가 존재해 타입 제약 없이 이름만으로 찾는
        ACCESSIBILITY_ID로 조회한다.

        _iter_text_elements()(전체 page_source 덤프)는 이 목적지 화면에서 WDA가 120초
        타임아웃을 일으켜(실기기로 확인 — test_008 실패 원인) 테스트 세션 자체가 끊기므로,
        대신 기대 문구 하나만 겨냥한 가벼운 조회를 사용한다."""
        if self.platform == "ios":
            locator = (AppiumBy.ACCESSIBILITY_ID, expected_text)
        else:
            locator = (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{expected_text}")')
        return self.is_element_present(locator, timeout=5)

    def get_visible_content_item_names(self, top_margin_ratio: float = 0.15) -> list:
        """더보기 등 목적지 화면에서 상단 고정영역을 제외한 콘텐츠 아이템 대표 텍스트 목록 (위→아래 순).

        화면 전환 직후 이전 화면의 잔여 요소(배너 캡션, 섹션 타이틀 등)가 접근성 트리에
        아직 남아있는 경우와, 실제 페이지의 "N개 작품 인기순 필터"처럼 정렬/필터 안내 행이
        둘 다 실제 아이템보다 먼저 나와 첫/마지막 항목으로 잘못 인식되는 문제가 실기기로
        확인되어("지금, 리디에서만 볼 수 있는 BL만화" 등), "N개 작품" 안내 행의 y좌표를 찾아
        그 행 이상(같은 행 포함)에 위치한 요소는 전부 제외한다 - 안내 행은 항상 진짜 아이템
        목록보다 위에 있어, 잔여 요소든 안내 라벨이든 이 기준 하나로 함께 걸러진다.

        "BL만화 베스트" 등 랭킹형 목적지 화면은 실제 콘텐츠가 아닌 내부 구분선 요소의
        접근성 이름("bottomLine")이 첫번째 항목으로 오탐되는 문제가 실기기로 확인되어
        추가로 제외한다.

        AOS는 "BL만화 실시간 랭킹" 더보기 화면에서 이전 화면(BL 키워드 검색 섹션)의
        해시태그 칩("#학원/캠퍼스" 등)과 표지 배지의 평점 개수만 단독으로 남은 요소
        ("(79)" 등)가 각각 첫번째/마지막 항목으로 오탐되는 문제가 실기기로 확인되어,
        "#"로 시작하는 해시태그와 괄호 숫자만 있는 텍스트를 추가로 제외한다. "지금,
        리디에서만 볼 수 있는 BL만화"에서는 평점 숫자만 단독으로 남은 요소("4.1" 등)가
        마지막 항목으로 오탐되는 문제도 확인되어 소수점 평점 단독 표기도 제외한다.

        AOS는 제목/저자/평점이 각각 별도 요소로 존재하는데, 정렬 순서상 저자명이 제목보다
        먼저 나오는 경우가 있어("BL만화 베스트"에서 "돌", "BL만화 실시간 랭킹"에서 "콘키치"
        등 저자명이 작품명 대신 첫번째 항목으로 오탐됨) 어떤 섹션은 제목을, 어떤 섹션은
        저자명을 가져오는 비일관성이 실기기로 확인되었다. 같은 행으로 묶어 가장 긴 텍스트를
        쓰는 방식과 iOS처럼 "(평가수)" 경계로 병합하는 방식 둘 다 시도했으나, 전자는 효과가
        없었고 후자는 오히려 여러 카드가 하나로 뭉쳐 완전히 깨지는 회귀를 일으켜(실기기
        확인됨) 둘 다 되돌렸다 - 근본 원인(왜 저자 요소가 정렬상 제목보다 앞에 오는지)을
        아직 못 찾아 known limitation으로 남겨두고, 기존처럼 요소 하나당 항목 하나로
        반환한다."""
        import re
        h = self.driver.get_window_size()["height"]
        top_cut = h * top_margin_ratio
        elems = [e for e in self._iter_text_elements()
                 if e[0] > top_cut and not e[4].lstrip().startswith(("©", "ⓒ", "#"))
                 and e[4].strip() != "bottomLine"
                 and not re.fullmatch(r'\(\d[\d,]*\)', e[4].strip())
                 and not re.fullmatch(r'\d(\.\d)?', e[4].strip())]
        marker_bottom = max((e[2] for e in elems if re.search(r'\d+개\s*작품', e[4])), default=None)
        if marker_bottom is not None:
            elems = [e for e in elems if e[0] >= marker_bottom]
        elems.sort(key=lambda e: (e[0], e[1]))
        names = []
        for e in elems:
            text = e[4].replace("\n", " ")
            if self.platform == "ios":
                # 목적지 화면 최초 로딩 시 여러 카드가 하나의 접근성 노드에 합쳐진 채로
                # 반환되는 문제가 실기기로 확인되어("BL만화 e북 신간" 더보기 첫번째 작품이
                # 실제로는 3개 작품이 이어붙은 텍스트로 오탐됨), 섹션 캐러셀과 동일한
                # "(평가수)" 경계 분리를 적용한다. 마커가 1개 이하면 원문 그대로 반환되어
                # 이미 정상 동작하던 케이스(마지막 작품 등)에는 영향 없다.
                names.extend(self._split_multi_card_text(text))
            else:
                names.append(text)
        return names

    def _split_multi_card_text(self, text: str) -> list:
        """"{제목} {저자} {평점} (평가수)"가 순위 없이 여러 개 이어붙은 문자열을 "(평가수)"
        경계로 분리한다(_split_ios_card_items와 동일한 핵심 로직, 섹션명 기반 예외 없이
        범용 사용). "(평가수)" 마커가 1개 이하면 분리 없이 원문 그대로 반환한다."""
        import re
        if not text:
            return []
        bounds = [0] + [m.end() for m in re.finditer(r'\(\d[\d,]*\)', text)]
        if bounds[-1] != len(text):
            bounds.append(len(text))
        items = [text[bounds[i]:bounds[i + 1]].strip() for i in range(len(bounds) - 1)]
        return [i for i in items if i] or [text]

    def _ios_destination_scroll_down(self):
        """더보기 등 목적지 화면(iOS) 전용 세로 스크롤. base_page.fallback_swipe("down")는
        iOS에서 방향이 반대로 매핑되어 있어(콘텐츠를 더 아래로 보여주는 게 아니라 반대 방향으로
        스크롤됨) 실질적으로 스크롤이 안 되는 것처럼 보이는 문제가 있어, 직접 방향을 맞춰 구현한다."""
        size = self.driver.get_window_size()
        x = int(size["width"] * 0.5)
        self.driver.swipe(x, int(size["height"] * 0.80), x, int(size["height"] * 0.35), 800)
        time.sleep(1)

    def collect_items_by_vertical_scroll(self, max_scrolls: int = 6, force_full_scroll: bool = False) -> list:
        """목적지 화면을 세로 스크롤하며 아이템을 중복없이 순서대로 수집.
        더보기 등 목적지 화면은 장르홈과 달리 가로 캐러셀이 섞여있지 않은 일반 목록이므로,
        원시 좌표 스와이프 대신 아이템 오클릭 위험이 없는 공용 scroll_down()(base_page)을 사용한다.
        (iOS는 scroll_down()의 방향 매핑 버그를 피해 전용 스크롤 사용)

        force_full_scroll=True는 "지금, 리디에서만 볼 수 있는 만화" 더보기처럼 화면 끝을
        감지할 별도 수단이 없는 목적지 화면 전용 - 2회 연속 신규 항목 없음(stall) 조기 종료
        없이 max_scrolls만큼 무조건 끝까지 스크롤해, 그 시점까지 확인된 마지막 항목을 사용한다.
        기본값 False는 기존 동작(stall 조기 종료) 그대로라 다른 호출부에 영향 없다."""
        seen, ordered = set(), []
        for name in self.get_visible_content_item_names():
            if name not in seen:
                seen.add(name)
                ordered.append(name)
        stall = 0
        count = 0
        while (force_full_scroll or stall < 2) and count < max_scrolls:
            if self.platform == "ios":
                self._ios_destination_scroll_down()
            else:
                self.scroll_down()
            count += 1
            newly = 0
            for name in self.get_visible_content_item_names():
                if name not in seen:
                    seen.add(name)
                    ordered.append(name)
                    newly += 1
            stall = 0 if newly else stall + 1
        return ordered

    def scroll_to_footer_and_get_last_item(self, section_name: str, max_scroll: int = 40) -> tuple:
        """장르홈 맨 마지막 섹션("...님의 취향 저격 AI 추천")은 더보기가 없어 좌우스와이프
        수집 대신, 푸터가 노출될 때까지 세로 스크롤을 계속하며 마지막 작품명을 확인한다.
        (마지막 작품명, 푸터 노출 여부) 튜플 반환.

        이 섹션은 장르홈 맨 마지막 섹션 자체가 랭킹형이라 항목 수가 많아, 기존 max_scroll=20
        으로는 푸터까지 도달하지 못하고 중간에 멈추는 문제가 실기기로 확인되어 상향한다.
        이 함수는 이 섹션 전용(다른 호출부 없음)이라 다른 스크롤 동작에 영향 없다.

        AOS는 스크롤이 진행될수록 이전에 지나친 요소(섹션 타이틀 포함)가 접근성 트리에서
        아예 사라지는데, 끝까지 스크롤한 뒤에야 타이틀 기준으로 아이템을 조회하려 하면 타이틀을
        찾지 못해 예외가 발생하는 문제가 실기기로 확인되었다(iOS는 블롭이 스크롤과 무관하게
        항상 남아있어 영향 없음). 이를 피하기 위해 AOS는 스크롤 도중 매 회차 보이는 아이템을
        갱신해두어, 이후 타이틀이 화면 밖으로 사라져도 마지막으로 확인된 값을 그대로 쓴다.

        iOS는 푸터("리디(주)...")도 장르홈 전체와 마찬가지로 하나의 접근성 블롭에 포함되어
        개별 StaticText로 존재하지 않아(실기기 확인됨) 로케이터 기반 감지가 원천적으로
        불가능하다 - 화면 하단 영역을 스크린샷+OCR로 읽어 노출 여부를 확인한다."""
        footer_locator = self._loc("FOOTER")
        footer_reached = False

        if self.platform == "ios":
            for _ in range(max_scroll):
                if self._is_text_visible_on_screen("리디(주)", top_ratio=0.15, from_bottom=True):
                    footer_reached = True
                    break
                self._vertical_swipe_up()
            content = self._get_ios_section_content(section_name)
            items = self._split_ios_card_items(section_name, content)
            last_item = items[-1] if items else "(확인불가)"
            return last_item, footer_reached

        last_item = "(확인불가)"
        for _ in range(max_scroll):
            try:
                items = self.get_section_item_names(section_name)
                if items:
                    last_item = items[-1]
            except Exception as e:
                self.log.warning(f"[scroll_to_footer_and_get_last_item] {section_name} 아이템 조회 실패(무시): {e}")
            if self.is_present(footer_locator, timeout=1):
                footer_reached = True
                break
            self._vertical_swipe_up()
        return last_item, footer_reached

    #만화 카테고리
    CATEGORY_TOPMENU_LOCATOR = {
        "만화 e북":    "CATEGORY_TOPMENU_EBOOK",
        "만화 연재":    "CATEGORY_TOPMENU_SERIAL",
        "BL 만화 e북": "CATEGORY_TOPMENU_BL_EBOOK",
        "라이트노벨":   "CATEGORY_TOPMENU_LIGHTNOVEL",
    }

    # 실기기(Appium MCP/직접 스크립트)로 확인한 상위메뉴별 하위메뉴 목록(개수: 15/13/3/3).
    # 하위메뉴 구조 자체가 정적인 카테고리 트리라, 화면에서 동적으로 파싱하는 대신 실측한
    # 목록을 그대로 사용한다.
    CATEGORY_SUBMENUS = {
        "만화 e북": [
            "만화 e북 전체", "국내 순정", "해외 순정", "드라마", "할리퀸", "무협", "학원",
            "액션", "판타지/SF", "스포츠", "코믹", "GL", "공포/추리", "극화", "만화잡지",
        ],
        "만화 연재": [
            "만화 연재 전체", "국내 순정", "해외 순정", "드라마", "무협", "액션", "판타지/SF",
            "학원", "스포츠", "코믹", "GL", "공포/추리", "극화",
        ],
        "BL 만화 e북": ["BL 만화 e북 전체", "국내 만화", "해외 만화"],
        "라이트노벨": ["라이트노벨 전체", "국내 라노벨", "해외 라노벨"],
    }

    # 햄버거(카테고리) 버튼은 텍스트/접근성ID가 없는 아이콘이라(실기기 확인됨) 좌표비율로
    # 탭한다. iOS(390x844 기준 362,121)/AOS(1080x2340 기준 1001,300) 모두 실기기로 실측한
    # 값이며, 두 플랫폼 다 서브탭 바(추천/베스트/...) 우측 끝에 위치한다.
    CATEGORY_BUTTON_COORD_RATIO = {
        "ios": (0.928, 0.143),
        "aos": (0.927, 0.1286),
    }

    def is_category_page_displayed(self) -> bool:
        return self.is_present(self._loc("CATEGORY_TITLE"), timeout=5)

    def _dismiss_ios_system_alert(self) -> bool:
        """iOS 실기기 확인 결과, 앱 재진입 후 알림/앱추적투명성(ATT) 권한 시스템 팝업이
        예측 불가한 시점에 떠서 좌표 탭을 가로채는 경우가 있다(장르홈 우측 상단 근처에서
        빈번히 관측됨). locators/common.py의 ALERT_ALLOW_IOS/ALLOW_BTN_IOS(IOS_PREDICATE
        기반 find_element)로 명시적으로 찾아 클릭하는 방식을 시도했으나, 이 시스템 알림은
        WDA의 일반 find_element/xpath 탐색 범위 밖에 있어(Appium MCP로 직접 tap_by_xpath/
        tap_by_text 둘 다 실패하고 좌표 탭만 성공하는 것으로 실기기 확인, 2026-07-23)
        전혀 동작하지 않았다 - mobile: alert accept(XCTest의 시스템 알림 전용 API)로
        되돌린다."""
        if self.platform != "ios":
            return False
        try:
            self.driver.execute_script("mobile: alert", {"action": "accept"})
            self.log.info("[카테고리] 시스템 팝업(알림/ATT) 감지되어 허용 처리")
            time.sleep(1)
            return True
        except Exception:
            return False

    def open_category_page(self) -> bool:
        """장르홈 추천탭 우측 상단 햄버거(카테고리) 버튼을 탭해 만화 카테고리 화면으로 진입.
        탭 전에 남아있는 시스템 팝업을 먼저 정리하고, 실패 시 팝업이 탭을 가로챈 경우를 대비해
        한 번 더 정리 후 재탭한다."""
        ratio = self.CATEGORY_BUTTON_COORD_RATIO[self.platform]
        size = self.driver.get_window_size()

        self._dismiss_ios_system_alert()
        self.tap_coordinate(int(size["width"] * ratio[0]), int(size["height"] * ratio[1]))
        self.log.info("[카테고리] 햄버거 버튼 탭")
        time.sleep(3)
        if self.is_category_page_displayed():
            return True

        if self._dismiss_ios_system_alert():
            self.tap_coordinate(int(size["width"] * ratio[0]), int(size["height"] * ratio[1]))
            self.log.info("[카테고리] 햄버거 버튼 재탭 (시스템 팝업 정리 후)")
            time.sleep(3)
        return self.is_category_page_displayed()

    def _scroll_category_page_down(self):
        """카테고리 화면에서 접힌 화면 밖으로 밀려난 항목을 노출시키기 위한 세로 스크롤.
        base_page.scroll_down()(fallback_swipe)은 iOS에서 방향이 반대로 매핑되어 있어(콘텐츠를
        더 아래로 보여주는 게 아니라 반대로 스크롤됨 — _ios_destination_scroll_down에서 이미
        동일한 이유로 우회한 이슈) 카테고리 화면에서도 동일하게 직접 방향을 맞춰 처리한다."""
        if self.platform == "ios":
            self._ios_destination_scroll_down()
        else:
            self.scroll_down()

    def _scroll_category_page_up(self):
        """_scroll_category_page_down의 반대 방향 - 하위메뉴를 탭하며 아래로 내려간 뒤
        위쪽에 있는 이미 펼쳐둔 상위메뉴 토글을 다시 찾아 접을 때 사용한다."""
        if self.platform == "ios":
            size = self.driver.get_window_size()
            x = int(size["width"] * 0.5)
            self.driver.swipe(x, int(size["height"] * 0.35), x, int(size["height"] * 0.80), 800)
            time.sleep(1)
        else:
            self.scroll_up()

    def _scroll_category_item_into_view(self, locator: tuple, max_scroll: int = 10, direction: str = "down") -> bool:
        scroll_fn = self._scroll_category_page_down if direction == "down" else self._scroll_category_page_up
        for _ in range(max_scroll):
            if self.is_present(locator, timeout=2):
                return True
            scroll_fn()
        return self.is_present(locator, timeout=2)

    def expand_category_topmenu(self, topmenu_name: str):
        """카테고리 화면에서 상위메뉴 토글을 펼쳐 하위메뉴 목록을 노출.
        이전에 펼친 다른 상위메뉴 토글이 자동으로 접히지 않고 그대로 남아있어(실기기 확인됨),
        뒤 순서 상위메뉴일수록 화면 아래로 밀려나 있을 수 있다 - 보이지 않으면 스크롤로
        노출시킨 뒤 탭한다.

        (2026-07-23 첫 시도: 펼친 직후 무조건 마지막 하위메뉴를 미리 스크롤로 찾아 넣었더니,
        스크롤이 아래 방향으로만 동작해 마지막 항목을 찾느라 화면이 훨씬 아래로 내려간 채
        남아버려서 그 다음 첫번째 하위메뉴를 오히려 못 찾는 회귀가 실기기로 확인되어
        (2026-07-24, TestWebtoonCategory 전부 실패) 롤백. 2026-07-24 재설계: 마지막 하위메뉴가
        이미 보이면(대부분의 상위메뉴는 이 경우라 기존 통과 케이스에 영향 없음) 아무것도 하지
        않고, 안 보일 때만 스크롤해 존재를 확인한 뒤 반드시 상위메뉴 헤더 위치로 다시 스크롤업해
        되돌린다 - 그래야 이후 tap_category_submenu의 첫 하위메뉴 탐색(아래 방향 스크롤만 가능)이
        이미 지나쳐버린 위쪽 항목을 못 찾는 문제가 재발하지 않는다.)"""
        attr = self.CATEGORY_TOPMENU_LOCATOR[topmenu_name]
        locator = self._loc(attr)
        self._scroll_category_item_into_view(locator)
        self.click(locator)
        time.sleep(1)

        last_submenu = self.CATEGORY_SUBMENUS[topmenu_name][-1]
        last_locator = self._category_item_locator(last_submenu)
        if not self.is_present(last_locator, timeout=2):
            self._scroll_category_item_into_view(last_locator, max_scroll=15)
            self._scroll_category_item_into_view(locator, direction="up", max_scroll=15)
        self.log.info(f"[카테고리] 상위메뉴 펼침: {topmenu_name}")

    def collapse_category_topmenu(self, topmenu_name: str):
        """expand_category_topmenu로 펼친 상위메뉴 토글을 다시 접는다(동일 토글 버튼 재탭).
        이전 상위메뉴가 접히지 않은 채 남아있으면 다음 상위메뉴/하위메뉴가 화면 아래로 계속
        밀려나 누적되어(실기기 확인됨, test_004~006 연쇄 실패 원인) 각 상위메뉴 처리가 끝나면
        반드시 접어 카테고리 화면을 다음 상위메뉴 테스트를 위한 깨끗한 상태로 되돌린다.
        하위메뉴를 여러 개 탭하며 아래로 스크롤한 뒤라 상위메뉴 토글은 화면 위쪽에 있으므로
        위 방향으로 스크롤해 찾는다."""
        attr = self.CATEGORY_TOPMENU_LOCATOR[topmenu_name]
        locator = self._loc(attr)
        self._scroll_category_item_into_view(locator, direction="up")
        self.click(locator)
        time.sleep(1)
        self.log.info(f"[카테고리] 상위메뉴 접음: {topmenu_name}")

    def _category_item_locator(self, name: str) -> tuple:
        """카테고리 화면의 상위/하위메뉴 항목은 실기기 확인 결과 플랫폼 공통으로 정확히
        일치하는 텍스트 하나로 개별 탭 가능한 요소라(iOS: accessibility id, AOS: UiSelector
        text), 메뉴명으로 로케이터를 동적으로 구성한다."""
        if self.platform == "ios":
            return (AppiumBy.ACCESSIBILITY_ID, name)
        return (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{name}")')

    def tap_category_submenu(self, submenu_name: str):
        """앞서 펼친 다른 상위메뉴들의 하위메뉴 목록이 위에 그대로 쌓여있어(실기기 확인됨)
        뒤 순서 하위메뉴일수록 화면 아래로 밀려나 있을 수 있다 - 보이지 않으면 스크롤로
        노출시킨 뒤 탭한다.

        하위메뉴명이 다른 상위메뉴명과 완전히 동일한 경우가 있다(예: 도서 카테고리 "잡지"의
        하위메뉴 "종교"가 상위메뉴 "종교"와 이름이 겹침, 실기기로 확인됨 2026-07-24). 이때
        두 요소가 동시에 화면 계층에 존재해 click(locator)이 항상 첫 번째로 매치되는 상위메뉴
        쪽을 잘못 탭해버린다 - "잡지"는 상위메뉴 목록 맨 뒤라 그 하위메뉴 "종교"는 항상 상위
        메뉴 "종교"보다 화면 아래쪽(y좌표가 큼)에 위치하므로, 이름이 겹치는 경우에 한해 여러
        매치 중 y좌표가 가장 큰 요소를 하위메뉴로 간주해 직접 탭한다.

        탭했는데 실제로는 화면전환이 안 되고 카테고리 목록에 그대로 남아있는 경우가 실기기로
        확인되어(2026-07-24, 도서 카테고리 맨 마지막 상위메뉴 "잡지"의 "잡지 전체"). 진단
        스크립트로 실측한 결과 근본 원인은 타이밍이 아니라 위치였다 - "잡지"는 목록 맨 마지막
        항목이라 펼치기 전 위치가 화면의 88%대까지밖에 안 올라오고, 그 하위메뉴 "잡지 전체"는
        화면의 94~97% 지점(안드로이드 시스템 네비게이션 바/제스처 영역과 겹칠 수 있는 위치)에
        걸려있어 탭이 씹혔다. is_present(요소가 하나라도 보이면 통과)만으로는 이 위치까지
        잡아내지 못해, 탭 전에 _scroll_until_safe_from_bottom으로 하단 여백을 확보한다.

        하위메뉴명이 화면 최상단 고정 카테고리 탭바("만화"/"웹툰"/"웹소설"/"도서" 등)와도
        우연히 겹칠 수 있다(예: "잡지"의 하위메뉴 "만화" - 실기기로 확인됨 2026-07-24, y≈93
        위치). 이 고정 탭은 스크롤과 무관하게 항상 존재해 스크롤을 한 번도 안 해도 즉시
        "찾았다"고 오판되고, 매치가 1개뿐이라 위 이름충돌 방지 로직(2개 이상일 때만 발동)도
        못 잡는다 - 그래서 스크롤 검색 자체를 화면 상단 10% 이내는 무시하는 전용 헬퍼
        (_scroll_submenu_into_view)로 대체한다.

        한때 탭 후 화면전환이 확인 안 되면 재탭하는 안전장치를 넣었었지만(2026-07-24),
        `is_category_page_displayed()`가 실제로는 이미 화면전환에 성공한 시점에도 계속
        참으로 오판해 불필요한 재탭을 반복시키고, 그 재탭이 이미 넘어간 목적지 화면에서
        엉뚱한 요소를 눌러 다음 하위메뉴 확인까지 연쇄로 꼬이게 만드는 문제가 실기기로
        확인되어(2026-07-24, "경영/재테크" 확인 시점에 엉뚱하게 "잡지 전체" 화면에 남아있게
        됨) 제거했다. 스크롤/안전마진/이름충돌 처리만으로 이미 충분히 안정적이라 판단."""
        locator = self._category_item_locator(submenu_name)
        self._scroll_submenu_into_view(locator)
        self._scroll_until_safe_from_bottom(locator)

        h = self.driver.get_window_size()["height"]
        elements = [e for e in self.find_elements(locator) if e.location["y"] >= h * 0.1]
        if len(elements) > 1:
            target = max(elements, key=lambda e: e.location["y"])
            target.click()
            self.log.info(f"[click] {locator} (이름이 겹치는 상위메뉴/고정탭과 구분 - 하단 요소 선택)")
        elif len(elements) == 1:
            elements[0].click()
            self.log.info(f"[click] {locator} (상단 고정탭 제외)")
        else:
            self.click(locator)
        self.log.info(f"[카테고리] 하위메뉴 탭: {submenu_name}")

    def _scroll_submenu_into_view(self, locator: tuple, max_scroll: int = 10) -> bool:
        """_scroll_category_item_into_view와 달리 화면 상단 10% 이내(고정 카테고리 탭바
        영역)에 있는 매치는 무시하고, 그 아래에 실제 하위메뉴가 보일 때까지 스크롤한다.
        하위메뉴명이 상단 고정 탭("만화" 등)과 겹치면 일반 is_present가 스크롤 없이 즉시
        "찾음"으로 오판하는 문제가 실기기로 확인되어(2026-07-24) 전용으로 둔다."""
        h = self.driver.get_window_size()["height"]
        for _ in range(max_scroll):
            elements = self.find_elements(locator)
            if any(e.location["y"] >= h * 0.1 for e in elements):
                return True
            self._scroll_category_page_down()
        elements = self.find_elements(locator)
        return any(e.location["y"] >= h * 0.1 for e in elements)

    def _scroll_until_safe_from_bottom(self, locator: tuple, safe_margin_ratio: float = 0.85, max_scroll: int = 5):
        """요소가 화면 맨 아래(안드로이드 시스템 네비게이션 바/제스처 영역과 겹칠 수 있는
        위치)에 걸쳐있으면 탭이 씹히는 문제가 실기기로 확인되어(2026-07-24, 도서 카테고리
        "잡지"의 "잡지 전체" - 하위메뉴가 화면의 93~97% 지점까지 밀려 있었음), 하단 여백을
        두고 안전하게 보일 때까지 추가로 스크롤한다. is_present는 요소가 하나라도 보이면
        통과 처리해 이 위치까지는 못 잡아내 별도로 둔다.

        화면 상단 고정 탭바와 이름이 겹치는 경우(예: "만화") find_element(첫 매치)가 그
        고정 탭을 집어서 "이미 안전하다"고 오판할 수 있어(2026-07-24), 매치 중 y좌표가 가장
        큰(실제 하위메뉴일 가능성이 높은) 요소를 기준으로 판단한다."""
        h = self.driver.get_window_size()["height"]
        for _ in range(max_scroll):
            elements = self.find_elements(locator)
            if not elements:
                return
            el = max(elements, key=lambda e: e.location["y"])
            bottom = el.location["y"] + el.size["height"]
            if bottom <= h * safe_margin_ratio:
                return
            self._scroll_category_page_down()

    def is_category_dest_title_visible(self, expected_title: str, timeout: int = 8) -> bool:
        """하위메뉴 선택 후 진입한 목적지 화면의 타이틀이 하위메뉴명과 일치하는지 확인.
        AOS는 page_source 기반 get_current_top_title()이 안전하지만, iOS는 이 목적지 화면도
        장르홈과 동일하게 전체 텍스트가 하나의 접근성 블롭에 뭉쳐 노출되고, 게다가 이 화면에서
        전체 page_source를 덤프(get_current_top_title 내부 동작)하면 WDA가 세션 자체를
        끊어버리는 것까지 실기기로 확인되어(장르홈보다 더 심각), 대신 is_all_filter_visible과
        동일하게 타이틀 텍스트 하나만 겨냥한 가벼운 조회로 존재 여부만 확인한다."""
        if self.platform == "ios":
            locator = (AppiumBy.IOS_CLASS_CHAIN, f'**/XCUIElementTypeStaticText[`name == "{expected_title}"`]')
            return self.is_element_present(locator, timeout=timeout)
        time.sleep(3)
        return expected_title in self.get_current_top_title()

    def navigate_back_one_screen(self):
        """카테고리 하위메뉴 목적지 화면 → 카테고리 화면처럼, 장르홈이 아닌 바로 이전 화면
        하나만 되돌아간다 (navigate_back_to_genrehome과 동일한 방식, 목적지만 다름)."""
        if self.platform == "aos":
            self.driver.back()
        else:
            self.tap_coordinate(20, 69)
        time.sleep(1.5)
        self.log.info("[카테고리] 뒤로가기 (이전 화면 복귀)")

    def _get_ios_category_dest_content(self, submenu_name: str) -> str:
        """카테고리 하위메뉴 목적지 화면(iOS)의 콘텐츠 블롭 원문 추출. 장르홈 섹션과 동일하게
        이 화면 전체 텍스트도 하나의 XCUIElementTypeOther에 뭉쳐서 노출되고(실기기 확인), 이
        블롭은 화면이 바뀌어도 초기화되지 않고 앱 세션 내내 계속 이어붙는(누적) 것까지 실기기로
        확인되었다.

        하위메뉴명이 등장하는 마지막 위치를 무조건 현재 화면으로 간주하면, "할리퀸"처럼 실제
        서점에서 임프린트/장르 태그로도 함께 쓰이는 이름은 이후 방문한 다른 화면 콘텐츠 어딘가에
        태그로 다시 등장할 수 있어 엉뚱한 위치를 짚는 문제가 실기기로 확인되었다. 카테고리 목적지
        화면은 타이틀 뒤에 항상 "베스트/신작/업데이트/전체" 서브탭바가 곧바로 이어지지만,
        "지금 많이 읽고 있는 만화" 더보기처럼 서브탭 없이 타이틀 바로 뒤에 곧장 순위(1위) 항목이
        오는 화면도 있어(실기기 확인됨), 타이틀 뒤에 "베스트" 또는 숫자+공백(순위 시작)이
        바로 따라오는 위치만 진짜 목적지로 인정한다."""
        try:
            locator = (AppiumBy.IOS_CLASS_CHAIN, f'**/XCUIElementTypeOther[`name CONTAINS "{submenu_name}"`]')
            blob = self.find_element(locator).get_attribute("name") or ""
        except Exception as e:
            self.log.warning(f"[_get_ios_category_dest_content] {submenu_name} 콘텐츠 추출 실패: {e}")
            return ""

        import re
        title_pattern = re.compile(re.escape(submenu_name) + r'\s*(?=베스트|\d+\s)')
        matches = list(title_pattern.finditer(blob))
        if not matches:
            return ""
        after = blob[matches[-1].end():].strip()

        # 목적지명 뒤에는 곧바로 항목이 오지 않고 "베스트/신작/업데이트/전체" 탭바와
        # "N개 작품 주간" 같은 목록 상단 안내문구가 먼저 온다(실기기 확인됨). 이 안내문구까지
        # 1위 항목에 잘못 묶이는 문제가 있어, "N개 작품" 마커 뒤 안내 단어(있는 경우)까지
        # 건너뛰고 실제 순위(1) 항목이 시작하는 지점부터 반환한다. 뒤따르는 단어를 숫자가 없는
        # 토큰으로 제한해(`[^\d\s]*`) "1위" 같은 순위 숫자 자체를 실수로 삼켜버리지 않게 한다.
        marker = re.search(r'\d+개\s*작품\s*[^\d\s]*\s*', after)
        if marker:
            after = after[marker.end():]
        return after

    def _split_category_dest_items_aos(self, elements: list) -> list:
        """AOS 카테고리 목적지 화면은 순위/제목/저자/평점 등 각 필드가 개별 요소로 노출되어
        (실기기 확인됨), 순위 숫자 하나짜리 요소를 항목 경계로 삼아 다음 순위 전까지의 필드들을
        하나의 항목 텍스트로 합친다. 첫 순위("1") 이전의 "N개 작품"/"주간" 같은 목록 상단
        안내문구는 항목이 아니므로 첫 순위가 나오기 전까지는 아예 수집을 시작하지 않는다
        (실기기 확인 결과, 안내문구까지 첫 항목으로 잘못 묶이는 문제가 있었음).

        순위 숫자는 1부터 순차 증가하는 정수라는 점이 실기기로 확인되어, 평점이 소수점 없이
        정수로 노출되는 카드(예: "5")가 순위 숫자로 오인되어 제목이 빠진 가짜 항목("5 (평가수)")을
        1위로 반환하는 문제가 실기기로 확인됨(2026-07-24, 웹툰/웹소설/일반도서 카테고리 목적지
        화면 - 만화는 항상 소수점 평점("4.9")이라 이 문제가 없었음). "다음에 기대되는 순위
        숫자"와 정확히 일치할 때만 새 항목 경계로 인정해 이 오탐을 막는다."""
        items, current = [], []
        started = False
        next_rank = 1
        for _, _, _, _, text in elements:
            if text.isdigit() and len(text) <= 3 and int(text) == next_rank:
                if started and current:
                    items.append(" ".join(current))
                current = []
                started = True
                next_rank += 1
            if started:
                current.append(text)
        if started and current:
            items.append(" ".join(current))
        return items

    @staticmethod
    def _is_category_book_item_aos(text: str) -> bool:
        """카테고리 목적지 화면의 실제 도서 항목은 항상 "...(평가수)"로 끝난다. AOS는 실기기
        확인 결과 목록 하단에 장르홈과 유사한 추천 위젯(퀵메뉴/유사작품 섹션 등)이 이어져
        있어, 순위 숫자로 오인될 수 있는 페이지 카운터/배지 텍스트까지 항목으로 잘못
        수집되는 문제가 있었다 - 이 패턴으로 실제 도서 항목만 걸러낸다."""
        import re
        return bool(re.search(r'\(\d[\d,]*\)\s*$', text))

    def _get_category_dest_elements_aos(self, top_margin_ratio: float = 0.15) -> list:
        h = self.driver.get_window_size()["height"]
        top_cut = h * top_margin_ratio
        return [e for e in self._iter_text_elements() if e[0] > top_cut]

    def get_category_dest_first_item(self, submenu_name: str) -> str:
        """목적지 화면의 1위(첫번째) 작품명 반환"""
        if self.platform == "ios":
            items = self._split_ios_ranked_items(self._get_ios_category_dest_content(submenu_name))
            return items[0] if items else "(확인불가)"
        items = [i for i in self._split_category_dest_items_aos(self._get_category_dest_elements_aos())
                 if self._is_category_book_item_aos(i)]
        return items[0] if items else "(확인불가)"

    def _category_dest_scroll_down(self):
        """카테고리 하위메뉴 목적지 화면 순회검증(collect_category_dest_items_by_scroll) 전용
        세로 스크롤. 다른 모듈/목적지 화면이 쓰는 공용 스크롤 함수(_ios_destination_scroll_down,
        base_page.scroll_down)와는 완전히 분리된 별도 구현이다 - 카테고리 목적지 화면은 최대
        200위까지 존재해 기본 이동폭으로는 시간이 너무 오래 걸리므로, 이 함수에서만 1회당
        이동 폭을 크게 잡아 스크롤 횟수 자체를 줄인다. 공용 함수를 건드리지 않으므로 퀵메뉴
        더보기 등 다른 목적지 화면 스크롤에는 전혀 영향 없다."""
        if self.platform == "ios":
            # 매 호출마다 블롭 전체를 다시 읽는 콘텐츠 추출(_get_ios_category_dest_content)이
            # 세션 누적으로 갈수록 느려져 체감 시간의 대부분을 차지한다 - 스와이프 자체를
            # 2회 연달아 실행해 추출 호출 횟수를 절반으로 줄인다. 델타 비교 방식이라 중간에
            # 몇 번 스크롤됐는지와 무관하게 정확도에는 영향 없다.
            size = self.driver.get_window_size()
            x = int(size["width"] * 0.5)
            for _ in range(2):
                self.driver.swipe(x, int(size["height"] * 0.95), x, int(size["height"] * 0.08), 500)
                time.sleep(0.3)
        else:
            # AOS는 원시 좌표 스와이프/mobile: swipeGesture 모두 이 실기기에서 스크롤을
            # 전혀 일으키지 않는 것이 확인됨(_vertical_swipe_up 주석 참고) - 유일하게 검증된
            # UiScrollable.scrollForward()를 재사용하되, 200위까지 빠르게 내려가도록 이 함수
            # 호출 1회당 3번 연달아 실행해 이동 폭을 키운다.
            for _ in range(3):
                self.driver.find_element(
                    AppiumBy.ANDROID_UIAUTOMATOR,
                    f'new UiScrollable({self.AOS_VERTICAL_SCROLLVIEW_SELECTOR}).scrollForward()'
                )
        time.sleep(1)

    def collect_category_dest_items_by_scroll(self, submenu_name: str, max_scrolls: int = 30) -> list:
        """목적지 화면을 세로 스크롤하며 아이템을 중복없이 순서대로 수집 (마지막 작품 확인 및
        스크롤 동작 자체의 검증 목적). "만화잡지"처럼 200위가 안 되는 목록은 아래 stall(연속
        2회 신규 항목 없음) 조기 종료가 그대로 적용되어 불필요하게 끝까지 스크롤하지 않는다."""
        if self.platform == "ios":
            seen, ordered = set(), []
            last_content = ""

            def add_new(content):
                nonlocal last_content
                if not content or content == last_content:
                    return
                delta = content[len(last_content):].strip() if content.startswith(last_content) else content
                last_content = content
                for item in self._split_ios_ranked_items(delta):
                    if item not in seen:
                        seen.add(item)
                        ordered.append(item)

            add_new(self._get_ios_category_dest_content(submenu_name))
            stall = 0
            count = 0
            while stall < 2 and count < max_scrolls:
                self._category_dest_scroll_down()
                count += 1
                before = len(ordered)
                add_new(self._get_ios_category_dest_content(submenu_name))
                stall = 0 if len(ordered) > before else stall + 1
            return ordered

        seen, ordered = set(), []
        for name in self._split_category_dest_items_aos(self._get_category_dest_elements_aos()):
            if name not in seen and self._is_category_book_item_aos(name):
                seen.add(name)
                ordered.append(name)

        stall = 0
        count = 0
        while stall < 2 and count < max_scrolls:
            self._category_dest_scroll_down()
            count += 1
            newly = 0
            for name in self._split_category_dest_items_aos(self._get_category_dest_elements_aos()):
                if name not in seen and self._is_category_book_item_aos(name):
                    seen.add(name)
                    ordered.append(name)
                    newly += 1

            if newly == 0:
                # 3배속 스크롤이 마지막 항목을 화면에 걸친 짧은 프레임째로 건너뛰었을 수 있어
                # (실기기 확인됨 - 마지막 200위가 199위에서 누락됨), stall 처리 전 딱 한 번만
                # 1칸(느린 폭)으로 미세 스크롤 후 재확인한다. 공용 스크롤 함수(_vertical_swipe_up)는
                # 호출하지 않고 동일 메커니즘만 이 함수 안에 인라인으로 재사용해 완전히 분리 유지.
                self.driver.find_element(
                    AppiumBy.ANDROID_UIAUTOMATOR,
                    f'new UiScrollable({self.AOS_VERTICAL_SCROLLVIEW_SELECTOR}).scrollForward()'
                )
                time.sleep(1)
                for name in self._split_category_dest_items_aos(self._get_category_dest_elements_aos()):
                    if name not in seen and self._is_category_book_item_aos(name):
                        seen.add(name)
                        ordered.append(name)
                        newly += 1

            stall = 0 if newly else stall + 1
        return ordered

    # 베스트 탭 연령/성별 필터바. 실기기 확인 전 잠정 구현 - 정확한 y좌표/추출 방식은
    # 실기기 탐색 후 보완 예정("코드 먼저 작성 → 실기기 탐색해서 보완" 순서로 진행 중).
    DEFAULT_AGE_GENDER_TAB = "50대 남성"

    def _age_gender_tab_locator(self, tab_name: str) -> tuple:
        """베스트 탭 하위 연령/성별 필터바의 개별 탭 로케이터. 카테고리 상/하위메뉴와 동일하게
        플랫폼 공통으로 정확히 일치하는 텍스트 하나로 개별 탭 가능한 요소라고 가정하고
        _category_item_locator와 동일한 방식으로 동적 구성한다(실기기 확인 후 보완 예정)."""
        if self.platform == "ios":
            return (AppiumBy.ACCESSIBILITY_ID, tab_name)
        return (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{tab_name}")')

    def is_age_gender_tab_visible(self, tab_name: str, timeout: int = 3, log: bool = True) -> bool:
        locator = self._age_gender_tab_locator(tab_name)
        if self.platform == "ios":
            result = self.is_element_present(locator, timeout=timeout)
        else:
            result = self.is_present(locator, timeout=timeout)
        if log:
            self.log.info(f"[베스트탭_연령성별] {tab_name} {'✅' if result else '❌'}")
        return result

    def _age_gender_tab_y(self) -> int:
        """연령/성별 필터바 y좌표(비율). iOS 실기기(QA iPhone 16e, 844pt) 확인 결과 y=146,
        비율로 약 0.173 - AOS는 동일 화면 구조로 가정해 같은 비율을 사용한다."""
        return int(self.driver.get_window_size()["height"] * 0.173)

    def swipe_age_gender_tab_left(self):
        """베스트 탭 연령/성별 필터바 전용 좌스와이프. 최상단 서브탭(추천/베스트/...)이 쓰는
        swipe_subtab_left와는 다른 UI 영역(y좌표)이라 별도 함수로 분리한다."""
        w = self.driver.get_window_size()["width"]
        y = self._age_gender_tab_y()
        self.driver.swipe(int(w * 0.80), y, int(w * 0.20), y, 500)
        time.sleep(0.4)

    def swipe_age_gender_tab_right(self):
        w = self.driver.get_window_size()["width"]
        y = self._age_gender_tab_y()
        self.driver.swipe(int(w * 0.20), y, int(w * 0.80), y, 500)
        time.sleep(0.4)

    def get_all_age_gender_tab_names(self) -> list:
        """get_all_subtab_names와 동일한 방식(AOS: page_source 기반 y좌표 매칭)이되, 대상
        y좌표만 연령/성별 필터바 쪽으로 바꾼 버전. iOS는 이 화면 구조를 아직 실기기로 확인하지
        못해 우선 빈 목록을 반환한다(실기기 확인 후 보완 예정)."""
        if self.platform == "aos":
            import re
            import xml.etree.ElementTree as ET
            bounds_pattern = re.compile(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]')
            target_y = self._age_gender_tab_y()
            y_tolerance = int(self.driver.get_window_size()["height"] * 0.03)
            items = []
            seen = set()
            root = ET.fromstring(self.driver.page_source)
            for elem in root.iter():
                text = (elem.get("text") or "").strip()
                if not text:
                    continue
                m = bounds_pattern.match(elem.get("bounds", ""))
                if not m:
                    continue
                x1, y1, x2, y2 = map(int, m.groups())
                y_center = (y1 + y2) // 2
                if abs(y_center - target_y) <= y_tolerance and text not in seen:
                    seen.add(text)
                    items.append((x1, text))
            items.sort(key=lambda t: t[0])
            return [name for _, name in items]
        return []

    def _get_ios_besttab_content(self) -> str:
        """베스트 탭(연령/성별 필터 적용 랭킹 리스트, 최대 200위) 콘텐츠 블롭 원문 추출(iOS 전용).
        이 화면도 카테고리 목적지 화면과 동일하게 전체 텍스트가 하나의 XCUIElementTypeOther에
        뭉쳐서 노출되고, 풀 page_source 덤프(get_visible_content_item_names 등)는 이 화면처럼
        항목이 많을 때 WDA 타임아웃/세션 크래시를 일으키는 것이 실기기로 확인되어(200위까지
        스크롤 시 blob이 커짐), 기본 선택 탭("50대 남성")을 anchor로 스코프 조회한다. anchor
        뒤에는 "50대 여성 주간 베스트 필터"가 이어지고 곧바로 "1 <작품명>..."이 시작된다
        (실기기 확인됨)."""
        try:
            locator = (AppiumBy.IOS_CLASS_CHAIN,
                       f'**/XCUIElementTypeOther[`name CONTAINS "{self.DEFAULT_AGE_GENDER_TAB}"`]')
            blob = self.find_element(locator).get_attribute("name") or ""
        except Exception as e:
            self.log.warning(f"[_get_ios_besttab_content] 콘텐츠 추출 실패: {e}")
            return ""

        import re
        idx = blob.rfind(self.DEFAULT_AGE_GENDER_TAB)
        if idx < 0:
            return ""
        after = blob[idx + len(self.DEFAULT_AGE_GENDER_TAB):]
        match = re.search(r'\d+\s', after)
        return after[match.start():] if match else ""

    def _besttab_scroll_down(self):
        """베스트 탭 순회검증(collect_besttab_items_by_scroll) 전용 세로 스크롤(iOS 전용).
        카테고리 목적지 화면 전용 스크롤(_category_dest_scroll_down)과는 서로 다른 화면/모듈이라
        완전히 분리된 별도 함수로 유지한다. 실기기 확인 결과, 카테고리 화면과 동일한 0.95→0.08
        범위(거의 풀스크린 스와이프)는 이 화면(장르홈에 속한 베스트 탭)에서는 상단 탭바/하단
        네비게이션 바 경계에 걸쳐 제스처가 전혀 먹히지 않았다 - 연령/성별 탭바(y≈0.17) 바로
        아래 ~ 하단 네비바(y≈0.95) 이전 사이, 즉 작품 리스트 영역 안에서만 스와이프해야 정상
        동작한다(실기기 확인). AOS는 기존 공용 스크롤 함수(collect_items_by_vertical_scroll
        내부의 _vertical_swipe_up)를 그대로 사용하므로 이 함수는 iOS에서만 쓰인다."""
        size = self.driver.get_window_size()
        x = int(size["width"] * 0.5)
        self.driver.swipe(x, int(size["height"] * 0.85), x, int(size["height"] * 0.28), 600)
        time.sleep(1)

    def collect_besttab_items_by_scroll(self, max_scrolls: int = 30) -> list:
        """베스트 탭을 세로 스크롤하며 항목을 중복없이 순서대로 수집(1위/마지막(200위) 작품
        확인 목적). iOS는 풀 page_source 위험 때문에 전용 스코프 조회+전용 스크롤을 쓰고,
        AOS는 이 화면에 한해 page_source 방식이 위험하지 않아 기존 공용 함수를 그대로 쓴다."""
        if self.platform == "ios":
            seen, ordered = set(), []
            last_content = ""

            def add_new(content):
                nonlocal last_content
                if not content or content == last_content:
                    return
                delta = content[len(last_content):].strip() if content.startswith(last_content) else content
                last_content = content
                for item in self._split_ios_ranked_items(delta):
                    if item not in seen:
                        seen.add(item)
                        ordered.append(item)

            add_new(self._get_ios_besttab_content())
            stall = 0
            count = 0
            while stall < 2 and count < max_scrolls:
                self._besttab_scroll_down()
                count += 1
                before = len(ordered)
                add_new(self._get_ios_besttab_content())
                stall = 0 if len(ordered) > before else stall + 1

            if ordered:
                # 진짜 마지막(200위) 항목에 도달하면 그 뒤로 하단 네비게이션 바 라벨("수직
                # 스크롤 막대, N페이지 도구 막대 내 서재 검색 홈 알림 MY" 등)이 그대로
                # 이어붙어 추출되는 것이 실기기로 확인되어, 마지막 항목만 노이즈를 잘라낸다.
                idx = ordered[-1].find("수직 스크롤 막대")
                if idx > 0:
                    ordered[-1] = ordered[-1][:idx].strip()
            return ordered

        return self.collect_items_by_vertical_scroll(max_scrolls=max_scrolls)

    # 신작 탭 카테고리 서브탭(전체~만화잡지). 베스트 탭과 동일 화면 유형(장르홈 서브탭)이라
    # 잠정적으로 동일 좌표/방식을 재사용 - 실기기 확인 후 보완 예정.
    DEFAULT_NEWCONTENT_TAB = "전체"

    def _newcontent_subtab_locator(self, tab_name: str) -> tuple:
        if self.platform == "ios":
            return (AppiumBy.ACCESSIBILITY_ID, tab_name)
        return (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{tab_name}")')

    def is_newcontent_subtab_visible(self, tab_name: str, timeout: int = 3, log: bool = True) -> bool:
        locator = self._newcontent_subtab_locator(tab_name)
        if self.platform == "ios":
            result = self.is_element_present(locator, timeout=timeout)
        else:
            result = self.is_present(locator, timeout=timeout)
        if log:
            self.log.info(f"[신작탭_카테고리서브탭] {tab_name} {'✅' if result else '❌'}")
        return result

    def _newcontent_subtab_y(self) -> int:
        """신작 탭 카테고리 서브탭바 y좌표(비율). 베스트 탭 연령/성별 필터바와 동일 위치로
        추정(0.173) - 실기기 확인 후 보완 예정."""
        return int(self.driver.get_window_size()["height"] * 0.173)

    def swipe_newcontent_subtab_left(self):
        w = self.driver.get_window_size()["width"]
        y = self._newcontent_subtab_y()
        self.driver.swipe(int(w * 0.80), y, int(w * 0.20), y, 500)
        time.sleep(0.4)

    def swipe_newcontent_subtab_right(self):
        w = self.driver.get_window_size()["width"]
        y = self._newcontent_subtab_y()
        self.driver.swipe(int(w * 0.20), y, int(w * 0.80), y, 500)
        time.sleep(0.4)

    def get_all_newcontent_subtab_names(self) -> list:
        """get_all_age_gender_tab_names와 동일한 방식(AOS: page_source 기반 y좌표 매칭).
        iOS는 개별 요소 존재 확인(is_newcontent_subtab_visible)만으로 충분해 빈 목록 반환."""
        if self.platform == "aos":
            import re
            import xml.etree.ElementTree as ET
            bounds_pattern = re.compile(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]')
            target_y = self._newcontent_subtab_y()
            y_tolerance = int(self.driver.get_window_size()["height"] * 0.03)
            items = []
            seen = set()
            root = ET.fromstring(self.driver.page_source)
            for elem in root.iter():
                text = (elem.get("text") or "").strip()
                if not text:
                    continue
                m = bounds_pattern.match(elem.get("bounds", ""))
                if not m:
                    continue
                x1, y1, x2, y2 = map(int, m.groups())
                y_center = (y1 + y2) // 2
                if abs(y_center - target_y) <= y_tolerance and text not in seen:
                    seen.add(text)
                    items.append((x1, text))
            items.sort(key=lambda t: t[0])
            return [name for _, name in items]
        return []

    def _get_ios_newcontenttab_content(self) -> str:
        """신작 탭(카테고리 서브탭 적용 카드 리스트, 순위 없음) 콘텐츠 블롭 원문 추출(iOS 전용).
        베스트 탭과 동일한 이유로 풀 page_source 대신 기본 선택 카테고리("전체")를 anchor로
        스코프 조회한다. anchor 뒤에는 나머지 카테고리 서브탭 이름들과 "최신순 필터"가 먼저
        나오고 그 다음에야 실제 작품 목록이 시작되는 것이 실기기로 확인되어(예:
        "전체 해외순정 판타지/SF ... 만화잡지 최신순 필터 [코믹] 단죄당한 악역 영애는..."),
        "필터" 뒤부터를 실제 콘텐츠 시작점으로 취급한다."""
        try:
            locator = (AppiumBy.IOS_CLASS_CHAIN,
                       f'**/XCUIElementTypeOther[`name CONTAINS "{self.DEFAULT_NEWCONTENT_TAB}"`]')
            blob = self.find_element(locator).get_attribute("name") or ""
        except Exception as e:
            self.log.warning(f"[_get_ios_newcontenttab_content] 콘텐츠 추출 실패: {e}")
            return ""
        idx = blob.rfind(self.DEFAULT_NEWCONTENT_TAB)
        if idx < 0:
            return ""
        after = blob[idx + len(self.DEFAULT_NEWCONTENT_TAB):]
        marker = after.rfind("필터")
        if marker >= 0:
            after = after[marker + len("필터"):]
        return after.strip()

    def _newcontenttab_scroll_down(self):
        """신작 탭 순회검증 전용 세로 스크롤(iOS 전용). 베스트 탭에서 실기기로 확인된 안전
        범위(카테고리 서브탭 바로 아래 ~ 하단 네비바 이전 사이)를 동일하게 적용한다."""
        size = self.driver.get_window_size()
        x = int(size["width"] * 0.5)
        self.driver.swipe(x, int(size["height"] * 0.85), x, int(size["height"] * 0.28), 600)
        time.sleep(1)

    def collect_newcontenttab_items_by_scroll(self, max_scrolls: int = 30) -> list:
        """신작 탭을 세로 스크롤하며 항목(순위 없는 카드)을 중복없이 순서대로 수집."""
        if self.platform == "ios":
            seen, ordered = set(), []
            last_content = ""

            def add_new(content):
                nonlocal last_content
                if not content or content == last_content:
                    return
                delta = content[len(last_content):].strip() if content.startswith(last_content) else content
                last_content = content
                for item in self._split_ios_card_items("신작탭", delta):
                    if item not in seen:
                        seen.add(item)
                        ordered.append(item)

            add_new(self._get_ios_newcontenttab_content())
            stall = 0
            count = 0
            while stall < 2 and count < max_scrolls:
                self._newcontenttab_scroll_down()
                count += 1
                before = len(ordered)
                add_new(self._get_ios_newcontenttab_content())
                stall = 0 if len(ordered) > before else stall + 1

            if ordered:
                idx = ordered[-1].find("수직 스크롤 막대")
                if idx > 0:
                    ordered[-1] = ordered[-1][:idx].strip()
            return ordered

        return self.collect_items_by_vertical_scroll(max_scrolls=max_scrolls)

    def _get_ocr_top_title(self, top_ratio_start: float = 0.06, top_ratio_end: float = 0.14) -> str:
        """상단 타이틀 줄만 스크린샷+OCR로 읽어 실제 노출된 텍스트 자체를 추출한다.
        get_current_top_title()이 이 화면에서 요소값을 제대로 못 읽어(빈 값, 하단 탭바
        텍스트, 캐러셀 아이템명 등 엉뚱한 값이 잡힘 - "BL 키워드 검색", "BL만화 실시간
        랭킹" 더보기 목적지에서 실기기 확인됨) 타이틀 불일치로 오판하는 문제의 폴백.

        기존에는 상태바를 포함한 넓은 영역(0~12%)을 그대로 OCR에 넣어 시계/배터리
        아이콘이 잡음으로 섞여 인식률이 낮았다(실기기 확인 - "BL 키워드 검색"이
        "RI 키위드거새" 등으로 깨짐). 상태바를 제외한 타이틀 줄만 좁게 잘라내고
        (grayscale 변환 + 3배 확대 + 명암 대비 강화), 단일 텍스트 줄 인식에 특화된
        --psm 6 옵션을 쓰면 인식률이 크게 개선됨을 실기기로 확인했다."""
        try:
            import pytesseract
            from PIL import Image, ImageOps
            import io
            png = self.driver.get_screenshot_as_png()
            img = Image.open(io.BytesIO(png))
            w, h = img.size
            crop = img.crop((0, int(h * top_ratio_start), w, int(h * top_ratio_end)))
            crop = crop.convert("L")
            crop = crop.resize((crop.width * 3, crop.height * 3), Image.LANCZOS)
            crop = ImageOps.autocontrast(crop)
            text = pytesseract.image_to_string(crop, lang="kor+eng", config="--psm 6").strip()
            return " ".join(text.split())
        except Exception as e:
            self.log.warning(f"[_get_ocr_top_title] OCR 추출 실패: {e}")
            return ""

    def _korean_only(self, text: str) -> str:
        """문자열에서 한글 음절만 추출한다. "BL" 같은 영문 접두어는 이 앱 폰트 스타일
        때문에 OCR이 자주 오인식하지만("BL만화 실시간 랭킹" → "8Ｌ.만화 실시간 랭킹"
        등 실기기 확인됨) 한글 부분은 안정적으로 인식되어, 힌트/OCR 텍스트 비교 시
        영문·공백·기호 차이에 영향받지 않도록 한글만 남겨 비교한다."""
        import re
        return re.sub(r'[^가-힣]', '', text or "")


class WebtoonGenrePage(ComicGenrePage):
    """웹툰 장르홈 - ComicGenrePage와 동일 구조(요소값만 다름)라 상속받아 공용 로직
    (카테고리 순회검증에 쓰이는 tap_category_submenu, get_current_top_title, 서브탭/
    카테고리 버튼 탭 등)을 그대로 재사용한다. _loc()만 오버라이드해 웹툰 전용 로케이터
    클래스(AOS_WEBTOON_GENRE/IOS_WEBTOON_GENRE)를 바라보게 하고, 서브탭 구성/카테고리
    상위·하위메뉴처럼 실제로 값이 다른 것만 이 클래스에 새로 정의한다."""
    SUBTAB_LOCATOR = {
        "추천": "SUBTAB_RECOMMEND",
    }

    CATEGORY_TOPMENU_LOCATOR = {
        "웹툰":    "CATEGORY_TOPMENU_WEBTOON",
        "BL 웹툰": "CATEGORY_TOPMENU_BL_WEBTOON",
    }

    CATEGORY_SUBMENUS = {
        "웹툰": [
            "웹툰 전체", "로판", "로맨스", "드라마", "GL", "판타지/SF",
            "공포/추리", "코믹", "액션/무협", "스포츠/학원",
        ],
        "BL 웹툰": ["BL 웹툰 전체"],
    }

    # 퀵메뉴: 사용자가 확인해준 4개("이달의 신작", "이벤트", "리디온리", "리다무")만 우선
    # 반영. 실제로는 총 11개라 나머지 7개는 실기기 확인 후 추가 필요.
    QUICK_MENU_LOCATOR = {
        "이달의 신작": "MONTHLY_NEW_QUICK",
        "이벤트":     "EVENT_QUICK",
        "리디온리":   "RIDIONLY_QUICK",
        "리다무":     "RIDAMU_QUICK",
    }

    # 실기기 미확인 - 만화 장르홈의 동일 패턴("RIDI ONLY 만화" 등)으로 추정한 값.
    # 실기기 확인 후 실제 목적지 타이틀로 보완 필요.
    QUICK_MENU_EXPECTED_TITLE = {
        "이달의 신작": "이달의 신작",
        "이벤트":     "이벤트",
        "리디온리":   "RIDI ONLY 웹툰",
        "리다무":     "리다무",
    }

    # 추천 탭 섹션 - "웹툰/만화 키워드 검색"은 만화 장르홈과 동일한 문구/의미로 보여
    # ComicGenrePage.SECTION_LOCATOR의 문구를 그대로 재사용(키는 사용자가 알려준 표기,
    # 값은 위 AOS_WEBTOON_GENRE/IOS_WEBTOON_GENRE에 새로 추가한 로케이터).
    SECTION_LOCATOR = {
        "방금 본 작품과 비슷한":     "SECTION_SIMILAR_RECENT",
        "웹툰 실시간 랭킹":         "SECTION_REALTIME_RANKING",
        "요일별 웹툰":              "SECTION_WEEKDAY_WEBTOON",
        "기다리면 무료로 시작해!":    "SECTION_WAIT_FREE",
        "오늘리디의 발견":          "SECTION_TODAY_DISCOVERY",
        "구매이력기반 AI 추천":      "SECTION_AI_PURCHASE",
        "웹툰/만화 키워드검색":       "SECTION_KEYWORD_SEARCH",
        "웹툰 베스트":              "SECTION_BEST",
        "지금리디에서만볼수있는 만화": "SECTION_RIDI_EXCLUSIVE",
        "새로나온작품":             "SECTION_NEW_ARRIVALS",
        "취향저격 AI추천 섹션":      "SECTION_AI_TASTE",
    }

    def _loc(self, attr: str):
        cls = AOS_WEBTOON_GENRE if self.platform == "aos" else IOS_WEBTOON_GENRE
        return getattr(cls, attr)

    def enter_webtoon_genrehome(self):
        self.open_deeplink(DeepLinks.WEBTOON_RECOMMEND_HOME)
        self.log.info("[진입] 웹툰 장르홈 진입")

    def is_webtoon_genrehome_displayed(self) -> bool:
        return self.is_present(self._loc("SUBTAB_RECOMMEND"))


class WebnovelGenrePage(ComicGenrePage):
    """웹소설 장르홈 - WebtoonGenrePage와 동일한 이유로 ComicGenrePage를 상속해 카테고리
    순회검증 공용 로직을 재사용한다. _loc()만 웹소설 전용 로케이터 클래스
    (AOS_WEBNOVEL_GENRE/IOS_WEBNOVEL_GENRE)를 바라보게 오버라이드하고, 서브탭 구성/
    카테고리 상위·하위메뉴처럼 실제로 값이 다른 것만 이 클래스에 새로 정의한다."""
    SUBTAB_LOCATOR = {
        "추천": "SUBTAB_RECOMMEND",
    }

    CATEGORY_TOPMENU_LOCATOR = {
        "로맨스 웹소설": "CATEGORY_TOPMENU_ROMANCE_NOVEL",
        "로맨스 e북":   "CATEGORY_TOPMENU_ROMANCE_EBOOK",
        "로판 웹소설":   "CATEGORY_TOPMENU_FANTASY_ROMANCE_NOVEL",
        "로판 e북":     "CATEGORY_TOPMENU_FANTASY_ROMANCE_EBOOK",
        "판타지 웹소설": "CATEGORY_TOPMENU_FANTASY_NOVEL",
        "판타지 e북":   "CATEGORY_TOPMENU_FANTASY_EBOOK",
        "BL 웹소설":    "CATEGORY_TOPMENU_BL_NOVEL",
        "BL 소설 e북":  "CATEGORY_TOPMENU_BL_EBOOK",
    }

    CATEGORY_SUBMENUS = {
        "로맨스 웹소설": ["로맨스 웹소설 전체", "현대물", "역사/시대물"],
        "로맨스 e북": ["로맨스 e북 전체", "현대물", "역사/시대물", "할리퀸 소설", "하이틴"],
        "로판 웹소설": ["로판 웹소설 전체", "동양풍 로판", "서양풍 로판", "가상 세계 로판"],
        "로판 e북": ["로판 e북 전체", "동양풍 로판", "서양풍 로판", "가상 세계 로판", "해외 소설"],
        "판타지 웹소설": ["판타지 웹소설 전체", "정통 판타지", "퓨전 판타지", "현대 판타지", "무협 소설"],
        "판타지 e북": [
            "판타지 e북 전체", "정통 판타지", "퓨전 판타지", "현대 판타지", "게임 판타지",
            "대체 역사물", "스포츠물", "신무협", "전통 무협",
        ],
        "BL 웹소설": ["BL 웹소설 전체", "현대물", "판타지물", "역사/시대물"],
        "BL 소설 e북": ["BL 소설 e북 전체", "현대물", "판타지물", "역사/시대물", "해외 소설"],
    }

    def _loc(self, attr: str):
        cls = AOS_WEBNOVEL_GENRE if self.platform == "aos" else IOS_WEBNOVEL_GENRE
        return getattr(cls, attr)

    def enter_webnovel_genrehome(self):
        self.open_deeplink(DeepLinks.WEBNOVEL_RECOMMEND_HOME)
        self.log.info("[진입] 웹소설 장르홈 진입")

    def is_webnovel_genrehome_displayed(self) -> bool:
        """iOS 실기기 확인 결과, 웹소설 장르홈의 서브탭 바("추천 로맨스 로판 판타지 BL")는
        만화/웹툰과 달리 개별 접근성 요소로 노출되지 않고 화면 전체가 하나의 블롭으로 뭉쳐서
        (2026-07-24) 표준 accessibility id 검색(단일 "추천", 중복 "추천 추천" 둘 다)으로 찾을 수
        없다 - 블롭 안에 "추천" 텍스트가 포함되는지로 대신 확인한다. AOS와 다른 장르홈(만화 등)
        은 이 문제가 없어 영향받지 않도록 이 클래스에만 좁게 적용한다."""
        if self.platform == "ios":
            try:
                locator = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "추천"`]')
                return "추천" in (self.find_element(locator).get_attribute("name") or "")
            except Exception:
                return False
        return self.is_present(self._loc("SUBTAB_RECOMMEND"))

    def click_subtab(self, tab_name: str, log: bool = True):
        """ComicGenrePage.click_subtab과 동일하되, iOS의 "추천" 탭 한정으로 예외 처리한다.
        웹소설 딥링크(WEBNOVEL_RECOMMEND_HOME)가 이미 "추천" 서브탭으로 바로 진입시키고,
        이 탭 자체가 위 is_webnovel_genrehome_displayed에서 설명한 이유로 개별 접근성 요소가
        없어 탭할 대상이 없다(실기기 확인됨, 2026-07-24) - 이미 선택된 상태이므로 별도 탭 없이
        통과시킨다. 다른 탭/플랫폼/다른 장르홈은 기존 동작 그대로 유지."""
        if self.platform == "ios" and tab_name == "추천":
            if log:
                self.log.info(f"[서브탭클릭] {tab_name} (iOS 웹소설: 딥링크로 이미 선택됨 - 탭 생략)")
            return
        super().click_subtab(tab_name, log=log)


class GeneralbookGenrePage(ComicGenrePage):
    """일반도서 장르홈 - WebtoonGenrePage와 동일한 이유로 ComicGenrePage를 상속해 카테고리
    순회검증 공용 로직을 재사용한다. _loc()만 일반도서 전용 로케이터 클래스
    (AOS_GENERALBOOK_GENRE/IOS_GENERALBOOK_GENRE)를 바라보게 오버라이드하고, 서브탭 구성/
    카테고리 상위·하위메뉴처럼 실제로 값이 다른 것만 이 클래스에 새로 정의한다."""
    SUBTAB_LOCATOR = {
        "추천": "SUBTAB_RECOMMEND",
    }

    CATEGORY_TOPMENU_LOCATOR = {
        "소설":         "CATEGORY_TOPMENU_NOVEL",
        "경영/경제":     "CATEGORY_TOPMENU_BUSINESS",
        "인문/사회/역사": "CATEGORY_TOPMENU_HUMANITIES",
        "자기계발":      "CATEGORY_TOPMENU_SELF_HELP",
        "에세이/시":     "CATEGORY_TOPMENU_ESSAY_POETRY",
        "여행":         "CATEGORY_TOPMENU_TRAVEL",
        "종교":         "CATEGORY_TOPMENU_RELIGION",
        "외국어":        "CATEGORY_TOPMENU_FOREIGN_LANG",
        "과학":         "CATEGORY_TOPMENU_SCIENCE",
        "진로/교육/교재": "CATEGORY_TOPMENU_CAREER_EDU",
        "컴퓨터/IT":     "CATEGORY_TOPMENU_COMPUTER_IT",
        "건강/다이어트":  "CATEGORY_TOPMENU_HEALTH_DIET",
        "가정/생활":     "CATEGORY_TOPMENU_HOME_LIFE",
        "어린이/청소년":  "CATEGORY_TOPMENU_KIDS_TEEN",
        "해외도서":      "CATEGORY_TOPMENU_FOREIGN_BOOK",
        "잡지":         "CATEGORY_TOPMENU_MAGAZINE",
    }

    CATEGORY_SUBMENUS = {
        "소설": [
            "소설 전체", "한국소설", "영미소설", "일본 소설", "중국 소설",
            "북유럽 소설", "독일 소설", "프랑스 소설", "기타 국가 소설",
        ],
        "경영/경제": [
            "경영/경제 전체", "경영일반", "경제일반", "마케팅/세일즈",
            "재테크/금융/부동산", "CEO/리더십",
        ],
        "인문/사회/역사": ["인문/사회/역사 전체", "인문", "정치/사회", "예술/문화", "역사"],
        "자기계발": [
            "자기계발 전체", "성공/삶의자세", "기획/창의/리더십", "설득/화술/협상",
            "취업/창업", "여성", "인간관계",
        ],
        "에세이/시": ["에세이/시 전체", "에세이", "시"],
        "여행": ["여행 전체", "국내여행", "해외여행"],
        "종교": ["종교 전체", "종교일반", "가톨릭", "기독교(개신교)", "불교", "기타"],
        "외국어": ["외국어 전체", "비즈니스영어", "일반영어", "제2외국어", "어학시험"],
        "과학": ["과학 전체", "과학일반", "수학", "자연과학", "응용과학"],
        "진로/교육/교재": [
            "진로/교육/교재 전체", "공부법", "특목고/자사고", "대입 수시", "대입 논술",
            "대입 합격수기", "진로 탐색", "유학/MBA", "교재/수험서",
        ],
        "컴퓨터/IT": [
            "컴퓨터/IT 전체", "IT 비즈니스", "개발/프로그래밍", "컴퓨터/앱 활용",
            "IT자격증", "IT 해외원서",
        ],
        "건강/다이어트": ["건강/다이어트 전체", "다이어트/운동/스포츠", "스타일/뷰티", "건강"],
        "가정/생활": ["가정/생활 전체", "결혼/임신/출산", "육아/자녀교육", "취미/요리/기타"],
        "어린이/청소년": ["어린이/청소년 전체", "유아", "어린이", "청소년"],
        "해외도서": ["해외도서 전체"],
        "잡지": [
            "잡지 전체", "경영/재테크", "문학/교양", "여성/패션/뷰티", "디자인/예술",
            "건강/스포츠", "취미/여행/요리", "과학/IT", "종교", "만화",
        ],
    }

    def _loc(self, attr: str):
        cls = AOS_GENERALBOOK_GENRE if self.platform == "aos" else IOS_GENERALBOOK_GENRE
        return getattr(cls, attr)

    def enter_generalbook_genrehome(self):
        self.open_deeplink(DeepLinks.GENERAL_RECOMMEND_HOME)
        self.log.info("[진입] 일반도서 장르홈 진입")

    def is_generalbook_genrehome_displayed(self) -> bool:
        return self.is_present(self._loc("SUBTAB_RECOMMEND"))

    def _scroll_category_page_down(self):
        """도서 카테고리 전용 오버라이드(AOS만). 공용 구현(_swipe, 화면 20~80% 영역 스와이프)이
        상위메뉴를 접었다 다시 편 직후(하위메뉴가 2개 정도만 보이는 상태)에는 반복 실행해도
        화면이 전혀 움직이지 않는 현상이 실기기로 확인되어(2026-07-24, "컴퓨터/IT" 재펼침 직후
        "개발/프로그래밍"을 찾는 스크롤이 10회를 반복해도 화면이 그대로임 - 사용자가 실기기로
        직접 확인), 클릭 가능한 메뉴 텍스트와 겹치지 않도록 화면 오른쪽 가장자리(90%)에서 세로로
        스와이프하는 좌표 기반 방식으로 바꿔본다. iOS/다른 카테고리 클래스는 영향 없도록 이
        클래스에만 오버라이드한다."""
        if self.platform != "aos":
            super()._scroll_category_page_down()
            return
        size = self.driver.get_window_size()
        x = int(size["width"] * 0.9)
        start_y = int(size["height"] * 0.8)
        end_y = int(size["height"] * 0.3)
        self.driver.swipe(x, start_y, x, end_y, 600)
        self.log.info("[swipe] direction=down (도서 카테고리 전용 좌표)")
        time.sleep(0.5)

    def scroll_topmenu_to_top(self, topmenu_name: str, max_scroll: int = 10, top_ratio: float = 0.3):
        """상위메뉴 헤더를 펼치기 전에 화면 상단 근처(top_ratio 이내)로 미리 스크롤한다.
        일반도서 카테고리는 상위메뉴가 16개(다른 카테고리는 2~8개)로 훨씬 많아, 펼친 뒤
        하위메뉴 전체가 표시될 공간을 미리 확보해두면 좋다.

        top_ratio 기본값 0.3: 기존 20~80% 영역 스와이프(_swipe) 방식으로는 화면 상단 20%
        이내로 올라오지 않는다는 게 실기기로 확인됐었지만(2026-07-24), 그건 그 스와이프
        구현 자체가 상위메뉴를 펼친 뒤 화면을 제대로 못 움직이는 문제와 같은 원인이었다 -
        _scroll_category_page_down을 화면 오른쪽 가장자리 좌표 기반 스와이프로 교체한 뒤
        실기기로 재확인한 결과 0.3까지도 정상 도달 가능해 상향했다. 다른 카테고리 클래스는
        상위메뉴가 적어 이 메서드 자체가 필요 없어 이 클래스에만 둔다.

        "잡지"(맨 마지막 상위메뉴)는 카테고리 화면 진입 직후 아직 화면에 전혀 렌더링되지
        않은 상태라 find_element가 NoSuchElementException을 내는데, 이를 "포기하고 즉시
        리턴"으로 처리했더니 스크롤을 한 번도 안 한 채 다음 단계로 넘어가버려 겨우 스와이프
        1회만큼만 스크롤된 상태로 하위메뉴를 펼치고 탭하게 되는 문제가 실기기로 확인됐다
        (2026-07-24 - "잡지 전체" 탭이 재탭까지 다 실패). 요소가 아직 안 보여 못 찾은 것도
        "찾을 때까지 스크롤해야 하는" 정상 케이스이므로, 예외가 나도 포기하지 않고 계속
        스크롤하며 재시도한다."""
        locator = self._loc(self.CATEGORY_TOPMENU_LOCATOR[topmenu_name])
        h = self.driver.get_window_size()["height"]
        for _ in range(max_scroll):
            try:
                y = self.find_element(locator).location["y"]
            except Exception:
                self._scroll_category_page_down()
                continue
            if y <= h * top_ratio:
                return
            self._scroll_category_page_down()

    def expand_category_topmenu_light(self, topmenu_name: str):
        """expand_category_topmenu와 달리 마지막 하위메뉴 사전탐색(최대 15회 스크롤 + 15회
        역스크롤이라 오래 걸림)을 생략하고, 상위메뉴 토글만 스크롤해 찾아 탭한다. 도서
        카테고리(GeneralbookGenrePage)는 상위메뉴가 16개로 많아 그 사전탐색이 "진로/교육/
        교재" 같은 뒤쪽 상위메뉴에서 3분 이상 낭비되는 문제가 실기기로 확인되어(2026-07-24)
        최초 펼치기에 이 가벼운 버전을 쓴다. 펼친 뒤 하위메뉴를 찾는 스크롤은 이후
        tap_category_submenu가 담당하며, 하위메뉴 상세페이지에서 뒤로가기해도 펼침 상태와
        스크롤 위치가 그대로 유지되므로(실기기 확인됨) 하위메뉴마다 다시 접었다 펼 필요는
        없다.

        iOS에서 "진로/교육/교재"처럼 뒤쪽 상위메뉴를 탭했는데 실제로는 안 펼쳐진 채(탭이
        빗나가거나 스크롤 직후 좌표가 아직 안정화되지 않아) 그대로 하위메뉴 탐색을 시작해버려
        계속 실패하는 문제가 실기기로 확인되어(2026-07-24), 탭 후 첫번째 하위메뉴가 실제로
        보이는지 확인하고 안 보이면 재탭한다."""
        locator = self._loc(self.CATEGORY_TOPMENU_LOCATOR[topmenu_name])
        first_submenu = self.CATEGORY_SUBMENUS[topmenu_name][0]
        first_locator = self._category_item_locator(first_submenu)
        for attempt in range(3):
            self._scroll_category_item_into_view(locator)
            self.click(locator)
            time.sleep(1)
            if self.is_present(first_locator, timeout=3):
                self.log.info(f"[카테고리] 상위메뉴 펼침: {topmenu_name}")
                return
            self.log.warning(f"[카테고리] 상위메뉴 펼침 미확인 - 재탭({attempt + 1}/3): {topmenu_name}")
        self.log.warning(f"[카테고리] 상위메뉴 펼침 끝내 미확인: {topmenu_name}")
