from selenium.webdriver.common.by import By
from appium.webdriver.common.appiumby import AppiumBy

class AOS_GenrehomeLocators:
    #웹툰 장르홈
    WEBTOON_RECOMMEND_TAB         = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("웹툰")')

    #만화 장르홈
    COMIC_RECOMMEND_TAB           = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("만화")')


   #CART_ICON          

class IOS_GenrehomeLocators:    
    #웹툰 장르홈
    WEBTOON_NEW_QUICK   = (AppiumBy.NAME, '이달의 신작') 

    #만화 장르홈
    COMIC_NEW_QUICK     = (AppiumBy.NAME, '무료') 
    
    #CART_ICON