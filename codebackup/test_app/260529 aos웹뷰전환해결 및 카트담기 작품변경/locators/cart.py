from selenium.webdriver.common.by import By
from appium.webdriver.common.appiumby import AppiumBy

class AOS_CartLocators:
    # CART_TAB        = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("카트").instance(1)')
    # WISH_TAB        = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("위시리스트")')
    RENT_TAB        = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("대여 가능")')
    OWN_TAB         = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("소장 가능 1")')
    RENT_PAY_BTN    = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("대여로 구매하기")')
    OWN_PAY_BTN     = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("소장으로 구매하기")')
    CHECKBOX_ALL    = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.widget.TextView").instance(8)')
    CHECKBOX_FIRST  = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.view.View").instance(29)')

class IOS_CartLocators:
    #CART_TAB        
    #WISH_TAB       
    RENT_TAB        = (AppiumBy.NAME, '대여 가능')
    OWN_TAB         = (AppiumBy.NAME, '소장 가능 1')
    RENT_PAY_BTN    = (AppiumBy.NAME, '대여로 구매하기')
    OWN_PAY_BTN     = (AppiumBy.NAME, '소장으로 구매하기')
    CHECKBOX_ALL    = (AppiumBy.NAME, '전체 선택')
    #CHECKBOX_FIRST  = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name == "고깔모자의 아틀리에 15권"`]')

