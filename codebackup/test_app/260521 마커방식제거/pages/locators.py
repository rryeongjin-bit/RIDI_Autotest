
from selenium.webdriver.common.by import By
from appium.webdriver.common.appiumby import AppiumBy

class CommonLocators:
    ALERT_ALLOW_AOS         = (AppiumBy.ID, 'com.android.permissioncontroller:id/permission_message')
    ALLOW_BTN_AOS           = (AppiumBy.ID, 'com.android.permissioncontroller:id/permission_allow_button')
    #ALERT_ALLOW_IOS         = (AppiumBy.IOS_PREDICATE, 'type == "XCUIElementTypeAlert"')
    #ALERT_TRACKING_IOS      = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeAlert[`name == "‘리디’이(가) 다른 회사의 앱 및 웹사이트에 걸친 사용자의 활동을 추적하도록 허용하겠습니까?"`]')
    #ALLOW_BTN_IOS           = (AppiumBy.IOS_PREDICATE, 'type == "XCUIElementTypeButton" AND label == "허용"')
    BRAZEPOPUP_AOS          = (AppiumBy.ID, 'com.initialcoms.ridi:id/com_braze_inappmessage_html')
    #BRAZEPOPUP_IOS
    BRAZEPOPUP_CLOSE_AOS    = (By.XPATH, '//a[@id="never_show_again"]/span')
    BRAZEPOPUP_CLOSE_IOS    = (AppiumBy.NAME, '다시 보지 않기')

class AOS_ReplacedeviceLocators:
    REPLACEDEVICE_LIST_TITLE   = (AppiumBy.ID, 'com.initialcoms.ridi:id/title') 
    REPLACEDEVICE_TOGGLE_FIRST = (AppiumBy.ID, 'com.initialcoms.ridi:id/selection_radio_button')
    REPLACEDEVICE_BTN          = (AppiumBy.ID, 'com.initialcoms.ridi:id/replace_button')

class IOS_ReplacedeviceLocators:
    REPLACEDEVICE_LIST_TITLE   = (AppiumBy.XPATH, '//XCUIElementTypeStaticText[@name="기기 대체"]')
    #sREPLACEDEVICE_TOGGLE_FIRST =
    REPLACEDEVICE_BTN          = (AppiumBy.XPATH, '//XCUIElementTypeButton[@name="대체하기"]')

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

class AOS_GenrehomeLocators:
    WEBTOON_TAB         = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("웹툰")')
   #CART_ICON          

class IOS_GenrehomeLocators:    
    WEBTOON_NEW_QUICK   = (AppiumBy.NAME, '이달의 신작')
    #CART_ICON

class AOS_ContentshomeLocators:
    #작품홈 상단영역
    ALL_CONTENTS_TITLE      = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("두 명의 상속인")')
    ADULT_CONTENTS_TITLE    = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("꽃은 밤을 걷는다")')
    CART_CONTENTS_TITLE     = (AppiumBy.ANDROID_UIAUTOMATOR,  'new UiSelector().text("고깔모자의 아틀리에")')

    #작품홈 회차앵커탭
    CONTENTS_EPISODE_TAB      = (AppiumBy.ACCESSIBILITY_ID, '회차')
    CONTENTS_EPISODE_SORT     = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("회차순")')
    SELECTBUY_CART_BTN        = (AppiumBy.ACCESSIBILITY_ID, '선택 구매, /, 카트 담기')
    SELECTBUY_CART_TITLE      = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("고깔모자의 아틀리에 총 15권")')
    
    CONTENTS_EPISODE_FIRST      = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("1화")')
    CONTENTS_EPISODE_DOWNLOAD   = (AppiumBy.XPATH, '(//android.view.ViewGroup[@resource-id="downloadButton"])[1]/android.widget.ImageView')
    RENT_OWNERSHIP_LABEL        = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("ownershipLabel")')
    OWN_OWNERSHIP_LABEL         = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("ownershipLabel").text("소장")')

    ALL_CONTENTS_THUMBNAIL_FIRST  = (AppiumBy.XPATH, '//android.view.ViewGroup[@content-desc="0두 명의 상속인 1화, 0두 명의 상속인 1화, 2022.04.14, 18.1MB"]/android.view.ViewGroup')
    ALL_CONTENTS_THUMBNAIL_SECOND = (AppiumBy.XPATH, '//android.view.ViewGroup[@content-desc="0두 명의 상속인 2화, 0두 명의 상속인 2화, 2022.04.14, 19.6MB"]/android.view.ViewGroup')
    EPISODE_TITLE_BEFORE_DOWNLOAD = (AppiumBy.XPATH,
    '(//android.view.ViewGroup[@resource-id="downloadButton"])[1]/preceding-sibling::android.view.ViewGroup[@content-desc][1]/android.widget.TextView[1]')

    #작품홈 선택구매 및 카트담기 화면
    SELECTBUY_CART_SORT_EPISODE     = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("회차순")')
    SELECTBUY_CART_SORT_LAST        = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("최신순")')
    SELECTBUY_CART_RENT_TAB         = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("대여")')
    SELECTBUY_CART_OWN_TAB          = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("소장")')
    SELECTBUY_CART_RENT_ITEM        = (AppiumBy.ACCESSIBILITY_ID, '0고깔모자의 아틀리에 1권, 0고깔모자의 아틀리에 1권, 2019.04.18, 214쪽, 328.7MB')
    SELECTBUY_CART_OWN_ITEM         = (AppiumBy.ACCESSIBILITY_ID, '고깔모자의 아틀리에 15권, 고깔모자의 아틀리에 15권, 2026.05.01, 198쪽, 325.2MB, 소장 3,800원 3,420원')
    SELECTBUY_CART_OWN_LAST_ITEM    = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("고깔모자의 아틀리에 15권, 고깔모자의 아틀리에 15권, 2026.05.01, 198쪽, 325.2MB, 소장 3,800원 3,420원")')
    SELECTBUY_CART_FIRST_TOGGLE     = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.widget.ImageView").instance(2)')
    CART_BTN                        = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("카트")')
    CART_TOAST                      = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("카트에 작품을 담았습니다.")')

    #결제팝업
    PAY_CASH_BTN = (By.XPATH, '//main/div/div/section/div[2]/div/div/section/div/button[1]')
    PAY_RENT_TAB = (By.XPATH, '//main/div/div/section/div[2]/div/div/div/div[1]/button[1]')
    PAY_RENT_BTN = (By.XPATH, '//main/div/div/section/div[2]/div/div/div/div[2]/div/div[2]/button')
    PAY_OWN_BTN  = (By.XPATH, '//button')
    
class IOS_ContentshomeLocators:
    #작품홈 상단영역
    ALL_CONTENTS_TITLE      = (AppiumBy.NAME, '두 명의 상속인')
    ADULT_CONTENTS_TITLE    = (AppiumBy.NAME, '꽃은 밤을 걷는다')
    CART_CONTENTS_TITLE     = (AppiumBy.NAME, '고깔모자의 아틀리에')

    #작품홈 회차앵커탭
    CONTENTS_EPISODE_TAB    = (AppiumBy.NAME, '회차')
    CONTENTS_EPISODE_SORT   = (AppiumBy.ACCESSIBILITY_ID, '회차순')
    SELECTBUY_CART_BTN      = (AppiumBy.NAME, '선택 구매 / 카트 담기')
    SELECTBUY_CART_TITLE    = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeStaticText[`name == "고깔모자의 아틀리에 총 15권"`]')

    CONTENTS_EPISODE_FIRST          = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "1화"`][1]')
    CONTENTS_EPISODE_DOWNLOAD       = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name == "downloadButton"`][1]')
    OWNERSHIP_LABEL                 = (AppiumBy.NAME, 'ownershipLabel')

    ALL_CONTENTS_THUMBNAIL_FIRST  = (AppiumBy.XPATH, '(//XCUIElementTypeOther[@name="두 명의 상속인 1화 2022.04.14, 18.1MB"])[3]')
    ALL_CONTENTS_THUMBNAIL_SECOND = (AppiumBy.XPATH, '(//XCUIElementTypeOther[@name="두 명의 상속인 2화 2022.04.14, 19.6MB"])[3]')
    EPISODE_TITLE_BEFORE_DOWNLOAD = (AppiumBy.XPATH, '(//XCUIElementTypeOther[@name="downloadButton"])[1]/../../XCUIElementTypeOther[1]')
    
    #작품홈 선택구매 및 카트담기 화면
    SELECTBUY_CART_SORT_EPISODE  = (AppiumBy.XPATH, '(//XCUIElementTypeOther[@name="회차순"])[2]')
    SELECTBUY_CART_SORT_LAST     = (AppiumBy.XPATH, '(//XCUIElementTypeOther[@name="최신순"])[2]')
    SELECTBUY_CART_RENT_TAB      = (AppiumBy.NAME, '대여 대여')
    SELECTBUY_CART_OWN_TAB       = (AppiumBy.NAME, '소장 소장')
    SELECTBUY_CART_RENT_ITEM     = (AppiumBy.NAME, '고깔모자의 아틀리에 1권 2019.04.18, 214쪽, 328.7MB')
    SELECTBUY_CART_OWN_ITEM      = (AppiumBy.NAME, '고깔모자의 아틀리에 1권 2019.04.18, 214쪽, 328.7MB 소장 3,800원 3,420원')
    SELECTBUY_CART_OWN_LAST_ITEM = (AppiumBy.NAME, '고깔모자의 아틀리에 15권 2026.05.01, 198쪽, 325.2MB 소장 3,800원 3,420원')
    #SELECTBUY_CART_FIRST_TOGGLE 
    CART_BTN                     = (AppiumBy.NAME, '카트')
    CART_TOAST                   = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name == "카트에 작품을 담았습니다. 보기"`][2]')

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

class AOS_CartLocators:
    # CART_TAB        = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("카트").instance(1)')
    # WISH_TAB        = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("위시리스트")')
    # RENT_TAB        = (By.XPATH, 'xpath//form[@id="form"]/article[1]/ul/li[1]/a')
    # OWN_TAB         = (By.XPATH, '//form[@id="form"]/article[1]/ul/li[2]/a')
    # RENT_PAY_BTN    = (By.XPATH, '//form[@id="form"]/article[1]/div/div[2]/button')
    OWN_PAY_BTN     = (By.XPATH, '//form[@id="form"]/article[1]/div/div[2]/button')
    CHECKBOX_ALL    = (By.XPATH, '//form[@id="form"]/article[2]/div/div[1]/div[1]/label')
    CHECKBOX_FIRST  = (By.XPATH, '//div[@id="book_505106678"]/div[1]/div/div[1]/label')

class IOS_CartLocators:
    #CART_TAB        
    #WISH_TAB       
    RENT_TAB        = (AppiumBy.NAME, '대여 가능 1')
    OWN_TAB         = (AppiumBy.NAME, '소장 가능 2')
    RENT_PAY_BTN    = (AppiumBy.NAME, '대여로 구매하기')
    OWN_PAY_BTN     = (AppiumBy.NAME, '소장으로 구매하기')
    CHECKBOX_ALL    = (AppiumBy.NAME, '전체 선택')
    #CHECKBOX_FIRST  = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name == "고깔모자의 아틀리에 15권"`]')

class AOS_CheckoutLocators:
    ORDER_LIST_SECTION      = (By.XPATH, '//article[@id="books_contents"]/section/div[1]/article/h3')
    PAYMENT_DETAIL_SECTION  = (By.XPATH, '//div[@id="ISLANDS__Ridipay"]/div/div/section[1]/h2')
    PAYMENT_AGREE           = (AppiumBy.ANDROID_UIAUTOMATOR,'new UiSelector().textContains("구매에 동의")')
    PAYMENT_BTN             = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("결제")')
    PAYMENT_COMPLETE        = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("결제 완료")')
    #MOVE_TO_ORDERLIST      = (By.XPATH,'//main/div/div[1]/button[1]')
    MOVE_TO_GENREHOME       = (By.XPATH, '//main/div/div[1]/button[2]')

class IOS_CheckoutLocators:
    ORDER_LIST_SECTION      = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeStaticText[`name == "1"`]')
    PAYMENT_DETAIL_SECTION  = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeStaticText[`name == "결제 상세"`]')
    PAYMENT_AGREE           = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeStaticText[`name == "상품, 가격, 할인 정보, 유의 사항 등을 확인하였으며 구매에 동의합니다. (필수)"`]')
    PAYMENT_BTN             = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeButton[`name == "결제"`]') 
    PAYMENT_COMPLETE        = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeStaticText[`name == "결제가 완료되었습니다."`]')
    #MOVE_TO_ORDERLIST      = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeButton[`name == "구매 목록으로 이동"`]')
    MOVE_TO_GENREHOME       = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeButton[`name == "홈으로 이동"`]')

class AOS_MyLocators:
    MY_TITLE                = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("MY").instance(0)')
    CHARGE_RIDI_CASH        = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("리디캐시 충전")')
    CHARGE_RIDI_CASH_TITLE  = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("캐시충전")')
    MY_RIDI_CASH            = (AppiumBy.ID, 'com.initialcoms.ridi:id/value')
    CHARGE_HISTORY          = (AppiumBy.ID, 'com.initialcoms.ridi:id/history_button')
    CHARGE_TIER_FIRST     = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("₩1,200")')
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
