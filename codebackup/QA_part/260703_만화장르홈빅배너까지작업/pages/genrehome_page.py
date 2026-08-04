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

    # ── 진입 ──────────────────────────────────────────────
    def enter_comic_genrehome(self):
        self.open_deeplink(DeepLinks.COMIC_RECOMMEND_HOME)
        self.log.info("[진입] 만화 장르홈 딥링크 진입")

    def is_comic_genrehome_displayed(self) -> bool:
        return self.is_present(self._loc("SUBTAB_RECOMMEND"))

    # ── 메인 장르탭 ──────────────────────────────────────
    def click_main_tab(self):
        self.click(self._loc("MAIN_TAB"))
        self.log.info("[메인탭] 만화 탭 클릭")

    # ── 서브탭 ───────────────────────────────────────────
    def _subtab_y(self) -> int:
        # AOS XML 기준 서브탭 y≈287 / 화면높이 2372 → 약 12%
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

    def is_subtab_visible(self, tab_name: str, timeout: int = 3) -> bool:
        attr = self.SUBTAB_LOCATOR[tab_name]
        # iOS: 서브탭 요소가 accessible=true이지만 Appium이 visible=false로 마킹
        # → visibility 체크 대신 presence 체크 사용
        if self.platform == "ios":
            result = self.is_element_present(self._loc(attr), timeout=timeout)
        else:
            result = self.is_present(self._loc(attr), timeout=timeout)
        self.log.info(f"[서브탭확인] {tab_name} {'✅' if result else '❌'}")
        return result

    def click_subtab(self, tab_name: str):
        attr = self.SUBTAB_LOCATOR[tab_name]
        locator = self._loc(attr)
        # iOS: 서브탭 요소가 visible=false이므로 presence 기반으로 찾아 직접 클릭
        if self.platform == "ios":
            self.wait_for_element(locator)
            self.find_element(locator).click()
        else:
            self.click(locator)
        self.log.info(f"[서브탭클릭] {tab_name}")

    # ── 빅배너 ───────────────────────────────────────────
    def is_big_banner_displayed(self) -> bool:
        if self.platform == "ios":
            # iOS: page_source 파싱 방식으로 빠르게 확인 (API 1회 호출)
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
        """빅배너 렌더링 완료 아이템 목록 반환 (page_source 파싱, 중복 제거)"""
        if self.platform == "aos":
            # AOS: BIG_BANNER locator는 퀵메뉴 아이콘(clickable + content-desc)도 함께 매칭되므로
            # 카드 높이(화면의 25% 이상)로 실제 빅배너만 구분 (퀵메뉴는 화면 높이의 ~9%)
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

        import xml.etree.ElementTree as ET
        import html
        source = self.driver.page_source
        root = ET.fromstring(source)
        seen = set()
        items = []
        for elem in root.iter():
            y = int(elem.get("y", -1))
            h = int(elem.get("height", 0))
            w = int(elem.get("width", 0))
            name = (elem.get("name") or "").strip()
            # y=155~215, h=300~400, w=380~430 → 개별 배너 컨테이너 (전체 캐러셀 w≈9984 제외)
            if 155 <= y <= 215 and 300 <= h <= 400 and 380 <= w <= 430 and name:
                clean = html.unescape(name).replace("\n", " / ")
                if clean not in seen:
                    seen.add(clean)
                    items.append(clean)
        return items

    def swipe_big_banner_left(self, times: int = 1):
        size = self.driver.get_window_size()
        y = int(size["height"] * 0.40)
        for _ in range(times):
            self.driver.swipe(int(size["width"] * 0.80), y, int(size["width"] * 0.20), y, 600)
            time.sleep(0.8)
        self.log.info(f"[빅배너] 좌 스와이프 {times}회")

    def swipe_big_banner_right(self, times: int = 1):
        size = self.driver.get_window_size()
        y = int(size["height"] * 0.40)
        for _ in range(times):
            self.driver.swipe(int(size["width"] * 0.20), y, int(size["width"] * 0.80), y, 600)
            time.sleep(0.8)
        self.log.info(f"[빅배너] 우 스와이프 {times}회")

    def get_big_banner_total_count(self) -> int:
        """빅배너 캐러셀 총 개수 반환 (페이지 카운터 요소에서 추출)"""
        import xml.etree.ElementTree as ET
        import re
        source = self.driver.page_source
        root = ET.fromstring(source)
        if self.platform == "aos":
            # AOS: "N / M" 인디케이터가 TextView("N") + 슬래시 아이콘 + TextView("M")로 분리되어 있어
            # 하나의 텍스트로 합쳐지지 않음 → 배너 우상단(가로 70%~, 세로 0~20%) 영역의
            # 숫자 전용 TextView 2개를 x좌표 순으로 찾아 뒤쪽(M) 값을 총 개수로 사용
            bounds_pattern = re.compile(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]')
            digit_pattern = re.compile(r'^\d+$')
            banner_box = None
            for elem in root.iter():
                if elem.get("class") != "android.view.ViewGroup" or elem.get("clickable") != "true":
                    continue
                if not (elem.get("content-desc") or ""):
                    continue
                m = bounds_pattern.match(elem.get("bounds", ""))
                if not m:
                    continue
                bx1, by1, bx2, by2 = map(int, m.groups())
                screen_h = self.driver.get_window_size()["height"]
                if screen_h * 0.12 < by1 < screen_h * 0.65:
                    banner_box = (bx1, by1, bx2, by2)
                    break
            if banner_box:
                bx1, by1, bx2, by2 = banner_box
                rx1 = bx1 + 0.7 * (bx2 - bx1)
                ry2 = by1 + 0.2 * (by2 - by1)
                found = []
                for elem in root.iter():
                    if elem.get("class") != "android.widget.TextView":
                        continue
                    text = (elem.get("text") or "").strip()
                    if not digit_pattern.match(text):
                        continue
                    m = bounds_pattern.match(elem.get("bounds", ""))
                    if not m:
                        continue
                    ex1, ey1, ex2, ey2 = map(int, m.groups())
                    if ex1 >= rx1 and ey2 <= ry2:
                        found.append((ex1, int(text)))
                found.sort(key=lambda t: t[0])
                if len(found) >= 2 and found[-1][1] > 1:
                    return found[-1][1]
        else:
            # iOS: 카운터 요소 name='N M' 형태 (슬래시 없음, y≈173, h≈18 소형 요소)
            pattern = re.compile(r'^(\d+)\s+(\d+)$')
            for elem in root.iter():
                y = int(elem.get("y", -1))
                h = int(elem.get("height", 0))
                name = (elem.get("name") or "").strip()
                if 160 <= y <= 190 and 10 <= h <= 25 and name:
                    m = pattern.match(name)
                    if m:
                        total = int(m.group(2))
                        if total > 1:
                            return total
        return 0

    def get_all_subtab_names(self) -> list:
        """page_source에서 전체 서브탭 이름 추출 (x좌표 순 정렬)"""
        if self.platform == "aos":
            # AOS: bounds="[x1,y1][x2,y2]" 파싱 (iOS의 y/height/name/accessible 속성 없음)
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

    def collect_big_banner_items_by_swipe(self, max_count: int = None) -> list:
        """빅배너를 좌스와이프하며 총 개수만큼 순차적으로 아이템을 수집 (중복 제거, 순서 유지)"""
        if max_count is None:
            max_count = self.get_big_banner_total_count()
        seen = set()
        ordered_items = []
        stall = 0
        # 스와이프 직후 카드 전환 애니메이션이 늦게 정착하는 경우를 대비해
        # max_count보다 여유 있게 시도하고, stall 허용치도 넉넉히 둔다
        for _ in range(max_count + 10):
            before = len(ordered_items)
            for text in self.get_big_banner_items():
                if text not in seen:
                    seen.add(text)
                    ordered_items.append(text)
            if len(ordered_items) >= max_count:
                break
            stall = 0 if len(ordered_items) > before else stall + 1
            if stall >= 5:
                break
            self.swipe_big_banner_left(times=1)
        return ordered_items
