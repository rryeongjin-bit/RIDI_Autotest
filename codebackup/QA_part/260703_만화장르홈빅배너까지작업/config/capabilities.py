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

def _get_aos_device_name(udid: str) -> str:
    try:
        result = subprocess.run(
            ["adb", "-s", udid, "shell", "getprop", "ro.product.model"],
            capture_output=True, text=True
        )
        name = result.stdout.strip()
        if name:
            print(f"[capabilities] AOS 기기명 자동 감지: {name}")
            return name
    except Exception as e:
        print(f"[capabilities] AOS 기기명 자동 감지 실패: {e}")
    return udid

def _get_ios_device_info() -> tuple:
    try:
        udid = subprocess.run(
            ["idevice_id", "-l"],
            capture_output=True, text=True
        ).stdout.strip().splitlines()[0]

        name = subprocess.run(
            ["ideviceinfo", "-k", "DeviceName"],
            capture_output=True, text=True
        ).stdout.strip()

        if udid:
            print(f"[capabilities] iOS 기기명 자동 감지: {name}, UDID: {udid}")
            return udid, name or "QA iPhone"
    except Exception as e:
        print(f"[capabilities] iOS 기기 정보 자동 감지 실패: {e}")
    return None, None

_AOS_UDID = _get_aos_udid()
_IOS_UDID, _IOS_DEVICE_NAME = _get_ios_device_info()

DEVICE_CONFIG = {
    "aos": [
        {
            "port":        4723,
            "udid":        _AOS_UDID,
            "device_name": _get_aos_device_name(_AOS_UDID) if _AOS_UDID else "Unknown AOS",
            "type":        "real",
        }
    ],
    "ios": [
        {
            "port":        4724,
            "udid":        _IOS_UDID,
            "device_name": _IOS_DEVICE_NAME or "Unknown iOS",
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