from selenium.webdriver.common.by import By
from appium.webdriver.common.appiumby import AppiumBy

class AOS_GenrehomeLocators:
    WEBTOON_TAB         = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("웹툰")')
   #CART_ICON          

class IOS_GenrehomeLocators:    
    WEBTOON_NEW_QUICK   = (AppiumBy.NAME, '이달의 신작')
    #CART_ICON