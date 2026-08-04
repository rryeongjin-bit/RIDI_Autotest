
from selenium.webdriver.common.by import By
from appium.webdriver.common.appiumby import AppiumBy

class AOS_MyLocators:
    MY_TITLE                = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("MY").instance(0)')
    CHARGE_RIDI_CASH        = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("리디캐시 충전")')
    CHARGE_RIDI_CASH_TITLE  = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("캐시충전")')
    MY_RIDI_CASH            = (AppiumBy.ID, 'com.initialcoms.ridi:id/value')
    CHARGE_HISTORY          = (AppiumBy.ID, 'com.initialcoms.ridi:id/history_button')
    CHARGE_TIER_FIRST       = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("₩1,200")')
    CHARGE_BTN              = (AppiumBy.XPATH, '//android.widget.Button[@resource-id="com.android.vending:id/0_resource_name_obfuscated"]')
    CHARGE_COMPLETE_POPUP   = (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.initialcoms.ridi:id/dialog_title"]')
    CHARGE_COMPLETE_CHECK   = (AppiumBy.XPATH, '//android.widget.Button[@text="확인"]')

class IOS_MyLocators:
    MY_TITLE                = (AppiumBy.NAME, 'MY')
    CHARGE_RIDI_CASH        = (AppiumBy.NAME, '리디캐시 충전')
    CHARGE_RIDI_CASH_TITLE  = (AppiumBy.NAME, '캐시충전')
    MY_RIDI_CASH            = (AppiumBy.XPATH, '//XCUIElementTypeStaticText[contains(@name, "내 리디캐시") and contains(@name, "캐시")]')
    CHARGE_HISTORY          = (AppiumBy.NAME, '충전 내역')
    AUTOCHARGE_MANAGE_BTN   = (AppiumBy.NAME, '자동충전 관리')
    AUTOCHARGE_BANNER       = (AppiumBy.XPATH, '//XCUIElementTypeStaticText[@name="잔액 기준 자동충전"]')

class AOS_MyInfoLocators:
    #내정보 관리화면 관련
    MY_INFO                 = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("내 정보")')
    RECHECK_PW_TITLE        = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("com.initialcoms.ridi:id/title_text")')
    RECHECK_PW_INPUT        = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.widget.EditText")')
    RECHECK_PW_OK_BTN       = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("확인")')
    MY_INFO_MANAGE_TITLE    = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("내 정보 관리")')
    CURRENT_USER_ID         = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textMatches("^qa.*")')
    WITHDRAW_ACCOUNT        = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("회원탈퇴")')

class IOS_MyInfoLocators:
    #내정보 관리화면 관련
    MY_INFO                 = (AppiumBy.NAME, '내 정보')
    RECHECK_PW_TITLE        = (AppiumBy.NAME, '비밀번호 재확인')
    RECHECK_PW_INPUT        = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeSecureTextField')
    RECHECK_PW_OK_BTN       = (AppiumBy.NAME, '확인')
    MY_INFO_MANAGE_TITLE    = (AppiumBy.NAME, '내 정보 관리')
    CURRENT_USER_ID         = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeStaticText[`name MATCHES "qa.*"`]')
    BACK_TO_MYRIDI          = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name == "내 정보 관리"`][1]/XCUIElementTypeOther[1]/XCUIElementTypeOther')

#class AOS_SettingLocators:
class IOS_SettingLocators:
    #설정 관련
    SETTINGS                = (AppiumBy.NAME, '설정')
    SETTINGS_TITLE          = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeStaticText[`name == "설정"`]')
    SECTION_APPINFO_TITLE   = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeStaticText[`name == "앱 정보 및 이용약관"`]')
    WITHDRAW_ACCOUNT        = (AppiumBy.NAME, '회원탈퇴')

class AOS_LoginLocators:
    LOGIN_BTN    = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("로그인")')
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
    
