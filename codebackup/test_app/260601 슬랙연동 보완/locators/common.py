from selenium.webdriver.common.by import By
from appium.webdriver.common.appiumby import AppiumBy

class CommonLocators:
    ALERT_ALLOW_AOS             = (AppiumBy.ID, 'com.android.permissioncontroller:id/permission_message')
    ALLOW_BTN_AOS               = (AppiumBy.ID, 'com.android.permissioncontroller:id/permission_allow_button')
    #ALERT_ALLOW_IOS         = (AppiumBy.IOS_PREDICATE, 'type == "XCUIElementTypeAlert"')
    #ALERT_TRACKING_IOS      = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeAlert[`name == "‘리디’이(가) 다른 회사의 앱 및 웹사이트에 걸친 사용자의 활동을 추적하도록 허용하겠습니까?"`]')
    #ALLOW_BTN_IOS           = (AppiumBy.IOS_PREDICATE, 'type == "XCUIElementTypeButton" AND label == "허용"')
    #BRAZEPOPUP_AOS          = (AppiumBy.ID, 'com.initialcoms.ridi:id/com_braze_inappmessage_html')
    #BRAZEPOPUP_IOS
    BRAZEPOPUP_CLOSE_AOS        = (By.XPATH, '//a[@id="never_show_again"]/span')
    BRAZEPOPUP_CLOSE_IOS        = (AppiumBy.NAME, '다시 보지 않기')
    
    #작품홈 선택구매/카트담기 회차목록
    SELECT_DRAG_ALERT_AOS       = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("com.initialcoms.ridi:id/big_text")')
    SELECT_DRAG_ALERT_CLOSE_AOS = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("com.initialcoms.ridi:id/bottom_button")')
    SELECT_DRAG_ALERT_IOS       = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeStaticText[`name == "드래그로 빠르게 선택"`]')
    SELECT_DRAG_ALERT_CLOSE_IOS = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeButton[`name == "확인"`]')

class AOS_ReplacedeviceLocators:
    REPLACEDEVICE_LIST_TITLE   = (AppiumBy.ID, 'com.initialcoms.ridi:id/title') 
    REPLACEDEVICE_TOGGLE_FIRST = (AppiumBy.ID, 'com.initialcoms.ridi:id/selection_radio_button')
    REPLACEDEVICE_BTN          = (AppiumBy.ID, 'com.initialcoms.ridi:id/replace_button')

class IOS_ReplacedeviceLocators:
    REPLACEDEVICE_LIST_TITLE   = (AppiumBy.XPATH, '//XCUIElementTypeStaticText[@name="기기 대체"]')
    #sREPLACEDEVICE_TOGGLE_FIRST =
    REPLACEDEVICE_BTN          = (AppiumBy.XPATH, '//XCUIElementTypeButton[@name="대체하기"]')






