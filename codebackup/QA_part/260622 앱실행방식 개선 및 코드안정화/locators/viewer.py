from selenium.webdriver.common.by import By
from appium.webdriver.common.appiumby import AppiumBy
   
class AOS_ViewerLocators:
    ALL_VIEWER_CONTENT = (AppiumBy.ID, 'com.initialcoms.ridi:id/reader_view')
    ADULT_VIEWER_CONTENT = (AppiumBy.ID, 'com.initialcoms.ridi:id/reader_page_layout')
    VIEWER_TOP_TITLE = (AppiumBy.ID, 'com.initialcoms.ridi:id/title')
    NEXT_EPISODE_BTN = (AppiumBy.ID, 'com.initialcoms.ridi:id/series_toolbar_next_book')
    NEXT_VIEWER_TOP_TITLE = (AppiumBy.ID, 'com.initialcoms.ridi:id/title')
    VIEWER_BACK_BTN = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("위로 이동")')

class IOS_ViewerLocators:
    ALL_VIEWER_CONTENT = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeWindow/XCUIElementTypeOther[3]/XCUIElementTypeOther')
    ADULT_VIEWER_CONTENT = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeWindow[1]/XCUIElementTypeOther[3]/XCUIElementTypeOther/XCUIElementTypeOther[1]/XCUIElementTypeOther[1]/XCUIElementTypeOther/XCUIElementTypeOther[1]/XCUIElementTypeOther/XCUIElementTypeWebView/XCUIElementTypeWebView/XCUIElementTypeWebView/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther')
    ALL_VIEWER_TOP_TITLE = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeStaticText[`name CONTAINS "두 명의 상속인"`]')
    ADULT_VIEWER_TOP_TITLE = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeStaticText[`name CONTAINS "제비 사냥"`]')
    NEXT_EPISODE_BTN = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeButton[`name == "다음 화 보기"`]')
    ALL_NEXT_VIEWER_TOP_TITLE = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeStaticText[`name CONTAINS "두 명의 상속인"`]')
    ADULT_NEXT_VIEWER_TOP_TITLE = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeStaticText[`name CONTAINS "제비 사냥"`]')
    VIEWER_BACK_BTN = (AppiumBy.NAME, '내 서재로 돌아가기')
