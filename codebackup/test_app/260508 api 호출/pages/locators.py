from selenium.webdriver.common.by import By
from appium.webdriver.common.appiumby import AppiumBy

class CommonLocators:
    ALERT_ALLOW    = (By.ID, "com.android.permissioncontroller:id/permission_message")
    ALLOW_BTN      = (By.ID, "com.android.permissioncontroller:id/permission_allow_button")
    BRAZEPOPUP_CLOSE_AOS = (By.ID, "never_show_again")
    BRAZEPOPUP_CLOSE_IOS = (AppiumBy.ACCESSIBILITY_ID, "다시 보지 않기")

class AOS_ReplacedeviceLocators:
    REPLACEDEVICE_LIST_TITLE   = (By.ID, "com.initialcoms.ridi:id/title")
    REPLACEDEVICE_TOGGLE_FIRST = (By.XPATH, "(//android.widget.RadioButton[@resource-id='com.initialcoms.ridi:id/selection_radio_button'])[1]")
    REPLACEDEVICE_BTN          = (By.ID, "com.initialcoms.ridi:id/replace_button")

class IOS_ReplacedeviceLocators:
    REPLACEDEVICE_LIST_TITLE   = (By.XPATH, "//XCUIElementTypeStaticText[@name='기기 대체']")
    # REPLACEDEVICE_TOGGLE_FIRST 
    REPLACEDEVICE_BTN          = (By.XPATH, "//XCUIElementTypeButton[@name='대체하기']")

class AOS_LoginLocators:
    LOGIN_BTN    = (By.XPATH, "//android.view.ViewGroup[@content-desc='로그인']")
    ID_INPUT     = (By.XPATH, "//input[@name='username'")
    PW_INPUT     = (By.XPATH, "//input[@name='password']")
    LOGIN_BUTTON = (By.XPATH, "//div[@id='__next']/div[2]/div/form[1]/button")
    LOGOUT_BNT   = (By.ID, "button-label")

class IOS_LoginLocators:
    LOGIN_BTN    = (By.XPATH, "//XCUIElementTypeOther[@name='button-label']")
    ID_INPUT     = (By.CLASS_NAME, "XCUIElementTypeTextField")
    PW_INPUT     = (By.CLASS_NAME, "XCUIElementTypeSecureTextField")
    LOGIN_BUTTON = (By.XPATH, "//XCUIElementTypeButton[@name='로그인']")
    LOGOUT_BNT   = (By.XPATH, "(//XCUIElementTypeOther[@name='button-label'])[1]")


