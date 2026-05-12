
from selenium.webdriver.common.by import By
from appium.webdriver.common.appiumby import AppiumBy

class CommonLocators:
    ALERT_ALLOW    = (AppiumBy.ID, 'com.android.permissioncontroller:id/permission_message')
    ALLOW_BTN      = (AppiumBy.ID, 'com.android.permissioncontroller:id/permission_allow_button')
    BRAZEPOPUP_CLOSE_AOS = (By.XPATH, '//a[@id="never_show_again"]/span')
    BRAZEPOPUP_CLOSE_IOS = (AppiumBy.ACCESSIBILITY_ID, '다시 보지 않기')
    #TWOFACTOR_ALERT_AOS = (AppiumBy.ANDROID_UIAUTOMATOR,'new UiSelector().text("2단계 인증으로 계정을 더 안전하게")')
    #TWOFACTOR_ALERT_CLOSE_AOS = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("다시 보지 않기")')

class AOS_ReplacedeviceLocators:
    REPLACEDEVICE_LIST_TITLE   = (AppiumBy.ID, 'com.initialcoms.ridi:id/title') 
    REPLACEDEVICE_TOGGLE_FIRST = (AppiumBy.ID, 'com.initialcoms.ridi:id/selection_radio_button')
    REPLACEDEVICE_BTN          = (AppiumBy.ID, 'com.initialcoms.ridi:id/replace_button')

class IOS_ReplacedeviceLocators:
    REPLACEDEVICE_LIST_TITLE   = (AppiumBy.XPATH, '//XCUIElementTypeStaticText[@name="기기 대체"]')
    REPLACEDEVICE_BTN          = (AppiumBy.XPATH, '//XCUIElementTypeButton[@name="대체하기"]')

class AOS_LoginLocators:
    LOGIN_BTN    = (AppiumBy.ACCESSIBILITY_ID, '로그인')
    ID_INPUT     = (By.XPATH, '//input[@name="username"]')
    PW_INPUT     = (By.XPATH, '//input[@name="password"]')
    LOGIN_BUTTON = (By.XPATH, '//button[@type="submit"]')
    LOGOUT_BTN   = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("로그아웃")')

class IOS_LoginLocators:
    LOGIN_BTN    = (AppiumBy.NAME, '로그인')
    ID_INPUT     = (AppiumBy.CLASS_NAME, 'XCUIElementTypeTextField')
    PW_INPUT     = (AppiumBy.CLASS_NAME, 'XCUIElementTypeSecureTextField')
    LOGIN_BUTTON = (AppiumBy.XPATH, '//XCUIElementTypeButton[@name="로그인"]')
    LOGOUT_BTN   = (AppiumBy.NAME, '로그아웃')

class AOS_LogoutLocators:
    LOGOUT_CONFIRM_POPUP = (AppiumBy.ID, 'com.initialcoms.ridi:id/dialog_title')
    LOGOUT_CONFIRM_BTN   = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("로그아웃")')

class IOS_LogoutLocators:
    LOGOUT_CONFIRM_POPUP = (AppiumBy.NAME, '로그아웃하시겠습니까?')
    LOGOUT_CONFIRM_BTN   = (AppiumBy.NAME, '로그아웃')  

class AOS_GenrehomeLocators:
    WEBTOON_TAB = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("웹툰")')

class IOS_GenrehomeLocators:    
    WEBTOON_NEW_QUICK = (AppiumBy.NAME, '이달의 신작')

class AOS_ContentshomeLocators:
    CONTENTS_EPISODE_TAB = (AppiumBy.ACCESSIBILITY_ID, '회차')
    CONTENTS_EPISODE_SORT = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("회차순")')
    CONTENTS_4TH_EPISODE = (AppiumBy.ANDROID_UIAUTOMATOR,'new UiSelector().className("android.widget.ImageView").instance(9)')

class IOS_ContentshomeLocators:
    CONTENTS_EPISODE_TAB = (AppiumBy.NAME, '회차')
    CONTENTS_EPISODE_SORT = (AppiumBy.ACCESSIBILITY_ID, '회차순')
    CONTENTS_4TH_EPISODE = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name == "downloadButton"`][4]')