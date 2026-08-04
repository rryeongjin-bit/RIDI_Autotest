from pages.base_page import *
from locators.contentshome import *
from locators.genrehome import *
from locators.common import *
from data.test_data import *
from pages.home_page import Alertnotification

class MainhomePage(BasePage):
    def launch_and_verify_genrehome(self) -> bool:
        """앱 실행 직후 뜨는 팝업들을 정리하고 장르홈 노출까지 확인한다.

        테스트 6개 모듈의 TestLaunchApp이 동일한 코드를 복붙해 갖고 있던 것을 여기로 모았다
        (2026-07-31). 테스트에는 pytest.skip 조건과 assert만 남는다 - 판정은 테스트의 책임이라
        여기서는 예외를 던지지 않고 bool로 반환한다."""
        alert = Alertnotification(self.driver, self.platform)
        if alert.is_noti_displayed():
            alert.click_noti_alert()
        else:
            self.log.info("[SKIP] 알림 권한 팝업 미노출")
        time.sleep(3)
        alert.close_braze_if_present()
        return self.is_genrehome_displayed()

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

    def enter_genrehome(self):
        """자기 장르홈으로 진입한다."""
        self.enter_comic_genrehome()

    def is_genrehome_displayed(self) -> bool:
        """자기 장르홈이 노출 중인지 판정한다."""
        return self.is_comic_genrehome_displayed()

    def _enter_own_genrehome(self):
        """iOS 결정론적 스크롤의 전체리셋에서 재진입할 "자기 장르홈".

        예전에는 이 자리에 enter_comic_genrehome()이 하드코딩돼 있어, 웹툰/웹소설 페이지의
        섹션을 찾는 중에도 **만화 장르홈으로 들어가버렸다**(2026-08-02 iOS 로그 - 웹툰
        "요일별 웹툰" 전체리셋 직후 "[진입] 만화 장르홈 진입"). 만화 페이지는 이 기본
        구현으로 기존과 동일하게 동작하고, 하위 클래스가 각자 자기 장르홈으로 오버라이드한다."""
        self.enter_comic_genrehome()

    def enter_comic_genrehome(self):
        self.open_deeplink(DeepLinks.COMIC_RECOMMEND_HOME)
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
        ComicGenrePage._ios_scroll_state = None
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
        "리디", "리디 (S)",  
        "STAGE", "S\nT\nA\nG\nE", "S T A G E",  
        "CANARY", "C\nA\nN\nA\nR\nY", "C A N A R Y",  
        "topCarouselSafeArea", 
        "오늘, 리디의 발견",  
    }

    NOISE_LABEL_PREFIXES = ("수직 스크롤 막대",)

    def _is_noise_top_title_candidate(self, text: str) -> bool:
        if text in self.PERSISTENT_TAB_LABELS or text.startswith(self.NOISE_LABEL_PREFIXES):
            return True
       
        import re
        if re.fullmatch(r'[\d.,()\s]+', text):
            return True
   
        if "\n" in text:
            return True
       
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
                if y1 < h * 0.09:
                    candidates.append((y1, x1, text))
        else:
            for elem in root.iter():
                name = (elem.get("name") or "").strip()
              
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
   
        import re
        title = re.sub(r'\s*(수직|수평) 스크롤 막대,?\s*\d*페이지', '', title).strip()
        return title

    # 더보기 목적지 타이틀이 빈 값일 때만 재조회하는 폴링 창(초).
    DEST_TITLE_POLL_SECONDS = 10

    def _is_dest_hint_present_on_top(self, hint: str) -> bool:
        """목적지 화면 상단 영역에 기대 타이틀 문구가 존재하는지 확인한다."""
        try:
            h = self.driver.get_window_size()["height"]
            for y1, x1, y2, x2, text in self._iter_text_elements():
                if y1 < h * 0.09 and hint in text:
                    self.log.info(
                        f"[목적지타이틀] 상단(y={y1})에서 기대 문구 '{hint}' 확인 "
                        f"- 잔여 요소가 위에 있어 최상단 텍스트로는 판별 불가한 화면"
                    )
                    return True
        except Exception as e:
            self.log.warning(f"[목적지타이틀] 상단 존재 확인 실패: {e}")
        return False

    def _read_dest_title_with_poll(self, section_name: str) -> str:
        def read_once() -> str:
            try:
                return self.get_current_top_title()
            except Exception as e:
                self.log.warning(f"[{section_name}] 목적지 타이틀 확인 실패(iOS WDA 이슈 가능): {e}")
                return ""

        title = read_once()
        if title:
            return title

        deadline = time.time() + self.DEST_TITLE_POLL_SECONDS
        attempt = 1
        while time.time() < deadline:
            attempt += 1
            time.sleep(1)
            title = read_once()
            if title:
                self.log.info(
                    f"[{section_name}] 목적지 타이틀이 {attempt}회째 조회에서 확인됨"
                    f"(직전까지 헤더 미렌더링) - '{title}'"
                )
                return title
        self.log.warning(
            f"[{section_name}] 목적지 타이틀이 {self.DEST_TITLE_POLL_SECONDS}초 폴링에도 빈 값 "
            f"- 화면 전환 실패이거나 헤더가 끝내 그려지지 않은 경우"
        )
        return ""

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
        "월간 캘린더": "만화 캘린더",  
        "리디온리":   "RIDI ONLY 만화",
    }

    def verify_quickmenu_destination_title(self, menu_name: str, timeout: int = 6, interval: float = 1.0) -> bool:
        """퀵메뉴 선택 후 진입한 화면의 타이틀이 기대값을 포함하는지 비교 (목적지별 로딩 속도가 달라 재시도).
        페이지 전환 직후 콘텐츠가 아직 로딩 중일 수 있어(더보기 화면과 동일한 이유) 확인 전 대기한다."""
        time.sleep(10)
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
        "오직 리디!":                    "SECTION_RIDI_ONLY",
        "새로 나온 작품":                 "SECTION_NEW_ARRIVALS",
        "만화 베스트":                    "SECTION_BEST",
        "와 비슷한":                      "SECTION_SIMILAR_WORK",  
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
        "님의 취향 저격 AI 추천":          "SECTION_AI_TASTE", 
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
        elements = self.find_elements(self._loc(attr))
        if not elements:
            raise NoSuchElementException(f"[_section_title_rect] {section_name} 요소 없음")
        h = self.driver.get_window_size()["height"]
        on_screen = [e for e in elements if 0 <= e.location["y"] < h]
        if len(elements) > 1:
            self.log.warning(
                f"[_section_title_rect] {section_name} 매치 {len(elements)}개 "
                f"(화면 내 {len(on_screen)}개): "
                f"{[(e.location['y'], e.size['height']) for e in elements]}"
            )
        el = (on_screen or elements)[0]
        loc, size = el.location, el.size
        return {"top": loc["y"], "bottom": loc["y"] + size["height"]}

  
    AOS_VERTICAL_SCROLLVIEW_SELECTOR = 'new UiSelector().className("android.widget.ScrollView")'

    def _vertical_swipe_up(self):
        if self.platform == "aos":
            self.driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                f'new UiScrollable({self.AOS_VERTICAL_SCROLLVIEW_SELECTOR}).scrollForward()'
            )
        else:
            size = self.driver.get_window_size()
            x = int(size["width"] * 0.5)
            h = size["height"]
            self.driver.swipe(
                x, int(h * self.SECTION_SEARCH_STEP_START_RATIO),
                x, int(h * self.SECTION_SEARCH_STEP_END_RATIO),
                800,
            )
        time.sleep(1)

    SECTION_SEARCH_STEP_START_RATIO = 0.78
    SECTION_SEARCH_STEP_END_RATIO   = 0.32

    def _section_search_scroll_up(self):
        size = self.driver.get_window_size()
        x = int(size["width"] * 0.5)
        h = size["height"]
        if self.platform == "aos":
            self.driver.swipe(
                x, int(h * self.SECTION_SEARCH_STEP_START_RATIO),
                x, int(h * self.SECTION_SEARCH_STEP_END_RATIO),
                800,
            )
            time.sleep(1)
            return
        self._vertical_swipe_up()

    def _section_search_scroll_down(self):
        size = self.driver.get_window_size()
        x = int(size["width"] * 0.5)
        h = size["height"]
        if self.platform == "aos":
            self.driver.swipe(
                x, int(h * self.SECTION_SEARCH_STEP_END_RATIO),
                x, int(h * self.SECTION_SEARCH_STEP_START_RATIO),
                800,
            )
            time.sleep(1)
            return
        self._vertical_swipe_down_ios()

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
        "BL 키워드 검색":                (0.910, 0.662),
        "BL만화 실시간 랭킹":             (0.910, 0.672),
        "BL만화 베스트":                 (0.913, 0.502),
        "BL만화 e북 이벤트":              (0.913, 0.531),
        "지금, 리디에서만 볼 수 있는 BL만화": (0.913, 0.553),
        "BL만화 e북 신간":                (0.913, 0.506),
    }
  
    IOS_SECTION_SUBTAB = {
        "BL 키워드 검색":                "BL",
        "BL만화 실시간 랭킹":             "BL",
        "BL만화 베스트":                 "BL",
        "BL만화 e북 이벤트":              "BL",
        "지금, 리디에서만 볼 수 있는 BL만화": "BL",
        "BL만화 e북 신간":                "BL",
    }
   
    IOS_SECTION_MORE_DEST_HINT = {
        "지금 많이 읽고 있는 만화": "지금 많이 읽고 있는 만화",
        "구매이력 기반 AI 추천":   "구매이력 기반 AI 추천",
        "오직 리디!":                    "이벤트",
        "웹툰/만화 키워드 검색":            "웹툰/만화 키워드 검색",
        "이벤트":                        "이벤트",
        "3분기 애니 원작 총집합!":          "3분기 애니 원작 총집합!",
        "만화를 특가 세트로!":             "만화를 특가 세트로!",
        "앞권 무료로 맛보기!":             "앞권 무료로 맛보기!",
        "지금, 리디에서만 볼 수 있는 만화":  "RIDI ONLY 만화",
        "2026 상반기 베스트 만화는?":       "2026 상반기 베스트 만화는?",
        "인생에 스포츠 만화는 필수입니다.":  "인생에 스포츠 만화는 필수입니다.",
        "그날 인류는 떠올렸다.":           "그날 인류는 떠올렸다.",
        "만화는 리디! 제대로 즐기는 법":    "만화는 리디! 제대로 즐기는 법",
        "별점 5점만점 명예의 전당":         "별점 5점만점 명예의 전당",
        "역대 만화 대상 수상작 모아보기":    "역대 만화 대상 수상작 모아보기",
        "이벤트 더 보기":                 "이벤트 더 보기",
        "BL 키워드 검색":                "BL 키워드 검색",
        "BL만화 실시간 랭킹":             "BL만화 실시간 랭킹",
        "BL만화 베스트":                 "BL만화 베스트",
        "BL만화 e북 이벤트":              "이벤트",
        "지금, 리디에서만 볼 수 있는 BL만화": "RIDI ONLY BL 웹툰/만화",
        "BL만화 e북 신간":                "BL만화 e북 신간",
    }
   
    _ios_scroll_state = None
    AOS_PERSONALIZED_SECTIONS = {
        "방금 본 작품과 비슷한",
        "구매이력기반 AI 추천",
        "구매이력 기반 AI 추천",
        "BL 구매이력기반 AI 추천",
        "내 취향 추천 신작",
        "이 작품 어때요",
        "이 판타지 어때요?",
        "취향저격 AI추천 섹션",
    }

    IOS_COLLECT_QUERY_EVERY_SWIPE = False
    IOS_LOG_SECTION_CONTENT_PREVIEW = False

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
        "BL 키워드 검색":                1,
        "BL만화 실시간 랭킹":             2,
        "BL만화 베스트":                 5,
        "BL만화 e북 이벤트":              7,
        "지금, 리디에서만 볼 수 있는 BL만화": 9,
        "BL만화 e북 신간":                11,
    }
 
    IOS_SECTION_END_MARKERS = [
        "방금 본 작품과 비슷한", "지금 많이 읽고 있는 만화", "오늘, 리디의 발견",
        "구매이력 기반 AI 추천", "오직 리디!", "새로 나온 작품",
        "이 작품을 주목", "만화 베스트", "와 비슷한", "웹툰/만화 키워드 검색",
        "이벤트 더 보기", "이벤트", "3분기 애니 원작 총집합!", "만화를 특가 세트로!",
        "앞권 무료로 맛보기!", "지금, 리디에서만 볼 수 있는 만화", "NEW | 7월의 주목 신작!",
        "2026 상반기 베스트 만화는?", "인생에 스포츠 만화는 필수입니다.",
        "그날 인류는 떠올렸다.", "만화는 리디! 제대로 즐기는 법", "별점 5점만점 명예의 전당",
        "역대 만화 대상 수상작 모아보기", "님의 취향 저격 AI 추천", "리디(주)",
        "BL 키워드 검색", "BL만화 실시간 랭킹", "BL만화 베스트", "BL만화 e북 이벤트",
        "지금, 리디에서만 볼 수 있는 BL만화", "BL만화 e북 신간",
    ]

    IOS_EXTRA_END_MARKERS = []

    def _ios_end_markers(self, section_name: str, screen_text: str) -> set:
       
        marks = set(self.IOS_SECTION_END_MARKERS) | set(self.IOS_EXTRA_END_MARKERS)
        for key in self.SECTION_LOCATOR:
            marks.add(self.IOS_SECTION_BLOB_ANCHOR.get(key, key))

        marks.discard(section_name)
        marks.discard(screen_text)
        return {m for m in marks if m and m not in screen_text}

    IOS_SECTION_BLOB_ANCHOR = {}

    def _get_ios_section_content(self, section_name: str) -> str:
        try:
            attr = self.SECTION_LOCATOR[section_name]
            found = self.find_elements(self._loc(attr))
            blob = found[0].get_attribute("name") if found else ""
            blob = blob or ""
            if not blob:
                return ""
            
            screen_text = self.IOS_SECTION_BLOB_ANCHOR.get(section_name, section_name)
            anchor = f"{screen_text} 더보기" if section_name in self.IOS_SECTION_MORE_COORD_RATIO else screen_text
            idx = blob.find(anchor)
            if idx == -1 and anchor != screen_text:
                idx = blob.find(screen_text)
                if idx != -1:
                    anchor = screen_text
                    self.log.info(
                        f"[_get_ios_section_content] {section_name} '더보기' 앵커 미발견 - "
                        f"섹션명 단독 앵커로 대체"
                    )
            if idx == -1:
                self.log.warning(
                    f"[_get_ios_section_content] {section_name} 앵커를 블롭에서 찾지 못함 "
                    f"(블롭 {len(blob)}자, 앞부분: {blob[:80]!r})"
                )
                return ""
            after = blob[idx + len(anchor):]
            end = len(after)
            for marker in self._ios_end_markers(section_name, screen_text):
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
      
        target = self.IOS_SECTION_SWIPE_COUNT.get(section_name, 0)
        state = ComicGenrePage._ios_scroll_state
        size = self.driver.get_window_size()
        x = int(size["width"] * 0.5)
        h = size["height"]

        need_reset = state is None or state[0] != subtab_name or target < state[1]
        if need_reset:
            reason = ("기억된 위치 없음(첫 호출 또는 서브탭 전환/복귀로 무효화됨)" if state is None
                      else f"서브탭 변경({state[0]} -> {subtab_name})" if state[0] != subtab_name
                      else f"역행(목표 {target}회 < 현재 {state[1]}회)")
            self.log.info(
                f"[iOS섹션스크롤] {section_name} | 전체리셋 (사유: {reason}) | "
                f"서브탭={subtab_name} 목표스와이프={target}회"
            )
        else:
            self.log.info(
                f"[iOS섹션스크롤] {section_name} | 증분 이어서 | 서브탭={subtab_name} "
                f"현재={state[1]}회 -> 목표={target}회 (추가 {target - state[1]}회)"
            )

        if need_reset:
            self.driver.terminate_app(BUNDLE_ID_IOS)
            time.sleep(1)
            self._enter_own_genrehome()
            time.sleep(2.5)
            self.click_subtab(subtab_name, log=False)
            time.sleep(2)

            # 배너/퀵메뉴 캐러셀 영역을 벗어나는 첫 스와이프 (배너 아래 지점에서 시작)
            self.driver.swipe(x, int(h * 0.746), x, int(h * 0.533), 600)
            time.sleep(1.3)

            if section_name == "방금 본 작품과 비슷한":
           
                time.sleep(4)
            done = 0
        else:
            done = state[1]

        for _ in range(target - done):
            self.driver.swipe(x, int(h * 0.829), x, int(h * 0.592), 600)
            time.sleep(1.3)

        ComicGenrePage._ios_scroll_state = (subtab_name, target)

        wait_t0 = time.time()
        loaded = self._wait_ios_section_loaded(section_name, timeout=30.0)
        wait_sec = time.time() - wait_t0
        if loaded:
          
            if self.IOS_LOG_SECTION_CONTENT_PREVIEW:
                try:
                    preview = (self._get_ios_section_content(section_name) or "")[:60].replace("\n", " ")
                except Exception as e:
                    preview = f"(추출실패: {type(e).__name__})"
                self.log.info(f"[iOS섹션스크롤] {section_name} 콘텐츠 확인 ✅ | 읽은 내용: {preview!r}")
            else:
                self.log.info(f"[iOS섹션스크롤] {section_name} 콘텐츠 확인 ✅")
        else:
            self.log.warning(
             
                f"[iOS섹션스크롤] {section_name} 콘텐츠 확인 ❌ ({wait_sec:.0f}초 대기) | "
                f"스와이프 {target}회 지점 - 섹션 위치는 도달했으나 그 자리의 텍스트(블롭)를 "
                f"읽지 못함. 스크롤 위치 어긋남 / 섹션 미노출 / 로딩지연 중 하나"
            )
        return loaded

    def _wait_ios_section_loaded(self, section_name: str, timeout: float = 10.0, interval: float = 1.0,
                                  min_attempts: int = 3, max_attempts: int = 30) -> bool:
        
        attr = self.SECTION_LOCATOR.get(section_name)
        if not attr:
            return True

        def content_ok() -> bool:
            return bool(self._get_ios_section_content(section_name))

        start = time.time()
        attempts = 0
        while True:
            attempts += 1
            try:
                if content_ok():
                    if attempts > 1:
                        self.log.info(
                            f"[_wait_ios_section_loaded] {section_name} {attempts}회째 조회에서 "
                            f"콘텐츠 확인 - 직전까지 로딩 중이었던 것으로 보임"
                        )
                    return True
            except Exception:
                pass
            if attempts >= min_attempts and time.time() - start >= timeout:
                break
            if attempts >= max_attempts:
                break
            time.sleep(interval)
        self.log.warning(
            f"[_wait_ios_section_loaded] {section_name} 콘텐츠 로딩 대기 실패"
            f"(조회 {attempts}회 / {time.time() - start:.0f}초) - 스켈레톤 상태이거나 "
            f"스크롤 위치가 어긋난 경우"
        )
        return False

    def scroll_to_section(self, section_name: str, max_scroll: int = 12, safe_margin_ratio: float = 0.45,
                           subtab_name: str = None) -> bool:
      
        if self.platform == "ios" and section_name in self.IOS_SECTION_SWIPE_COUNT:
            resolved_subtab = subtab_name or self.IOS_SECTION_SUBTAB.get(section_name, "추천")
            if self._ios_scroll_to_section_deterministic(section_name, resolved_subtab):
                return True
      
            self.log.warning(
                f"[scroll_to_section] {section_name} 증분 스크롤 위치가 실제 화면과 어긋난 것으로 "
                f"판단(섹션 콘텐츠 확인 실패) - 최상단 리셋 후 재시도"
            )
            ComicGenrePage._ios_scroll_state = None
            return self._ios_scroll_to_section_deterministic(section_name, resolved_subtab)

        attr = self.SECTION_LOCATOR[section_name]
        locator = self._loc(attr)

        found = False
        for _ in range(max_scroll):
            if self.is_present(locator, timeout=2):
                found = True
                break
            self._section_search_scroll_up()
        if not found:
            found = self.is_present(locator, timeout=2)

        if not found:
            
            for _ in range(max_scroll):
                self._section_search_scroll_down()
                if self.is_present(locator, timeout=2):
                    found = True
                    break

        if not found:
            return False

        if self.platform == "ios":
        
            self._small_nudge_up()
            if not self.is_present(locator, timeout=2):
                self._small_nudge_down_ios()
            return True

        h = self.driver.get_window_size()["height"]
        for _ in range(3):
            rect = self._section_title_rect(section_name)
            if rect["bottom"] < h * safe_margin_ratio:
                break
            self._small_nudge_up()
            if not self.is_present(locator, timeout=2):
                break
        return True

    def is_section_title_present(self, section_name: str) -> bool:
      
        try:
            self._section_title_rect(section_name)
            return True
        except Exception:
            return False

    def _section_item_row_y(self, section_name: str):
      
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
       
        w = self.driver.get_window_size()["width"]
        y = self._section_item_row_y(section_name) or (self._section_title_rect(section_name)["bottom"] + 100)
        y = self._guard_swipe_row_y(section_name, y)
        start, end = (0.90, 0.10) if wide else (0.80, 0.20)
        self.driver.swipe(int(w * start), y, int(w * end), y, 500)
        time.sleep(0.5)

    def swipe_section_right(self, section_name: str, wide: bool = False):
        w = self.driver.get_window_size()["width"]
        y = self._section_item_row_y(section_name) or (self._section_title_rect(section_name)["bottom"] + 100)
        y = self._guard_swipe_row_y(section_name, y)
        start, end = (0.10, 0.90) if wide else (0.20, 0.80)
        self.driver.swipe(int(w * start), y, int(w * end), y, 500)
        time.sleep(0.5)

    def _guard_swipe_row_y(self, section_name: str, y: int) -> int:
        
        if self.platform != "aos":
            return y
        h = self.driver.get_window_size()["height"]
        floor_y   = int(h * (self.AOS_STICKY_HEADER_BOTTOM_RATIO + 0.05))
        ceiling_y = int(h * 0.85)   # 하단 글로벌 탭바(내 서재/검색/홈/알림/MY) 회피

        def title_bottom():
            try:
                return self._section_title_rect(section_name)["bottom"]
            except Exception:
                return None

        tb = title_bottom()
        for attempt in range(2):
            if tb is not None and tb >= floor_y:
                break
            self.log.warning(
                f"[좌우스와이프가드] {section_name} 타이틀이 상단 고정영역(하한 {floor_y}) "
                f"침범/이탈 (타이틀하단={tb}) - 아래로 스크롤해 확보 {attempt + 1}/2"
            )
            self._section_search_scroll_down()
            tb = title_bottom()

        safe_y = y
        if tb is not None:
            recalc = None
            if safe_y <= tb:
                try:
                    recalc = self._section_item_row_y(section_name)
                except Exception:
                    recalc = None
            safe_y = max(safe_y, recalc or 0, tb + 100)
        safe_y = min(max(safe_y, floor_y), ceiling_y)

        if safe_y != y:
            self.log.info(
                f"[좌우스와이프가드] {section_name} 스와이프 y {y} -> {safe_y} 보정 "
                f"(타이틀하단={tb}, 고정영역하한={floor_y})"
            )
        return safe_y

    
    IOS_NO_RESET_AFTER_SWIPE = set()

    def _invalidate_ios_scroll_state_after_swipe(self, section_name: str):
        
        if self.platform != "ios":
            return
        if section_name in self.IOS_NO_RESET_AFTER_SWIPE:
            self.log.info(
                f"[iOS스크롤상태] {section_name} 재진입 불필요 섹션 - 스크롤 상태를 유지하고 "
                f"바로 더보기를 탭한다"
            )
            return
        ComicGenrePage._ios_scroll_state = None
        self.log.info(
            f"[iOS스크롤상태] {section_name} 좌우스와이프 수행으로 스크롤 상태 무효화 "
            f"- 더보기 탭 직전 재보정이 전체리셋(재진입)으로 아이템/좌표를 복원한다"
        )

    def get_section_item_names(self, section_name: str) -> list:
        if self.platform == "ios":
            content = self._get_ios_section_content(section_name)
            if section_name in self.IOS_SWIPE_RANKED_SECTIONS:
                return self._split_ios_ranked_items(content)
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

    IOS_SWIPE_RANKED_SECTIONS = {"지금 많이 읽고 있는 만화"}
    IOS_SECTION_NO_CARD_SPLIT = {"구매이력 기반 AI 추천"}

    def collect_section_items_by_swipe(self, section_name: str, max_swipes: int = 6, wide: bool = False):
    
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
            self._invalidate_ios_scroll_state_after_swipe(section_name)
            return ordered, swipe_count

        if self.platform == "ios":
            seen, ordered = set(), []
            last_content = ""

            def add_new_content(content):
                nonlocal last_content
                if not content or content == last_content:
                    return
                delta = content[len(last_content):].strip() if content.startswith(last_content) else content
                last_content = content
                for item in self._split_ios_card_items(section_name, delta):
                    if "도구 막대" in item:
                        continue
                    if item not in seen:
                        seen.add(item)
                        ordered.append(item)

            add_new_content(self._get_ios_section_content(section_name))

            swipe_count = 5
            for _ in range(swipe_count):
                self.swipe_section_left(section_name, wide=wide)
                if self.IOS_COLLECT_QUERY_EVERY_SWIPE:
                    add_new_content(self._get_ios_section_content(section_name))
            if not self.IOS_COLLECT_QUERY_EVERY_SWIPE:
                add_new_content(self._get_ios_section_content(section_name))
            self._invalidate_ios_scroll_state_after_swipe(section_name)
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

    def click_section_more(self, section_name: str, more_y_nudge: float = 0.0) -> bool:
      
        if self.platform == "ios":
           
            if section_name in self.IOS_SECTION_SWIPE_COUNT:
                subtab_name = self.IOS_SECTION_SUBTAB.get(section_name, "추천")
                
                if not self._ios_scroll_to_section_deterministic(section_name, subtab_name):
                    self.log.warning(f"[섹션더보기클릭] {section_name} 콘텐츠 로딩 미확인 - 탭 보류")
                    return False
            ratio = self.IOS_SECTION_MORE_COORD_RATIO[section_name]
            size = self.driver.get_window_size()
            y_ratio = ratio[1] + more_y_nudge
           
            if self.IOS_MORE_OCR_CORRECTION:
                measured = self._ios_locate_more_row(section_name, ratio[1])
                if measured is not None:
                    self.log.info(
                        f"[섹션더보기클릭] {section_name} OCR y보정 "
                        f"{ratio[1]:.3f} -> {measured / size['height']:.3f}"
                    )
                    y_ratio = measured / size["height"] + more_y_nudge
            self.tap_coordinate(int(size["width"] * ratio[0]), int(size["height"] * y_ratio))
            nudge_note = f" y보정 {more_y_nudge:+.3f} -> {y_ratio:.3f}" if more_y_nudge else ""
            self.log.info(f"[섹션더보기클릭] {section_name} (iOS 좌표 기반){nudge_note}")
            return True
       
        self._scroll_until_above_ratio(section_name)

     
        elem = (self._find_more_button_element(section_name)
                if section_name in self.AOS_MORE_CLICK_BY_ELEMENT else None)
        if elem is not None:
            
            prev_rect = None
            for _ in range(5):
                try:
                    cur_rect = elem.rect
                except Exception:
                    break
                if cur_rect == prev_rect:
                    break
                prev_rect = cur_rect
                time.sleep(0.5)
                refreshed = self._find_more_button_element(section_name)
                if refreshed is not None:
                    elem = refreshed
            try:
                elem.click()
                self.log.info(f"[섹션더보기클릭] {section_name} (요소 클릭)")
                return True
            except Exception as e:
                self.log.warning(
                    f"[섹션더보기클릭] {section_name} 요소 클릭 실패 - 좌표 방식으로 폴백: {e}"
                )

        coord = self._find_more_button_coordinate(section_name)
       
        for _ in range(5):
            time.sleep(0.5)
            new_coord = self._find_more_button_coordinate(section_name)
            if new_coord == coord:
                break
            self.log.warning(f"[click_section_more] {section_name} 좌표 불안정 감지: {coord} -> {new_coord}")
            coord = new_coord
        self.tap_coordinate(*coord)
        self.log.info(f"[섹션더보기클릭] {section_name}")
        return True

   
    AOS_STICKY_HEADER_BOTTOM_RATIO = 0.20

    def _scroll_until_above_ratio(self, section_name: str, safe_ratio: float = 0.40,
                                   min_ratio: float = None, max_scroll: int = 2):
    
        if min_ratio is None:
            min_ratio = self.AOS_STICKY_HEADER_BOTTOM_RATIO
        h = self.driver.get_window_size()["height"]
        for _ in range(max_scroll):
            try:
                rect = self._section_title_rect(section_name)
            except Exception:
                return
            if rect["top"] <= h * safe_ratio:
                return
            self._small_nudge_up()
            try:
                rect = self._section_title_rect(section_name)
            except Exception:
                return
            if rect["top"] < h * min_ratio:
                self.log.warning(
                    f"[_scroll_until_above_ratio] {section_name} 타이틀이 상단 고정 헤더 구간"
                    f"(<{min_ratio:.0%})까지 올라가 더보기가 가려질 수 있어 한 칸 되돌림 "
                    f"(top={rect['top']}, 화면높이={h})"
                )
                self._small_nudge_down_ios()
                return

    AOS_MORE_CLICK_BY_ELEMENT = {"지금리디에서만볼수있는 웹툰"}

    def _find_more_button_element(self, section_name: str):
        
        try:
            rect = self._section_title_rect(section_name)
            title_center = (rect["top"] + rect["bottom"]) / 2
            elems = self.find_elements(
                (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("더보기")')
            )
            cands = []
            for e in elems:
                r = e.rect
                y1, y2 = r["y"], r["y"] + r["height"]
                if y1 < rect["bottom"] and y2 > rect["top"]:
                    cands.append((abs((y1 + y2) / 2 - title_center), y1, e))
            if not cands:
                return None
            if len(cands) > 1:
                self.log.info(
                    f"[_find_more_button_element] {section_name} 같은 선상 더보기 {len(cands)}개 "
                    f"- 타이틀 중심에 가장 가까운 것 선택 (타이틀 rect={rect})"
                )
            return min(cands, key=lambda c: c[0])[2]
        except Exception as e:
            self.log.warning(f"[_find_more_button_element] {section_name} 요소 조회 실패: {e}")
            return None

    def _find_more_button_coordinate(self, section_name: str) -> tuple:
        rect = self._section_title_rect(section_name)
        title_center = (rect["top"] + rect["bottom"]) / 2
        candidates = [
            (y1, x1, y2, x2) for y1, x1, y2, x2, text in self._iter_text_elements()
            if text == "더보기" and y1 < rect["bottom"] and y2 > rect["top"]
        ]
        if not candidates:
            raise RuntimeError(f"[click_section_more] {section_name} 더보기 버튼 위치를 찾지 못함")
        if len(candidates) > 1:
            
            self.log.warning(
                f"[_find_more_button_coordinate] {section_name} 더보기 후보 {len(candidates)}개 발견: "
                f"{candidates} (타이틀 rect={rect})"
            )
        y1, x1, y2, x2 = min(candidates, key=lambda c: abs((c[0] + c[2]) / 2 - title_center))
       
        return (x1 + x2) // 2, (y1 + y2) // 2

    def click_section_more_and_verify(self, section_name: str, max_attempts: int = 3) -> tuple:
        
        hint = self.IOS_SECTION_MORE_DEST_HINT.get(section_name)
        if not hint:
            
            self.log.warning(
                f"[{section_name}] ⚠️ 더보기 목적지 미검증 - IOS_SECTION_MORE_DEST_HINT에 "
                f"기대 타이틀이 등록되지 않아 어떤 화면으로 이동했는지 확인하지 않고 통과 처리됨"
            )
        dest_title = ""
        for attempt in range(max_attempts if hint else 1):
            
            nudge = (0.0, +0.006, -0.006)[attempt] if self.platform == "ios" and attempt < 3 else 0.0
            if not self.click_section_more(section_name, more_y_nudge=nudge):
             
                continue
            time.sleep(5)
            dest_title = self._read_dest_title_with_poll(section_name)
            if not hint or hint in dest_title:
                return dest_title, True
           
            if self.platform == "aos" and hint and self._is_dest_hint_present_on_top(hint):
                return hint, True
            if hint:
                
                ocr_text = self._get_ocr_top_title()
                hint_kor = self._korean_only(hint)
                if ocr_text and hint_kor and hint_kor in self._korean_only(ocr_text):
                    self.log.info(f"[{section_name}] 요소 기반 타이틀 추출 실패 - OCR로 '{hint}' 확인됨(실제 텍스트: '{ocr_text}')")
                    return ocr_text, True
            if self._looks_like_genrehome_top_blob(dest_title):
                self.log.warning(
                    f"[{section_name}] 더보기 화면전환 없음(시도 {attempt + 1}/{max_attempts}) "
                    f"- 장르홈에 그대로 머묾(탭이 빗나갔거나 더보기가 화면 밖). "
                    f"기대 힌트:'{hint}' - 재시도"
                )
            else:
                self.log.warning(
                    f"[{section_name}] 더보기 목적지 불일치(시도 {attempt + 1}/{max_attempts}) "
                    f"기대 힌트:'{hint}' 실제타이틀:'{dest_title}' - 장르홈 복귀 후 재시도"
                )
            self.navigate_back_to_genrehome()
            time.sleep(1)
        if self._looks_like_genrehome_top_blob(dest_title):
            return "", False
        return dest_title, False


    GENREHOME_TOP_BLOB_TOKENS = ("만화", "웹툰", "웹소설", "도서", "셀렉트")

    def _looks_like_genrehome_top_blob(self, text: str) -> bool:
        """읽어온 '목적지 타이틀'이 실은 장르홈 상단 블롭인지 판별한다(= 화면 전환이 없었음)."""
        if not text or len(text) < 20:
            return False
        return sum(t in text for t in self.GENREHOME_TOP_BLOB_TOKENS) >= 4
    IOS_MORE_OCR_CORRECTION = False
    IOS_MORE_OCR_MAX_SHIFT = 0.35
    IOS_MORE_ROW_SAFE_MIN = 0.22
    IOS_MORE_ROW_SAFE_MAX = 0.72
    IOS_MORE_ROW_RESCAN_MAX = 2

    def _ios_scroll_back_small(self):
        size = self.driver.get_window_size()
        x = int(size["width"] * 0.5)
        h = size["height"]
        self.driver.swipe(x, int(h * 0.45), x, int(h * 0.58), 600)
        time.sleep(1.0)
        ComicGenrePage._ios_scroll_state = None

    def _ios_locate_more_row(self, section_name: str, fallback_ratio: float):
        h = self.driver.get_window_size()["height"]
        lo, hi = h * self.IOS_MORE_ROW_SAFE_MIN, h * self.IOS_MORE_ROW_SAFE_MAX
        rescanned = False
        for attempt in range(self.IOS_MORE_ROW_RESCAN_MAX + 1):
            y = self._ios_title_row_y_from_screen(section_name, fallback_ratio)
            if y is not None and lo <= y <= hi:
                if attempt:
                    self.log.info(f"[더보기y보정] {section_name} 되돌림 {attempt}회 후 확정 y={y:.1f}")
                return y
            if attempt == self.IOS_MORE_ROW_RESCAN_MAX:
                break
            why = "화면에서 못 찾음" if y is None else f"안전구간 밖(y={y:.1f})"
            self.log.info(
                f"[더보기y보정] {section_name} {why} - 위로 되돌려 재탐색"
                f" ({attempt + 1}/{self.IOS_MORE_ROW_RESCAN_MAX})"
            )
            self._ios_scroll_back_small()
            rescanned = True
        if rescanned and section_name in self.IOS_SECTION_SWIPE_COUNT:
            self.log.info(f"[더보기y보정] {section_name} 되돌림 취소 - 기준 위치 복구 후 등록 좌표 사용")
            ComicGenrePage._ios_scroll_state = None
            self._ios_scroll_to_section_deterministic(
                section_name, self.IOS_SECTION_SUBTAB.get(section_name, "추천")
            )
        else:
            self.log.warning(f"[더보기y보정] {section_name} 확정 실패 - 등록 좌표 사용")
        return None

    IOS_MORE_BAND_X    = (0.83, 0.99)      # 더보기 탐색 x 범위(화면 우측)
    IOS_TITLE_BAND_X   = (0.03, 0.45)      # 섹션 타이틀 탐색 x 범위(화면 좌측)
    IOS_MORE_BAND_TH   = (6, 15)           # 더보기 텍스트 띠 두께 허용범위(논리 px)
    IOS_TITLE_BAND_TH  = (9, 26)           # 타이틀 텍스트 띠 두께 허용범위(논리 px)

    IOS_MORE_BAND_X_CENTER = 356.0
    IOS_MORE_BAND_X_TOL    = 6.0
    IOS_MORE_XSCAN_X       = (0.55, 1.00)

    IOS_TITLE_CROP_PAD   = 14     # 더보기 띠 위아래 여유(논리 px)
    IOS_TITLE_CROP_X_MAX = 0.75   # 크롭 우측 한계(화면비율). 타이틀에 계정ID 접두사가 붙어
                                  # 논리 x 253까지 뻗는 경우가 있어(0.55=214로는 잘림) 넉넉히 둔다.
   
    IOS_MORE_CLUSTER_GAP = 15

    def _ios_title_row_y_from_screen(self, section_name: str, fallback_ratio: float):
      
        try:
            from PIL import Image
            import io
            screen_text = self.IOS_SECTION_BLOB_ANCHOR.get(section_name, section_name)
            png_bytes = self.driver.get_screenshot_as_png()
            img_rgb = Image.open(io.BytesIO(png_bytes))
            img = img_rgb.convert("L")
            wp, hp = img.size
            h = self.driver.get_window_size()["height"]
            sy = h / hp
            px = img.load()

            def bands(x_lo, x_hi, thresh, min_hits):
                hits, out = [], []
                for y in range(int(hp * 0.12), int(hp * 0.88)):
                    c = sum(1 for x in range(int(wp * x_lo), int(wp * x_hi), 2)
                            if px[x, y] < thresh)
                    if c >= min_hits:
                        hits.append(y)
                for y in hits:
                    if out and y - out[-1][1] <= 3:
                        out[-1][1] = y
                    else:
                        out.append([y, y])
                return [(a * sy, b * sy) for a, b in out]

            more_bands = bands(*self.IOS_MORE_BAND_X, 170, 6)
            title_bands = bands(*self.IOS_TITLE_BAND_X, 110, 10)

            w_logical = self.driver.get_window_size()["width"]

            def band_x_center(ma, mb):
                
                ya, yb = int(ma / sy), int(mb / sy)
                step = 2
                x_from = int(wp * self.IOS_MORE_XSCAN_X[0])
                x_to = int(wp * self.IOS_MORE_XSCAN_X[1]) - 1
                dark = sorted({x for y in range(ya, yb + 1)
                               for x in range(x_from, x_to, step)
                               if px[x, y] < 170})
                if not dark:
                    return None
                gap_px = self.IOS_MORE_CLUSTER_GAP / (w_logical / wp)   # 논리 → 이미지 px
                clusters, cur = [], [dark[0], dark[0]]
                for x in dark[1:]:
                    if x - cur[1] <= gap_px:
                        cur[1] = x
                    else:
                        clusters.append(tuple(cur))
                        cur = [x, x]
                clusters.append(tuple(cur))
                # 덩어리 중 x중심이 더보기 위치에 맞는 것을 고른다.
                for a, b in clusters:
                    c = (a + b) / 2 * (w_logical / wp)
                    if abs(c - self.IOS_MORE_BAND_X_CENTER) <= self.IOS_MORE_BAND_X_TOL:
                        return c
                return None

            def title_text_at(ma, mb):
               
                import pytesseract
                pad = self.IOS_TITLE_CROP_PAD / sy
                top = max(0, int(ma / sy) - pad)
                bot = min(hp, int(mb / sy) + pad)
                crop = img_rgb.crop((0, int(top), int(wp * self.IOS_TITLE_CROP_X_MAX), int(bot)))
                txt = pytesseract.image_to_string(crop, lang="kor+eng", config="--psm 7")
                return re.sub(r'[^가-힣]', '', txt)

            want_parts = [p for p in re.findall(r'[가-힣]+', screen_text) if p]

            best = None
            for ma, mb in more_bands:
                if not (self.IOS_MORE_BAND_TH[0] <= mb - ma <= self.IOS_MORE_BAND_TH[1]):
                    continue
                cx = band_x_center(ma, mb)
                if cx is None or abs(cx - self.IOS_MORE_BAND_X_CENTER) > self.IOS_MORE_BAND_X_TOL:
                    continue
                mc = (ma + mb) / 2
                paired = any(
                    abs((ta + tb) / 2 - mc) <= 12
                    and self.IOS_TITLE_BAND_TH[0] <= tb - ta <= self.IOS_TITLE_BAND_TH[1]
                    for ta, tb in title_bands
                )
                if not paired:
                    continue
                shift = abs(mc / h - fallback_ratio)
                tkor = title_text_at(ma, mb)
                matched = bool(want_parts) and all(p in tkor for p in want_parts)
                if matched:
                    self.log.info(
                        f"[더보기y보정] {section_name} 섹션명 일치 확인 - y={mc:.1f} 채택"
                        f"(크롭 OCR: {tkor[:24]!r})"
                    )
                    return mc
                if shift > self.IOS_MORE_OCR_MAX_SHIFT:
                    self.log.info(
                        f"[더보기y보정] {section_name} 후보 y={mc:.1f}는 등록값에서 "
                        f"{shift:.3f} 벗어나 무시(허용 {self.IOS_MORE_OCR_MAX_SHIFT}) "
                        f"/ 크롭 OCR: {tkor[:24]!r}"
                    )
                    continue
                if best is None or shift < best[1]:
                    best = (mc, shift, tkor)
            if best:
                self.log.info(
                    f"[더보기y보정] {section_name} 후보 y={best[0]:.1f}는 다른 섹션의 더보기 "
                    f"(크롭 OCR: {best[2][:24]!r}) - 채택하지 않음"
                )
            return None
        except Exception as e:
            self.log.warning(f"[더보기y보정] {section_name} 픽셀 스캔 실패(등록 좌표 사용): {e}")
            return None

    def _is_text_visible_on_screen(self, expected_text: str, top_ratio: float = 0.12, from_bottom: bool = False) -> bool:
        
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

        if self.platform == "ios":
            locator = (AppiumBy.ACCESSIBILITY_ID, expected_text)
        else:
            locator = (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{expected_text}")')
        return self.is_element_present(locator, timeout=5)

    def get_visible_content_item_names(self, top_margin_ratio: float = 0.15) -> list:
       
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
              
                names.extend(self._split_multi_card_text(text))
            else:
                names.append(text)
        return names

    def _split_multi_card_text(self, text: str) -> list:
        
        import re
        if not text:
            return []
        bounds = [0] + [m.end() for m in re.finditer(r'\(\d[\d,]*\)', text)]
        if bounds[-1] != len(text):
            bounds.append(len(text))
        items = [text[bounds[i]:bounds[i + 1]].strip() for i in range(len(bounds) - 1)]
        return [i for i in items if i] or [text]

    def _ios_destination_scroll_down(self):
       
        size = self.driver.get_window_size()
        x = int(size["width"] * 0.5)
        self.driver.swipe(x, int(size["height"] * 0.80), x, int(size["height"] * 0.35), 800)
        time.sleep(1)

    def collect_items_by_vertical_scroll(self, max_scrolls: int = 6, force_full_scroll: bool = False) -> list:
     
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

    IOS_FOOTER_OCR_BOTTOM_RATIO = 0.30

    def scroll_to_footer_and_get_last_item(self, section_name: str, max_scroll: int = 60) -> tuple:
       
        footer_locator = self._loc("FOOTER")
        footer_reached = False

        if self.platform == "ios":
            for _ in range(max_scroll):
                if self._is_text_visible_on_screen(
                        "리디(주)", top_ratio=self.IOS_FOOTER_OCR_BOTTOM_RATIO, from_bottom=True):
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

  
    CATEGORY_BUTTON_COORD_RATIO = {
        "ios": (0.928, 0.143),
        "aos": (0.927, 0.1286),
    }

    def is_category_page_displayed(self) -> bool:
        return self.is_present(self._loc("CATEGORY_TITLE"), timeout=5)

    def _dismiss_ios_system_alert(self) -> bool:
        """iOS 알림/ATT 권한 시스템 팝업 허용 처리. 구현은 BasePage.dismiss_ios_system_alert로
        옮겨 로그인 등 장르홈 밖 화면에서도 재사용하게 했고(2026-07-29), 이 메서드는 기존
        호출부(장르홈 진입/카테고리 탭)와의 호환을 위해 위임만 한다."""
        return self.dismiss_ios_system_alert()

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
        """카테고리 화면에서 상위메뉴 토글을 펼쳐 하위메뉴 목록을 노출"""
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
        """expand_category_topmenu로 펼친 상위메뉴 토글을 다시 접는다(동일 토글 버튼 재탭)"""
        attr = self.CATEGORY_TOPMENU_LOCATOR[topmenu_name]
        locator = self._loc(attr)
        self._scroll_category_item_into_view(locator, direction="up")
        self.click(locator)
        time.sleep(1)
        self.log.info(f"[카테고리] 상위메뉴 접음: {topmenu_name}")

    def _category_item_locator(self, name: str) -> tuple:
        if self.platform == "ios":
            return (AppiumBy.ACCESSIBILITY_ID, name)
        return (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{name}")')

    def tap_category_submenu(self, submenu_name: str):
        
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
       
        h = self.driver.get_window_size()["height"]
        for _ in range(max_scroll):
            elements = self.find_elements(locator)
            if any(e.location["y"] >= h * 0.1 for e in elements):
                return True
            self._scroll_category_page_down()
        elements = self.find_elements(locator)
        return any(e.location["y"] >= h * 0.1 for e in elements)

    def _scroll_until_safe_from_bottom(self, locator: tuple, safe_margin_ratio: float = 0.85, max_scroll: int = 5):
        h = self.driver.get_window_size()["height"]
        for _ in range(max_scroll):
            elements = [e for e in self.find_elements(locator) if e.location["y"] >= h * 0.1]
            if not elements:
                return
            el = max(elements, key=lambda e: e.location["y"])
            bottom = el.location["y"] + el.size["height"]
            if bottom <= h * safe_margin_ratio:
                return
            self._scroll_category_page_down()

    CATEGORY_DEST_ITEM_POLL_SECONDS = 15

    def is_category_dest_title_visible(self, expected_title: str, timeout: int = 8) -> bool:
    
        if self.platform == "ios":
            locator = (AppiumBy.IOS_CLASS_CHAIN, f'**/XCUIElementTypeStaticText[`name == "{expected_title}"`]')
            return self.is_element_present(locator, timeout=timeout)
        time.sleep(3)
        if expected_title in self.PERSISTENT_TAB_LABELS:
            
            locator = (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{expected_title}")')
            if self.is_present(locator, timeout=timeout) and not self.is_category_page_displayed():
                return True
            
            deadline = time.time() + self.CATEGORY_DEST_ITEM_POLL_SECONDS
            attempt = 0
            while time.time() < deadline:
                attempt += 1
                if self.get_category_dest_first_item(expected_title) != "(확인불가)":
                    if attempt > 1:
                        self.log.info(
                            f"[카테고리] {expected_title} 목적지 작품 조회 성공(시도 {attempt}회째) "
                            f"- 직전까지 로딩 중이었던 것으로 보임"
                        )
                    return True
                time.sleep(1)
            self.log.warning(
                f"[카테고리] {expected_title} 목적지 작품이 "
                f"{self.CATEGORY_DEST_ITEM_POLL_SECONDS}초 동안 조회되지 않음(시도 {attempt}회) "
                f"- 진입 실패이거나 로딩이 그보다 더 지연된 경우"
            )
            return False
        return expected_title in self.get_current_top_title()

    def navigate_back_one_screen(self):
       
        for attempt in range(5):
            if self.platform == "aos":
                self.driver.back()
            else:
                self.tap_coordinate(20, 69)
            time.sleep(1.5)
            if self.is_category_page_displayed():
                self.log.info("[카테고리] 뒤로가기 (이전 화면 복귀)")
                return
            self.log.warning(f"[카테고리] 뒤로가기 후 카테고리 화면 미확인 - 재시도({attempt + 1}/5)")
        self.log.info("[카테고리] 뒤로가기 (이전 화면 복귀)")

    def _get_ios_category_dest_content(self, submenu_name: str) -> str:
        
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

        marker = re.search(r'\d+개\s*작품\s*[^\d\s]*\s*', after)
        if marker:
            after = after[marker.end():]
        return after

    def _split_category_dest_items_aos(self, elements: list) -> list:
        
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
       
        if self.platform == "ios":
            size = self.driver.get_window_size()
            x = int(size["width"] * 0.5)
            for _ in range(2):
                self.driver.swipe(x, int(size["height"] * 0.95), x, int(size["height"] * 0.08), 500)
                time.sleep(0.3)
        else:
            for _ in range(3):
                self.driver.find_element(
                    AppiumBy.ANDROID_UIAUTOMATOR,
                    f'new UiScrollable({self.AOS_VERTICAL_SCROLLVIEW_SELECTOR}).scrollForward()'
                )
        time.sleep(1)

    def collect_category_dest_items_by_scroll(self, submenu_name: str, max_scrolls: int = 30) -> list:
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
    
    DEFAULT_AGE_GENDER_TAB = "50대 남성"

    def _age_gender_tab_locator(self, tab_name: str) -> tuple:
        
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
        return int(self.driver.get_window_size()["height"] * 0.173)

    def swipe_age_gender_tab_left(self):
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
        size = self.driver.get_window_size()
        x = int(size["width"] * 0.5)
        self.driver.swipe(x, int(size["height"] * 0.85), x, int(size["height"] * 0.28), 600)
        time.sleep(1)

    def collect_besttab_items_by_scroll(self, max_scrolls: int = 30) -> list:
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
                idx = ordered[-1].find("수직 스크롤 막대")
                if idx > 0:
                    ordered[-1] = ordered[-1][:idx].strip()
            return ordered

        return self.collect_items_by_vertical_scroll(max_scrolls=max_scrolls)

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
        size = self.driver.get_window_size()
        x = int(size["width"] * 0.5)
        self.driver.swipe(x, int(size["height"] * 0.85), x, int(size["height"] * 0.28), 600)
        time.sleep(1)

    def collect_newcontenttab_items_by_scroll(self, max_scrolls: int = 30) -> list:
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
        import re
        return re.sub(r'[^가-힣]', '', text or "")

    NO_HORIZONTAL_SWIPE_SECTIONS = {"이 작품 어때요"}

    def scroll_and_get_last_item(self, section_name: str, scroll_times: int = 3) -> str:
        for _ in range(scroll_times):
            self._section_search_scroll_up()
        time.sleep(1)

        if self.platform == "ios":
            items = self.get_section_item_names(section_name)
            return items[-1].replace("\n", " ") if items else ""

        try:
            band = list(self._iter_text_elements())
        except Exception as e:
            self.log.warning(f"[scroll_and_get_last_item] {section_name} 화면 텍스트 조회 실패: {e}")
            return ""
        if not band:
            return ""
        rows = {}
        for e in band:
            key = e[0] // 40          # 40px 단위로 같은 행 묶기
            rows.setdefault(key, []).append(e)
        for key in sorted(rows, reverse=True):
            row = sorted(rows[key], key=lambda e: e[1])   # 같은 행이면 왼쪽 칸 우선
            for item in row:
                text = item[4].replace("\n", " ").strip()
                if self._looks_like_work_title(text):
                    return text
        return ""

    @staticmethod
    def _looks_like_work_title(text: str) -> bool:
      
        import re
        if not text or len(text) < 2:
            return False
        if re.fullmatch(r'[\d.,()\s]+', text):                 # 숫자/기호만 (평점, 평가수)
            return False
        if re.fullmatch(r'\d+(\.\d+)?\s*\([\d,]+\)', text):    # "5(6,417)" 형태
            return False
        if re.fullmatch(r'\d+화무?', text):                     # "2화무" 화수 배지
            return False
        return True


class WebtoonGenrePage(ComicGenrePage):
    # 서브탭: 사용자가 확인해준 4개(추천/로맨스/BL/판타지-SF)
    SUBTAB_LOCATOR = {
        "추천":     "SUBTAB_RECOMMEND",
        "로맨스":    "SUBTAB_ROMANCE",
        "BL":      "SUBTAB_BL",
        "판타지/SF": "SUBTAB_FANTASY_SF",
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

    QUICK_MENU_EXPECTED_TITLE = {
        "이달의 신작": "웹툰 신작 캘린더",
        "이벤트":     "이벤트",
        "리디온리":   "RIDI ONLY 웹툰",
        "리다무":     "기다리면 무료",
    }

    IOS_SECTION_MORE_DEST_HINT = {
        "요일별 웹툰":  "요일별 웹툰",
        "기다리면 무료로 시작해!": "기다리면 무료로 시작해!",
        "구매이력기반 AI 추천": "구매이력 기반 AI 추천",
        "웹툰 키워드 검색": "웹툰/만화 키워드 검색",
        "웹툰 베스트":  "웹툰 베스트",
        "지금리디에서만볼수있는 웹툰": "RIDI ONLY 웹툰",
        "새로나온작품": "새로 나온 작품",
        "실시간 랭킹":         "실시간 랭킹",
        "로맨스 기다리면 무료!": "로맨스 기다리면 무료!",
        "로맨스 베스트":       "로맨스 베스트",
        "웹툰/만화 키워드 검색": "웹툰/만화 키워드 검색",
        "BL웹툰 실시간 랭킹":       "BL웹툰 실시간 랭킹",
        "BL 구매이력기반 AI 추천":   "구매이력기반 AI 추천", 
        "BL웹툰 베스트":            "BL웹툰 베스트",
        "BL키워드 검색":            "BL 키워드 검색",
        "BL 요일별 웹툰":           "BL 요일별 웹툰",
        "지금, 리디에서만 볼수있는 BL 웹툰": "RIDI ONLY BL 웹툰/만화",
        "RIDI ONLY 신작 모음":      "RIDI ONLY 신작 모음",
        "판타지 기다리면 무료!": "판타지 기다리면 무료!",
        "판타지 베스트":       "판타지 베스트",
        "RIDI ONLY 판타지":   "RIDI ONLY 판타지",
        "판타지 새로나온작품":  "새로 나온 작품",
    }

    SECTION_LOCATOR = {
        "방금 본 작품과 비슷한":     "SECTION_SIMILAR_RECENT",
        "웹툰 실시간 랭킹":         "SECTION_REALTIME_RANKING",
        "요일별 웹툰":              "SECTION_WEEKDAY_WEBTOON",
        "기다리면 무료로 시작해!":    "SECTION_WAIT_FREE",
        "오늘리디의 발견":          "SECTION_TODAY_DISCOVERY",
        "구매이력기반 AI 추천":      "SECTION_AI_PURCHASE",
        "웹툰 키워드 검색":           "SECTION_KEYWORD_SEARCH",
        "웹툰 베스트":              "SECTION_BEST",
        "지금리디에서만볼수있는 웹툰": "SECTION_RIDI_EXCLUSIVE",
        "새로나온작품":             "SECTION_NEW_ARRIVALS",
        "취향저격 AI추천 섹션":      "SECTION_AI_TASTE",
        "오늘, 리디의 발견":        "SECTION_TODAY_DISCOVERY",
        "실시간 랭킹":             "SECTION_REALTIME_RANKING",
        "로맨스 기다리면 무료!":     "SECTION_WAIT_FREE",
        "로맨스 베스트":            "SECTION_ROMANCE_BEST",
        "웹툰/만화 키워드 검색":     "SECTION_KEYWORD_SEARCH",
        "오직 리디에서만!":         "SECTION_RIDI_ONLY_EXCLAIM",
        "BL웹툰 실시간 랭킹":       "SECTION_REALTIME_RANKING",
        "BL 오늘, 리디의 발견":     "SECTION_TODAY_DISCOVERY",
        "BL 구매이력기반 AI 추천":  "SECTION_AI_PURCHASE",
        "BL웹툰 베스트":           "SECTION_BL_BEST",
        "BL키워드 검색":           "SECTION_BL_KEYWORD_SEARCH",
        "BL 요일별 웹툰":          "SECTION_WEEKDAY_WEBTOON",
        "지금, 리디에서만 볼수있는 BL 웹툰": "SECTION_RIDI_EXCLUSIVE",
        "RIDI ONLY 신작 모음":     "SECTION_RIDI_ONLY_NEW_COLLECTION",
        "이 작품 어때요":          "SECTION_HOW_ABOUT_THIS",
        "판타지 오늘, 리디의 발견": "SECTION_TODAY_DISCOVERY",
        "판타지 기다리면 무료!":    "SECTION_WAIT_FREE",
        "판타지 베스트":          "SECTION_FANTASY_BEST",
        "RIDI ONLY 판타지":      "SECTION_RIDI_ONLY_FANTASY",
        "판타지 오직 리디에서만!":  "SECTION_RIDI_ONLY_EXCLAIM",
        "이 판타지 어때요?":       "SECTION_HOW_ABOUT_FANTASY",
        "판타지 새로나온작품":     "SECTION_NEW_ARRIVALS",
    }

    IOS_SECTION_SWIPE_COUNT = {
        **ComicGenrePage.IOS_SECTION_SWIPE_COUNT,
        "요일별 웹툰":              4,
        "기다리면 무료로 시작해!":    7,
        "오늘리디의 발견":           8,
        "구매이력기반 AI 추천":      10,
        "웹툰 키워드 검색":          12,
        "웹툰 베스트":              13,
        "지금리디에서만볼수있는 웹툰": 19,
        # 22 -> 25 (2026-08-04 실기기 재측정). 22회 지점에는 미등록 섹션 "매주 화수목엔 포인트
        # 줍줍"만 보여서, 더보기 y보정이 그 섹션 타이틀을 읽고 "다른 섹션의 더보기"로 3회 전부
        # 거부한 뒤 등록 좌표를 눌러 표지를 오탭했다(목적지 타이틀 '완벽한 복수에 대하여').
        # 밴드 스캔 실측: 22회=0.436('매주..'), 24회=0.723, 26회=0.293 -> 보간하면 25회=0.508.
        # 등록 좌표 0.520과 거의 일치한다 = 좌표는 25회 기준으로 맞게 측정됐고 횟수만 틀렸다.
        # 25회가 안전구간(0.22~0.72) 중앙이라 스크롤이 ±1회 흔들려도 견딘다.
        "새로나온작품":             25,
        "취향저격 AI추천 섹션":      26,
        "오늘, 리디의 발견":        3,
        "실시간 랭킹":             5,
        "로맨스 기다리면 무료!":     8,
        "로맨스 베스트":            9,
        "웹툰/만화 키워드 검색":    13,
        "오직 리디에서만!":        15,
        "BL웹툰 실시간 랭킹":       2,
        "BL 오늘, 리디의 발견":     4,
        "BL 구매이력기반 AI 추천":  5,
        "BL웹툰 베스트":           7,
        "BL키워드 검색":           9,
        "BL 요일별 웹툰":         12,
        "지금, 리디에서만 볼수있는 BL 웹툰": 14,
        "RIDI ONLY 신작 모음":    16,
        "이 작품 어때요":         21,
        "판타지 오늘, 리디의 발견": 2,
        "판타지 기다리면 무료!":   3,
        "판타지 베스트":         5,
        "RIDI ONLY 판타지":     7,
        "판타지 오직 리디에서만!": 9,
        "이 판타지 어때요?":     11,
        "판타지 새로나온작품": 22,
    }

    IOS_SECTION_SUBTAB = {
        **ComicGenrePage.IOS_SECTION_SUBTAB,
        "요일별 웹툰":              "추천",
        "기다리면 무료로 시작해!":    "추천",
        "오늘리디의 발견":           "추천",
        "구매이력기반 AI 추천":       "추천",
        "웹툰 키워드 검색":          "추천",
        "웹툰 베스트":              "추천",
        "지금리디에서만볼수있는 웹툰": "추천",
        "새로나온작품":             "추천",
        "취향저격 AI추천 섹션":      "추천",
        "오늘, 리디의 발견":        "로맨스",
        "실시간 랭킹":             "로맨스",
        "로맨스 기다리면 무료!":     "로맨스",
        "로맨스 베스트":            "로맨스",
        "웹툰/만화 키워드 검색":     "로맨스",
        "오직 리디에서만!":         "로맨스",
        "BL웹툰 실시간 랭킹":       "BL",
        "BL 오늘, 리디의 발견":     "BL",
        "BL 구매이력기반 AI 추천":  "BL",
        "BL웹툰 베스트":           "BL",
        "BL키워드 검색":           "BL",
        "BL 요일별 웹툰":          "BL",
        "지금, 리디에서만 볼수있는 BL 웹툰": "BL",
        "RIDI ONLY 신작 모음":     "BL",
        "이 작품 어때요":          "BL",
        "판타지 오늘, 리디의 발견": "판타지/SF",
        "판타지 기다리면 무료!":   "판타지/SF",
        "판타지 베스트":         "판타지/SF",
        "RIDI ONLY 판타지":     "판타지/SF",
        "판타지 오직 리디에서만!": "판타지/SF",
        "이 판타지 어때요?":    "판타지/SF",
        "판타지 새로나온작품":  "판타지/SF",
    }

    IOS_SECTION_MORE_COORD_RATIO = {
        "요일별 웹툰":              (0.910, 0.579),
        "기다리면 무료로 시작해!":    (0.910, 0.375),
        "구매이력기반 AI 추천":       (0.910, 0.463),
        "웹툰 키워드 검색":          (0.910, 0.452),
        "웹툰 베스트":              (0.910, 0.472),
        "지금리디에서만볼수있는 웹툰": (0.910, 0.449),
        "새로나온작품":             (0.913, 0.520),
        "실시간 랭킹":             (0.913, 0.455),
        "로맨스 기다리면 무료!":     (0.913, 0.279),
        "로맨스 베스트":            (0.913, 0.458),
        "웹툰/만화 키워드 검색":     (0.913, 0.457),
        "BL웹툰 실시간 랭킹":       (0.913, 0.365),
        "BL 구매이력기반 AI 추천":  (0.915, 0.284),
        "BL웹툰 베스트":           (0.913, 0.504),
        "BL키워드 검색":           (0.913, 0.544),
        "BL 요일별 웹툰":          (0.913, 0.448),
        "지금, 리디에서만 볼수있는 BL 웹툰": (0.913, 0.461),
        "RIDI ONLY 신작 모음":     (0.913, 0.422),
        "판타지 기다리면 무료!":     (0.913, 0.494),
        "판타지 베스트":            (0.913, 0.460),
        "RIDI ONLY 판타지":        (0.913, 0.501),
        "판타지 새로나온작품":       (0.913, 0.550),
    }

    IOS_MORE_OCR_CORRECTION = True

    # 테스트 대상에서 제외된 섹션을 콘텐츠 경계로 넣는다. 구현된 섹션은 SECTION_LOCATOR 키가
    # _ios_end_markers()에서 자동으로 마커에 들어가므로 여기 적을 필요가 없고, 이 목록은
    # "구현 안 된 섹션이 검증 섹션 바로 뒤에 오는 경우"만 담는다.
    #   "최신 업데이트": BL탭 "오늘, 리디의 발견" 바로 뒤에 오는 미구현 섹션. 경계가 없어서
    #   아이템 1개에 다음 섹션 타이틀+첫 작품이 통째로 딸려붙었다(2026-08-04 test_004 실패).
    IOS_EXTRA_END_MARKERS = ["최신 업데이트"]

    def _loc(self, attr: str):
        cls = AOS_WEBTOON_GENRE if self.platform == "aos" else IOS_WEBTOON_GENRE
        return getattr(cls, attr)

    IOS_SECTION_BLOB_ANCHOR = {
        "오늘리디의 발견":           "오늘, 리디의 발견",
        "구매이력기반 AI 추천":       "구매이력 기반 AI 추천",
        "지금리디에서만볼수있는 웹툰": "지금, 리디에서만 볼 수 있는 웹툰",
        "새로나온작품":              "새로 나온 작품",
        "취향저격 AI추천 섹션":       "님의 취향 저격 AI 추천",
        "BL 오늘, 리디의 발견":            "오늘, 리디의 발견",
        "BL 요일별 웹툰":                 "요일별 웹툰",
        "BL 구매이력기반 AI 추천":          "구매이력 기반 AI 추천",
        "지금, 리디에서만 볼수있는 BL 웹툰": "지금, 리디에서만 볼 수 있는 BL웹툰",
        "판타지 오늘, 리디의 발견":         "오늘, 리디의 발견",
        "판타지 오직 리디에서만!":          "오직 리디에서만!",
        "판타지 새로나온작품":             "새로 나온 작품",
        # 코드 키에는 공백이 없지만 실제 화면 문구는 "BL 키워드 검색"(공백 있음)이라, 앵커를
        # 보정하지 않으면 블롭에서 "BL키워드 검색 더보기"를 찾다가 실패한다(2026-08-04 확인).
        "BL키워드 검색":                  "BL 키워드 검색",
        # 더보기 y보정의 크롭 OCR이 이 섹션 타이틀을 '실시간랭킹'으로만 읽는다(앞의 영문 섞인
        # "BL웹툰"을 놓친다). 앵커 없이 코드 키로 대조하면 한글 조각이 ['웹툰','실시간','랭킹']이
        # 되어 '웹툰'이 빠져 "다른 섹션의 더보기"로 거부되고, 3회 전부 표지를 오탭했다.
        # 앵커를 "실시간 랭킹"으로 주면 조각이 ['실시간','랭킹']이 되어 OCR 판독값과 일치한다.
        # 블롭 콘텐츠 추출은 그대로다 - 실측 위치 기준으로 잘라내는 시작점이 동일하다.
        #   "BL웹툰 실시간 랭킹 더보기" 위치 887 + 길이 15 = 902
        #   "실시간 랭킹 더보기"        위치 892 + 길이 10 = 902
        "BL웹툰 실시간 랭킹":              "실시간 랭킹",
    }

    def enter_genrehome(self):
        self.enter_webtoon_genrehome()

    def is_genrehome_displayed(self) -> bool:
        return self.is_webtoon_genrehome_displayed()

    def _enter_own_genrehome(self):
        self.enter_webtoon_genrehome()

    def enter_webtoon_genrehome(self):
        self.open_deeplink(DeepLinks.WEBTOON_RECOMMEND_HOME)
        self.log.info("[진입] 웹툰 장르홈 진입")

    # ---- 2026-08-04 추가: 서브탭 렌더링 지연 대응 (웹툰 전용 오버라이드) ----
    # 증상: test_006/007/008이 "더보기 화면 -> 뒤로가기 -> 장르홈 재진입" 직후에만 서브탭 요소를
    #   DEFAULT_TIMEOUT(10초) 안에 못 찾아 실패했다.
    #     13:26:26 [뒤로가기] 장르홈 복귀 시도 / 13:26:37 [진입] 웹툰 장르홈 진입
    #     13:26:50 [ERROR] 타임아웃: ('accessibility id', '로맨스 로맨스') | 10s
    # 같은 '로맨스 로맨스' 클릭이 13:07·13:09에는 정상 동작했으므로 로케이터 문제가 아니라
    # 화면전환 직후 렌더링 지연이다(웹소설에서 서브탭 표기를 단일로 바꾼 것과는 무관 -
    # 웹툰의 중복 표기는 여전히 유효하므로 로케이터를 건드리면 안 된다).
    # 공통 ComicGenrePage.click_subtab / is_present를 고치면 만화·웹소설·도서까지 전부 영향을
    # 받으므로, 웹툰 클래스에서만 오버라이드한다. AOS 경로는 기존과 동일하게 둔다.
    SUBTAB_WAIT_SEC = 25

    def is_webtoon_genrehome_displayed(self) -> bool:
        return self.is_present(self._loc("SUBTAB_RECOMMEND"), timeout=self.SUBTAB_WAIT_SEC)

    def click_subtab(self, tab_name: str, log: bool = True):
        attr = self.SUBTAB_LOCATOR[tab_name]
        locator = self._loc(attr)
        if self.platform == "ios":
            if not self.is_element_present(locator, timeout=self.SUBTAB_WAIT_SEC):
                self.log.warning(
                    f"[서브탭클릭] {tab_name} {self.SUBTAB_WAIT_SEC}초 내 미노출 - "
                    f"장르홈 재진입 후 1회 재시도"
                )
                self.enter_webtoon_genrehome()
                time.sleep(3)
                self.wait_for_element(locator, timeout=self.SUBTAB_WAIT_SEC)
            self.find_element(locator).click()
        else:
            self.click(locator)
        ComicGenrePage._ios_scroll_state = None
        if log:
            self.log.info(f"[서브탭클릭] {tab_name}")


class WebnovelGenrePage(ComicGenrePage):
    SUBTAB_LOCATOR = {
        "추천":   "SUBTAB_RECOMMEND",
        "로맨스": "SUBTAB_ROMANCE",
        "로판":   "SUBTAB_ROMANCE_FANTASY",
        "BL":    "SUBTAB_BL",
        "판타지": "SUBTAB_FANTASY",
    }

    QUICK_MENU_LOCATOR = {
        "신작":    "NEW_QUICK",
        "베스트":  "BEST_QUICK",
        "이벤트":  "EVENT_QUICK",
        "캘린더":  "CALENDAR_QUICK",
    }

    QUICK_MENU_EXPECTED_TITLE = {
        "신작":    "신작",
        "베스트":  "베스트",
        "이벤트":  "이벤트",
        "캘린더":  "캘린더",
    }

    SECTION_LOCATOR = {
        "방금 본 작품과 비슷한":  "SECTION_SIMILAR_RECENT",
        "내 취향 추천 신작":     "SECTION_MY_TASTE_NEW",
        "웹소설 실시간 랭킹":    "SECTION_REALTIME_RANKING",
        "새로 나온 작품":        "SECTION_NEW_ARRIVALS",
        "구매이력 기반 AI 추천": "SECTION_AI_PURCHASE",
        "진행중인 이벤트":       "SECTION_ONGOING_EVENT",
        "취향저격 AI추천 섹션":   "SECTION_AI_TASTE",
    }

    IOS_SECTION_MORE_DEST_HINT = {
        "내 취향 추천 신작":     "신작",
        "새로 나온 작품":        "신작",
        "구매이력 기반 AI 추천": "구매이력 기반 AI 추천",
        "진행중인 이벤트":       "이벤트",
    }

    IOS_SECTION_SWIPE_COUNT = {
        "방금 본 작품과 비슷한":  2,
        "내 취향 추천 신작":     5,
        "웹소설 실시간 랭킹":    6,
        "새로 나온 작품":        9,
        "구매이력 기반 AI 추천": 12,
        "진행중인 이벤트":      18,
        "취향저격 AI추천 섹션":  20,
    }

    IOS_SECTION_SUBTAB = {
        "내 취향 추천 신작":     "추천",
        "웹소설 실시간 랭킹":    "추천",
        "새로 나온 작품":        "추천",
        "구매이력 기반 AI 추천": "추천",
        "진행중인 이벤트":       "추천",
        "취향저격 AI추천 섹션":   "추천",
    }

    IOS_SECTION_MORE_COORD_RATIO = {
        "내 취향 추천 신작":     (0.913, 0.360),
        "새로 나온 작품":        (0.913, 0.359),
        "구매이력 기반 AI 추천": (0.913, 0.463),
        "진행중인 이벤트":       (0.913, 0.390),
    }

    IOS_SECTION_BLOB_ANCHOR = {
        "취향저격 AI추천 섹션":   "님의 취향 저격 AI 추천",
    }

    IOS_MORE_OCR_CORRECTION = True
    IOS_EXTRA_END_MARKERS = [
        "BL 현대물 베스트", "키워드로 작품 찾기", "역사/시대물 베스트",
    ]

    IOS_SECTION_ROW_Y_RATIO = {
        "방금 본 작품과 비슷한":  0.52,
        "내 취향 추천 신작":     0.60,
        "웹소설 실시간 랭킹":    0.40,
        "새로 나온 작품":        0.60,
        "구매이력 기반 AI 추천": 0.40,
        "진행중인 이벤트":       0.62,
        "취향저격 AI추천 섹션":   0.63,
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

    def enter_genrehome(self):
        self.enter_webnovel_genrehome()

    def is_genrehome_displayed(self) -> bool:
        return self.is_webnovel_genrehome_displayed()

    def _enter_own_genrehome(self):
        self.enter_webnovel_genrehome()

    def enter_webnovel_genrehome(self):
        self.open_deeplink(DeepLinks.WEBNOVEL_RECOMMEND_HOME)
        self.log.info("[진입] 웹소설 장르홈 진입")

    def is_webnovel_genrehome_displayed(self) -> bool:
        if self.platform == "ios":
            try:
                locator = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "추천"`]')
                return "추천" in (self.find_element(locator).get_attribute("name") or "")
            except Exception:
                return False
        return self.is_present(self._loc("SUBTAB_RECOMMEND"))

    def click_subtab(self, tab_name: str, log: bool = True):
        if self.platform == "ios" and tab_name == "추천":
            if log:
                self.log.info(f"[서브탭클릭] {tab_name} (iOS 웹소설: 딥링크로 이미 선택됨 - 탭 생략)")
            return
        super().click_subtab(tab_name, log=log)


class GeneralbookGenrePage(ComicGenrePage):
    SUBTAB_LOCATOR = {
        "추천": "SUBTAB_RECOMMEND",
    }

    QUICK_MENU_LOCATOR = {
        "신간":       "NEW_QUICK",
        "북스 베스트": "BEST_QUICK",
        "이벤트":     "EVENT_QUICK",
        "리디온리":    "RIDIONLY_QUICK",
    }

    QUICK_MENU_EXPECTED_TITLE = {
        "신간":       "신간",
        "북스 베스트": "베스트",
        "이벤트":     "이벤트",
        "리디온리":    "RIDI ONLY 도서",
    }

    SECTION_LOCATOR = {
        "방금 본 작품과 비슷한":            "SECTION_SIMILAR_RECENT",
        "지금 많이 읽고 있는 작품":          "SECTION_MOST_READ",
        "오늘, 리디의 발견":               "SECTION_TODAY_DISCOVERY",
        "구매이력 기반 AI 추천":            "SECTION_AI_PURCHASE",
        "이벤트":                        "SECTION_ONGOING_EVENT",
        "베스트":                        "SECTION_BEST",
        "새로 나온 작품":                  "SECTION_NEW_ARRIVALS",
        "지금, 리디에서만 볼 수 있는 도서":   "SECTION_RIDI_ONLY_BOOK",
        "취향저격 AI추천 섹션":             "SECTION_AI_TASTE",
    }

    IOS_SECTION_MORE_DEST_HINT = {
        "지금 많이 읽고 있는 작품":          "지금 많이 읽고 있는 작품",
        "구매이력 기반 AI 추천":            "구매이력 기반 AI 추천",
        "이벤트":                        "이벤트",
        "베스트":                        "베스트",
        "새로 나온 작품":                  "새로 나온 작품",
        "지금, 리디에서만 볼 수 있는 도서":   "RIDI ONLY 도서",
    }

    AOS_PERSONALIZED_SECTIONS = ComicGenrePage.AOS_PERSONALIZED_SECTIONS | {
        "지금 많이 읽고 있는 작품",
    }

    RANKED_SECTIONS = {"지금 많이 읽고 있는 작품"}
    IOS_SECTION_SWIPE_COUNT = {
        # 퀵메뉴 바로 다음에 오는 첫 섹션이다(사용자 확인 + 실측). 한때 8로 등록했는데 그건
        # 중간 기획 섹션 "<프로젝트 헤일메리>와 비슷한"의 위치였다 - 프레임 OCR needle을
        # "비슷한"으로 잡아 두 섹션을 혼동한 것이고, 8회 지점에서는 이 섹션이 화면 밖이라
        # 콘텐츠 확인이 98초씩 두 번 실패한 뒤 스킵됐다(2026-08-04).
        # 요소 rect를 스와이프마다 읽어 재측정한 결과: 최상단 y639 → 1회 492 → 2회 310(중앙)
        # → 3회 130(헤더 아래로 벗어남) → 4회부터 음수(화면 밖).
        "방금 본 작품과 비슷한":            2,
        "지금 많이 읽고 있는 작품":          2,
        "오늘, 리디의 발견":               4,
        "구매이력 기반 AI 추천":            7,
        "이벤트":                        9,
        "베스트":                       11,
        "새로 나온 작품":                 17,
        "지금, 리디에서만 볼 수 있는 도서":  22,
        "취향저격 AI추천 섹션":            24,
    }

    IOS_SECTION_SUBTAB = {k: "추천" for k in IOS_SECTION_SWIPE_COUNT}
    IOS_SECTION_MORE_COORD_RATIO = {
        "지금 많이 읽고 있는 작품":         (0.913, 0.758),
        "구매이력 기반 AI 추천":           (0.913, 0.502),
        "이벤트":                       (0.913, 0.493),
        "베스트":                       (0.913, 0.492),
        "새로 나온 작품":                 (0.913, 0.379),
        "지금, 리디에서만 볼 수 있는 도서": (0.913, 0.574),
    }

    # "방금 본 작품과 비슷한"은 등록하지 않는다. 한때 iOS 화면 문구가 "<작품명>와 비슷한"인 줄
    # 알고 앵커를 "와 비슷한"으로 넣었는데 **틀렸다**(2026-08-04 블롭 실측). 이 지면에는
    # "비슷한"이 들어간 것이 4곳 있고, 검증 대상은 퀵메뉴 바로 다음에 오는 첫 번째다:
    #   idx  662  '... 이달의 쿠폰 대여 혜택 모아봄 방금 본 작품과 비슷한 프로젝트'  ← 검증 대상
    #   idx 1156  '... 베스트 더보기 <프로젝트 헤일메리>와 비슷한 비하인드'          ← 기획 섹션
    #   idx 1543/1557  '[프로젝트 헤일메리] 비슷한'                              ← 아이템 라벨
    # 앵커를 "와 비슷한"으로 두면 idx 1156(기획 섹션)을 먼저 찾아 엉뚱한 구간을 잘라낸다.
    # 코드 키가 화면 문구와 그대로 일치하므로("방금 본 작품과 비슷한" in 블롭 = True) 매핑 불필요.
    IOS_SECTION_BLOB_ANCHOR = {
        "취향저격 AI추천 섹션":  "님의 취향 저격 AI 추천",
    }

    IOS_EXTRA_END_MARKERS = [
        "지금, 리디에서만! 선 출간 신작", "히가시노 게이고 작가 대표작",
        "짧지만 강렬한 서사, 우주라이크소설",
    ]
    IOS_MORE_OCR_CORRECTION = True

    BIG_BANNER_Y_RATIO = (0.14, 0.62)

    def get_big_banner_page_indicator(self) -> tuple:
        import re as _re
        if self.platform != "aos":
            return (None, None)
        import xml.etree.ElementTree as _ET
        try:
            h = self.driver.get_window_size()["height"]
            lo, hi = h * self.BIG_BANNER_Y_RATIO[0], h * self.BIG_BANNER_Y_RATIO[1]
            bounds_re = _re.compile(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]')
            nums = []
            for el in _ET.fromstring(self.driver.page_source).iter():
                t = (el.get("text") or "").strip()
                if not t.isdigit():
                    continue
                m = bounds_re.match(el.get("bounds", ""))
                if not m:
                    continue
                x1, y1, x2, y2 = map(int, m.groups())
                if lo < y1 < hi:
                    nums.append((x1, int(t)))
            nums.sort()
            if len(nums) >= 2:
                return (nums[0][1], nums[-1][1])
        except Exception as e:
            self.log.warning(f"[빅배너] 인디케이터 조회 실패: {e}")
        return (None, None)

    def collect_big_banner_pages_by_polling(self, target_count: int = 5,
                                            max_seconds: int = 90) -> list:
        seen, order = set(), []
        deadline = time.time() + max_seconds
        while len(order) < target_count and time.time() < deadline:
            cur, total = self.get_big_banner_page_indicator()
            if cur is not None and cur not in seen:
                seen.add(cur)
                order.append(cur)
                self.log.info(f"[빅배너] 페이지 {cur}/{total} 확인 ({len(order)}/{target_count})")
            time.sleep(1.5)
        return order

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

    def enter_genrehome(self):
        self.enter_generalbook_genrehome()

    def is_genrehome_displayed(self) -> bool:
        return self.is_generalbook_genrehome_displayed()

    def _enter_own_genrehome(self):
        # iOS 결정론적 스크롤 전체리셋 시 만화가 아니라 일반도서 장르홈으로 재진입한다.
        self.enter_generalbook_genrehome()

    def enter_generalbook_genrehome(self):
        self.open_deeplink(DeepLinks.GENERAL_RECOMMEND_HOME)
        self.log.info("[진입] 일반도서 장르홈 진입")

    def is_generalbook_genrehome_displayed(self) -> bool:
        return self.is_present(self._loc("SUBTAB_RECOMMEND"))

    def _scroll_category_page_down(self):
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

    def _scroll_category_page_up(self):
        if self.platform != "aos":
            super()._scroll_category_page_up()
            return
        size = self.driver.get_window_size()
        x = int(size["width"] * 0.9)
        start_y = int(size["height"] * 0.3)
        end_y = int(size["height"] * 0.8)
        self.driver.swipe(x, start_y, x, end_y, 600)
        self.log.info("[swipe] direction=up (도서 카테고리 전용 좌표)")
        time.sleep(0.5)

    def scroll_topmenu_to_top(self, topmenu_name: str, max_scroll: int = 10, top_ratio: float = 0.3):
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
