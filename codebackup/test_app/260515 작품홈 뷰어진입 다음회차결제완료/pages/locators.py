
from selenium.webdriver.common.by import By
from appium.webdriver.common.appiumby import AppiumBy

class CommonLocators:
    ALERT_ALLOW_AOS    = (AppiumBy.ID, 'com.android.permissioncontroller:id/permission_message')
    ALLOW_BTN_AOS      = (AppiumBy.ID, 'com.android.permissioncontroller:id/permission_allow_button')
    ALERT_ALLOW_IOS    = (AppiumBy.NAME, '"리디"에서 알림을 보내고자 합니다.')
    ALLOW_BTN_IOS      = (AppiumBy.NAME, '허용')
    BRAZEPOPUP_CLOSE_AOS = (By.XPATH, '//a[@id="never_show_again"]/span')
    BRAZEPOPUP_CLOSE_IOS = (AppiumBy.NAME, '다시 보지 않기')

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
    #작품홈 상단영역
    ALL_CONTENTS_TITLE = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("두 명의 상속인")')
    ADULT_CONTENTS_TITLE = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("꽃은 밤을 걷는다")')

    #작품홈 회차앵커탭
    CONTENTS_EPISODE_TAB = (AppiumBy.ACCESSIBILITY_ID, '회차')
    CONTENTS_EPISODE_SORT = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("회차순")')
    
    CONTENTS_EPISODE_FIRST = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("1화")')
    CONTENTS_EPISODE_DOWNLOAD = (AppiumBy.XPATH, '(//android.view.ViewGroup[@resource-id="downloadButton"])[1]/android.widget.ImageView')
    RENT_OWNERSHIP_LABEL = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("ownershipLabel")')
    OWN_OWNERSHIP_LABEL  = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("ownershipLabel").text("소장")')

    ALL_CONTENTS_THUMBNAIL_FIRST  = (AppiumBy.XPATH, '//android.view.ViewGroup[@content-desc="0두 명의 상속인 1화, 0두 명의 상속인 1화, 2022.04.14, 18.1MB"]/android.view.ViewGroup')
    ALL_CONTENTS_THUMBNAIL_SECOND = (AppiumBy.XPATH, '//android.view.ViewGroup[@content-desc="0두 명의 상속인 2화, 0두 명의 상속인 2화, 2022.04.14, 19.6MB"]/android.view.ViewGroup')
    EPISODE_TITLE_BEFORE_DOWNLOAD = (AppiumBy.XPATH,
    '(//android.view.ViewGroup[@resource-id="downloadButton"])[1]/preceding-sibling::android.view.ViewGroup[@content-desc][1]/android.widget.TextView[1]')

    #결제팝업
    PAY_CASH_BTN = (By.XPATH, '//main/div/div/section/div[2]/div/div/section/div/button[1]')
    PAY_RENT_TAB = (By.XPATH, '//main/div/div/section/div[2]/div/div/div/div[1]/button[1]')
    PAY_RENT_BTN = (By.XPATH, '//main/div/div/section/div[2]/div/div/div/div[2]/div/div[2]/button')
    PAY_OWN_BTN  = (By.XPATH, '//button')
    
class IOS_ContentshomeLocators:
    #작품홈 상단영역
    ALL_CONTENTS_TITLE = (AppiumBy.NAME, '두 명의 상속인')
    ADULT_CONTENTS_TITLE = (AppiumBy.NAME, '꽃은 밤을 걷는다')

    #작품홈 회차앵커탭
    CONTENTS_EPISODE_TAB = (AppiumBy.NAME, '회차')
    CONTENTS_EPISODE_SORT = (AppiumBy.ACCESSIBILITY_ID, '회차순')

    CONTENTS_EPISODE_FIRST = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "1화"`][1]')
    CONTENTS_EPISODE_DOWNLOAD = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name == "downloadButton"`][1]')
    OWNERSHIP_LABEL = (AppiumBy.NAME, 'ownershipLabel')

    ALL_CONTENTS_THUMBNAIL_FIRST = (AppiumBy.XPATH, '(//XCUIElementTypeOther[@name="두 명의 상속인 1화 2022.04.14, 18.1MB"])[3]')
    ALL_CONTENTS_THUMBNAIL_SECOND = (AppiumBy.XPATH, '(//XCUIElementTypeOther[@name="두 명의 상속인 2화 2022.04.14, 19.6MB"])[3]')
    EPISODE_TITLE_BEFORE_DOWNLOAD = (AppiumBy.XPATH, '(//XCUIElementTypeOther[@name="downloadButton"])[1]/../../XCUIElementTypeOther[1]')
    
    #결제팝업
    PAY_CASH_BTN = (AppiumBy.NAME, '캐시로 결제')
    PAY_RENT_TAB = (AppiumBy.NAME, '대여')
    PAY_RENT_BTN = (AppiumBy.NAME, '대여로 결제')
    PAY_OWN_BTN  = (AppiumBy.NAME, '소장으로 결제')
    
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
    ADULT_VIEWER_TOP_TITLE = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeStaticText[`name CONTAINS "꽃은 밤을 걷는다"`]')
    NEXT_EPISODE_BTN = (AppiumBy.NAME, '다음화')
    ALL_NEXT_VIEWER_TOP_TITLE = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeStaticText[`name CONTAINS "두 명의 상속인"`]')
    ADULT_NEXT_VIEWER_TOP_TITLE = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeStaticText[`name CONTAINS "꽃은 밤을 걷는다"`]')
    VIEWER_BACK_BTN = (AppiumBy.NAME, '내 서재로 돌아가기')