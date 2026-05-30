import os
import glob
import logging
from pathlib import Path
from typing import Optional
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)


def get_latest_report(platform: str) -> Optional[str]:
    project_path = os.getenv("TEST_PROJECT_PATH", ".")
    report_dir = os.path.join(project_path, "reports", platform)
    reports = glob.glob(os.path.join(report_dir, "*.html"))
    if not reports:
        return None
    return max(reports, key=os.path.getmtime)


def capture_report_screenshot(report_path: str, output_path: str) -> bool:
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            page.goto(f"file://{report_path}")
            page.wait_for_load_state("networkidle")
            page.screenshot(path=output_path, full_page=True)
            browser.close()
            return True
    except Exception as e:
        logger.error(f"[reporter] 스크린샷 캡처 실패: {e}")
        return False

