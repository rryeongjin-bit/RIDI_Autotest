from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
from config.settings import *
import os
import subprocess
import re

APP_DIR = "/Users/ridi/Desktop/appfile"

def _get_aos_udid() -> str:
    try:
        result = subprocess.run(
            ["adb", "devices"],
            capture_output=True, text=True
        )
        lines = result.stdout.strip().splitlines()
        for line in lines[1:]:  
            if "device" in line and "offline" not in line:
                udid = line.split()[0]
                print(f"[capabilities] AOS UDID 자동 감지: {udid}")
                return udid
    except Exception as e:
        print(f"[capabilities] AOS UDID 자동 감지 실패: {e}")
    return None

def _get_ios_udid() -> str:
    try:
        result = subprocess.run(
            ["xcrun", "xctrace", "list", "devices"],
            capture_output=True, text=True
        )
        for line in result.stdout.splitlines():
            if "Simulator" in line or "MacBook" in line or line.startswith("=="):
                continue
            match = re.search(r'\([\d.]+\)\s+\(([0-9a-fA-F\-]{25,})\)', line)
            if match:
                udid = match.group(1)
                print(f"[capabilities] iOS UDID 자동 감지: {udid}")
                return udid
    except Exception as e:
        print(f"[capabilities] iOS UDID 자동 감지 실패: {e}")
    return None

DEVICE_CONFIG = {
    "aos": [
        {
            "port":        4723,
            "udid":        _get_aos_udid(),
            "device_name": "R5CY60QNY9N",
            "type":        "real",
        }
    ],
    "ios": [
        {
            "port":        4724,
            "udid":        _get_ios_udid(),
            "device_name": "QA iPhone",
            "type":        "real",
        }
    ]
}

def get_capabilities(platform: str, device: dict):
    if platform == "aos":
        return _get_aos_capabilities(device)
    elif platform == "ios":
        return _get_ios_capabilities(device)
    else:
        raise ValueError(f"[capabilities] 지원하지 않는 플랫폼: {platform}")


def _get_aos_capabilities(device: dict) -> UiAutomator2Options:
    options = UiAutomator2Options()
    options.platform_name    = "Android"
    options.device_name      = device["device_name"]
    options.udid             = device["udid"]
    options.automation_name  = "UiAutomator2"
    options.app_package      = APP_PACKAGE
    options.app_activity     = APP_ACTIVITY
    options.no_reset         = False
    options.full_reset       = True
    options.app              = os.path.join(APP_DIR, "app.apk")
    options.set_capability("chromedriverAutoDownload", True)
    return options

def _get_ios_capabilities(device: dict) -> XCUITestOptions:
    options = XCUITestOptions()
    options.platform_name    = "iOS"
    options.device_name      = device["device_name"]
    options.udid             = device["udid"]
    options.automation_name  = "XCUITest"
    options.bundle_id        = BUNDLE_ID_IOS
    options.no_reset         = False
    options.full_reset       = True
    options.app              = os.path.join(APP_DIR, "app.ipa")
    options.use_new_wda      = False
    options.set_capability("wdaConnectionTimeout", 120000)
    options.set_capability("commandTimeout", 120)
    return options

def get_server_url(port: int) -> str:
    return f"http://localhost:{port}"