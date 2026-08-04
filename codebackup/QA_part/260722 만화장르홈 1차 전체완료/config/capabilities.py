from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
from config.settings import *
import os
import subprocess
import re

APP_DIR = "/Users/ridi/Desktop/appfile"

def _get_aos_devices() -> list:
    devices = []
    try:
        result = subprocess.run(
            ["adb", "devices"],
            capture_output=True, text=True
        )
        lines = result.stdout.strip().splitlines()
        for line in lines[1:]:
            if "device" in line and "offline" not in line:
                udid = line.split()[0]
                device_type = "emulator" if udid.startswith("emulator-") else "real"
                if any(d["type"] == device_type for d in devices):
                    continue
                print(f"[capabilities] AOS {device_type} 기기 자동 감지: {udid}")
                devices.append({"udid": udid, "type": device_type})
    except Exception as e:
        print(f"[capabilities] AOS 기기 자동 감지 실패: {e}")
    return devices

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

def _get_ios_simulator_info() -> tuple:
    try:
        result = subprocess.run(
            ["xcrun", "simctl", "list", "devices", "booted"],
            capture_output=True, text=True
        )
        for line in result.stdout.splitlines():
            match = re.search(r'^\s*(.+?)\s+\(([0-9A-Fa-f-]{36})\)\s+\(Booted\)', line)
            if match:
                name, udid = match.group(1), match.group(2)
                print(f"[capabilities] iOS 시뮬레이터 자동 감지: {name}, UDID: {udid}")
                return udid, name
    except Exception as e:
        print(f"[capabilities] iOS 시뮬레이터 자동 감지 실패: {e}")
    return None, None

def _get_ios_simulator_bundle_id(app_path: str) -> str:
    try:
        result = subprocess.run(
            ["/usr/libexec/PlistBuddy", "-c", "Print :CFBundleIdentifier", os.path.join(app_path, "Info.plist")],
            capture_output=True, text=True
        )
        bundle_id = result.stdout.strip()
        if bundle_id:
            print(f"[capabilities] 시뮬레이터 앱 Bundle ID 자동 감지: {bundle_id}")
            return bundle_id
    except Exception as e:
        print(f"[capabilities] 시뮬레이터 앱 Bundle ID 자동 감지 실패: {e}")
    return BUNDLE_ID_IOS

_AOS_DEVICES = _get_aos_devices()
_IOS_REAL_UDID, _IOS_REAL_NAME = _get_ios_device_info()
_IOS_SIM_UDID, _IOS_SIM_NAME = _get_ios_simulator_info()

_IOS_DEVICES = []
if _IOS_REAL_UDID:
    _IOS_DEVICES.append({
        "port":        4724,
        "udid":        _IOS_REAL_UDID,
        "device_name": _IOS_REAL_NAME or "QA iPhone",
        "type":        "real",
    })
if _IOS_SIM_UDID:
    _IOS_DEVICES.append({
        "port":        4724,
        "udid":        _IOS_SIM_UDID,
        "device_name": _IOS_SIM_NAME or "QA iOS Simulator",
        "type":        "simulator",
    })

DEVICE_CONFIG = {
    "aos": [
        {
            "port":        4723,
            "udid":        d["udid"],
            "device_name": _get_aos_device_name(d["udid"]),
            "type":        d["type"],
        }
        for d in _AOS_DEVICES
    ],
    "ios": _IOS_DEVICES
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
    is_simulator = device["type"] == "simulator"
    app_path     = os.path.join(APP_DIR, "Ridibooks for Appium.app" if is_simulator else "app.ipa")

    options = XCUITestOptions()
    options.platform_name    = "iOS"
    options.device_name      = device["device_name"]
    options.udid             = device["udid"]
    options.automation_name  = "XCUITest"
    options.bundle_id        = _get_ios_simulator_bundle_id(app_path) if is_simulator else BUNDLE_ID_IOS
    options.no_reset         = False
    options.full_reset       = not is_simulator
    options.app              = app_path
    options.use_new_wda      = False
    options.set_capability("wdaConnectionTimeout", 120000)
    options.set_capability("commandTimeout", 120)
    return options

def get_server_url(port: int) -> str:
    return f"http://localhost:{port}"