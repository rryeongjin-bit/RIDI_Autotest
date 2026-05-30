from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
from config.settings import *

DEVICE_CONFIG = {
    "aos": [
        {
            "port":        4723,
            "udid":        "R5CY60QNY9N",
            "device_name": "R5CY60QNY9N",
            "type":        "real",         
        }
    ],

    "ios": [
        {
            "port":        4724,
            "udid":        "00008140-000641321482801C",
            "device_name": "나리디의 iPhone",
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
    options.no_reset         = True
    options.full_reset        = False  
    options.set_capability("chromedriverAutoDownload", True)
    return options

def _get_ios_capabilities(device: dict) -> XCUITestOptions:
    options = XCUITestOptions()
    options.platform_name    = "iOS"
    options.device_name      = device["device_name"]
    options.udid             = device["udid"]
    options.automation_name  = "XCUITest"
    options.bundle_id        = BUNDLE_ID_IOS
    options.no_reset         = True
    options.full_reset        = False
    options.use_new_wda = False
    options.set_capability("wdaConnectionTimeout", 120000)
    options.set_capability("commandTimeout", 120)
    return options

def get_server_url(port: int) -> str:
    return f"http://localhost:{port}"