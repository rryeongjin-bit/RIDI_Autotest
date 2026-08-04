from selenium.webdriver.common.by import By
from appium.webdriver.common.appiumby import AppiumBy

class AOS_CartLocators:
    # CART_TAB        = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("카트").instance(1)')
    # WISH_TAB        = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("위시리스트")')
    RENT_TAB        = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("대여 가능")')
    OWN_TAB         = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("소장 가능 1")')
    RENT_PAY_BTN    = (By.XPATH, '//form[@id="form"]/article[1]/div/div[2]/button')
    OWN_PAY_BTN     = (By.XPATH, '//form[@id="form"]/article[1]/div/div[2]/button')
    CHECKBOX_ALL    = (By.XPATH, '//form[@id="form"]/article[2]/div/div[1]/div[1]/label')
    CHECKBOX_FIRST  = (By.XPATH, '(//div[starts-with(@id, "book_")])[1]/div[1]/div/div[1]/label')
 
class IOS_CartLocators:
    #CART_TAB        
    #WISH_TAB       
    RENT_TAB        = (AppiumBy.NAME, '대여 가능')
    OWN_TAB         = (AppiumBy.NAME, '소장 가능 1')
    RENT_PAY_BTN    = (AppiumBy.NAME, '대여로 구매하기')
    OWN_PAY_BTN     = (AppiumBy.NAME, '소장으로 구매하기')
    CHECKBOX_ALL    = (AppiumBy.NAME, '전체 선택')
    #CHECKBOX_FIRST  = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name == ""]')

