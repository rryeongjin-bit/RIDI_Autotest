"""[임시 진단] 도서 장르홈 빅배너 요소 구조 + '리디온리' 퀵메뉴 실제 동작 실측.

pytest 세션 안에서 돌려야 한다 - conftest가 full_reset=True로 앱을 새로 설치하고 권한/Braze
팝업까지 처리해주며, 세션이 끝나면 앱이 제거되어 외부에서 붙을 수 없기 때문이다.
확인이 끝나면 이 파일은 삭제한다(2026-08-03).
"""
import re
import time
import logging
import xml.etree.ElementTree as ET

import pytest

from pages.genrehome_page import GeneralbookGenrePage, MainhomePage
from pages.login_page import LoginPage

BR = re.compile(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]')


class TestTmpGeneralProbe:
    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver = driver
        self.platform = platform
        self.page = GeneralbookGenrePage(driver, platform)

    def test_000_준비_앱실행_로그인(self):
        assert MainhomePage(self.driver, self.platform).launch_and_verify_genrehome()
        assert LoginPage(self.driver, self.platform).login_if_needed()

    def test_001_빅배너_요소구조(self):
        self.page.enter_generalbook_genrehome()
        time.sleep(5)
        s = self.driver.get_window_size()
        W, H = s["width"], s["height"]
        logging.info(f"[진단] 화면 {W}x{H}")

        root = ET.fromstring(self.driver.page_source)
        logging.info("[진단] === 빅배너 후보 (상단 45% / 높이 150+) ===")
        for el in root.iter():
            rid = el.get("resource-id") or ""
            cls = (el.get("class") or "").split(".")[-1]
            m = BR.match(el.get("bounds", ""))
            if not m:
                continue
            x1, y1, x2, y2 = map(int, m.groups())
            if y1 > H * 0.45 or (y2 - y1) < 150:
                continue
            logging.info(f"[진단]   y={y1}~{y2} x={x1}~{x2} {cls} id={rid.split('/')[-1]!r}")

        logging.info("[진단] === 빅배너 영역 텍스트 ===")
        for el in root.iter():
            t = (el.get("text") or "").strip()
            m = BR.match(el.get("bounds", ""))
            if t and m:
                x1, y1, x2, y2 = map(int, m.groups())
                if H * 0.10 < y1 < H * 0.48:
                    logging.info(f"[진단]   y={y1} {t[:46]!r}")

    def test_002_리디온리_퀵메뉴_동작(self):
        self.page.enter_generalbook_genrehome()
        time.sleep(4)
        s = self.driver.get_window_size()
        H = s["height"]

        logging.info(f"[진단] 리디온리 노출: {self.page.is_quickmenu_visible('리디온리', log=False)}")
        self.page.click_quickmenu("리디온리")
        time.sleep(4)
        logging.info(f"[진단] 클릭후 top_title: {self.page.get_current_top_title()!r}")
        logging.info(f"[진단] 클릭후 장르홈여부: {self.page.is_generalbook_genrehome_displayed()}")

        root = ET.fromstring(self.driver.page_source)
        rows = []
        for el in root.iter():
            t = (el.get("text") or "").strip()
            m = BR.match(el.get("bounds", ""))
            if t and m:
                x1, y1, x2, y2 = map(int, m.groups())
                if y1 < H * 0.35:
                    rows.append((y1, x1, t))
        logging.info("[진단] === 클릭 후 상단 35% 텍스트 ===")
        for y, x, t in sorted(rows)[:18]:
            logging.info(f"[진단]   y={y} x={x} {t[:42]!r}")
        self.driver.save_screenshot("logs/diag/aos_ridionly_after.png")


    def test_003_리디온리_요소구조_정밀(self):
        """'리디온리' 텍스트 요소가 몇 개인지, clickable 여부와 조상 클릭영역을 확인한다."""
        self.page.enter_generalbook_genrehome()
        time.sleep(4)
        root = ET.fromstring(self.driver.page_source)

        # 부모 추적용 맵
        parent = {c: p for p in root.iter() for c in p}

        logging.info("[진단] === 'ㄹ리디온리' 포함 요소 전수 ===")
        hits = 0
        for el in root.iter():
            t = (el.get("text") or "") + "|" + (el.get("content-desc") or "")
            if "리디온리" not in t:
                continue
            hits += 1
            m = BR.match(el.get("bounds", ""))
            cls = (el.get("class") or "").split(".")[-1]
            logging.info(
                f"[진단] #{hits} {cls} bounds={el.get('bounds')} "
                f"text={el.get('text')!r} desc={el.get('content-desc')!r} "
                f"clickable={el.get('clickable')} enabled={el.get('enabled')}"
            )
            # 조상 3단계까지 clickable 찾기
            cur, depth = el, 0
            while cur in parent and depth < 4:
                cur = parent[cur]
                depth += 1
                ccls = (cur.get("class") or "").split(".")[-1]
                logging.info(
                    f"[진단]      조상{depth} {ccls} bounds={cur.get('bounds')} "
                    f"clickable={cur.get('clickable')} id={(cur.get('resource-id') or '').split('/')[-1]!r}"
                )
        logging.info(f"[진단] 총 {hits}개")

        # 퀵메뉴 행 전체(같은 y밴드) 나열
        s2 = self.driver.get_window_size()
        logging.info("[진단] === 퀵메뉴 행 후보(라벨 y밴드) ===")
        for el in root.iter():
            t = (el.get("text") or "").strip()
            m = BR.match(el.get("bounds", ""))
            if not t or not m:
                continue
            x1, y1, x2, y2 = map(int, m.groups())
            if 0.58 * s2["height"] < y1 < 0.70 * s2["height"]:
                logging.info(f"[진단]   y={y1}~{y2} x={x1}~{x2} {t[:20]!r} clickable={el.get('clickable')}")


    def test_004_수동확인용_대기(self):
        """앱을 로그인 상태로 도서 장르홈에 띄워두고 대기한다(사용자 수동 확인용).
        세션이 끊기면 앱이 제거되므로 대기 시간 동안 세션을 유지한다."""
        self.page.enter_generalbook_genrehome()
        time.sleep(4)
        logging.info(f"[진단] 장르홈 노출: {self.page.is_generalbook_genrehome_displayed()}")
        logging.info("[진단] ★ 준비 완료 - 수동으로 '리디온리' 퀵메뉴를 눌러보세요 (10분 대기)")
        for i in range(1, 21):
            time.sleep(30)
            try:
                logging.info(f"[진단] 대기 {i * 30}초 - 상단타이틀: {self.page.get_current_top_title()!r}")
            except Exception as e:
                logging.info(f"[진단] 대기 {i * 30}초 - 조회 실패: {type(e).__name__}")
