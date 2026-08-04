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

# ===== [임시] 2026-08-04 iOS 기기 2대 병렬 실행용 - 요청 시 이 블록만 되돌리면 됨 =====
# 실기기 2대를 서로 다른 Appium 서버(4724 / 4726)에 붙여 다른 모듈을 동시에 검증하기 위한
# 환경변수 오버라이드다. 세 변수 모두 **주지 않으면 기존과 완전히 동일**하게 동작한다.
#   IOS_APPIUM_PORT : Appium 서버 포트          (미지정 시 4724)
#   IOS_UDID        : 사용할 기기 UDID           (미지정 시 idevice_id -l 첫 줄 = 기존 동작)
#   IOS_WDA_PORT    : WebDriverAgent 로컬 포트   (미지정 시 8100 = Appium 기본)
# IOS_UDID가 필요한 이유: _get_ios_device_info()가 idevice_id -l의 **첫 줄만** 쓰기 때문에
# 2대가 붙으면 어느 기기가 잡힐지 보장되지 않는다. AOS처럼 real/emulator 타입으로 구분할 수도
# 없어(둘 다 real) UDID를 직접 지정해야 한다.
# IOS_WDA_PORT가 필요한 이유: 두 기기가 기본 8100을 함께 쓰면 WDA가 충돌한다.
#
# 사용 예:
#   기기A(기존)  python -m pytest ... --platform ios --env real
#   기기B(추가)  IOS_APPIUM_PORT=4726 IOS_UDID=<UDID> IOS_WDA_PORT=8101 python -m pytest ...
#
#   되돌리는 방법: 아래 _IOS_PORT / _IOS_REAL_UDID 재할당 2줄을 지우고
#                 "port": 4724 로 되돌린 뒤, _get_ios_capabilities의 wdaLocalPort 줄을 삭제
_IOS_PORT = int(os.getenv("IOS_APPIUM_PORT", 4724))
if os.getenv("IOS_UDID"):
    _IOS_REAL_UDID = os.getenv("IOS_UDID")
    print(f"[capabilities] iOS UDID 환경변수 지정: {_IOS_REAL_UDID}")
# ===== [임시] 끝 =====

_IOS_DEVICES = []
if _IOS_REAL_UDID:
    _IOS_DEVICES.append({
        "port":        _IOS_PORT,
        "udid":        _IOS_REAL_UDID,
        "device_name": _IOS_REAL_NAME or "QA iPhone",
        "type":        "real",
    })
if _IOS_SIM_UDID:
    _IOS_DEVICES.append({
        "port":        _IOS_PORT,
        "udid":        _IOS_SIM_UDID,
        "device_name": _IOS_SIM_NAME or "QA iOS Simulator",
        "type":        "simulator",
    })

DEVICE_CONFIG = {
    "aos": [
        {
            # ===== [임시] 2026-08-03 AOS 에뮬레이터 병행 실행용 - 요청 시 이 1줄만 4723으로 되돌리면 됨 =====
            # 실기기를 4723에서 수동 실행하는 동안 에뮬레이터를 별도 포트(4725)로 붙이기 위한
            # 환경변수 오버라이드다. AOS_APPIUM_PORT를 주지 않으면 기존과 완전히 동일하게
            # 4723을 쓰므로 기존 실행에는 영향이 없다.
            #   되돌리는 방법:  "port": 4723,   ← 아래 한 줄을 이것으로 교체
            "port":        int(os.getenv("AOS_APPIUM_PORT", 4723)),
            # ===== [임시] 끝 =====
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
    # ===== [임시] 2026-08-04 iOS 2대 병렬용 - IOS_WDA_PORT 미지정 시 기본 8100(=기존 동작) =====
    options.set_capability("wdaLocalPort", int(os.getenv("IOS_WDA_PORT", 8100)))
    # ===== [임시] 끝 =====
    return options

def get_server_url(port: int) -> str:
    return f"http://localhost:{port}"