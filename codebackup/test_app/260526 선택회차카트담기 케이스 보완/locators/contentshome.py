from selenium.webdriver.common.by import By
from appium.webdriver.common.appiumby import AppiumBy

class AOS_ContentshomeLocators:
    #작품홈 상단영역
    ALL_CONTENTS_TITLE      = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("두 명의 상속인")')
    ADULT_CONTENTS_TITLE    = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("꽃은 밤을 걷는다")')
    CART_CONTENTS_TITLE     = (AppiumBy.ANDROID_UIAUTOMATOR,  'new UiSelector().text("고깔모자의 아틀리에")')

    #작품홈 회차앵커탭
    CONTENTS_EPISODE_TAB      = (AppiumBy.ACCESSIBILITY_ID, '회차')
    CONTENTS_EPISODE_SORT     = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("회차순")')
    CONTENTS_WATCHING_SORT    = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("보던순")')
    SELECTBUY_CART_BTN        = (AppiumBy.ACCESSIBILITY_ID, '선택 구매, /, 카트 담기')
    SELECTBUY_CART_TITLE      = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("고깔모자의 아틀리에 총 15권")')
    
    CONTENTS_EPISODE_FIRST      = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("1화")')
    CONTENTS_EPISODE_ANY        = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textMatches(".*[화권].*").instance(0)')
    CONTENTS_EPISODE_DOWNLOAD   = (AppiumBy.XPATH, '(//android.view.ViewGroup[@resource-id="downloadButton"])[1]/android.widget.ImageView')
    RENT_OWNERSHIP_LABEL        = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("ownershipLabel")')
    OWN_OWNERSHIP_LABEL         = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("ownershipLabel").text("소장")')

    ALL_CONTENTS_THUMBNAIL_FIRST  = (AppiumBy.XPATH, '//android.view.ViewGroup[@content-desc="0두 명의 상속인 1화, 0두 명의 상속인 1화, 2022.04.14, 18.1MB"]/android.view.ViewGroup')
    ALL_CONTENTS_THUMBNAIL_SECOND = (AppiumBy.XPATH, '//android.view.ViewGroup[@content-desc="0두 명의 상속인 2화, 0두 명의 상속인 2화, 2022.04.14, 19.6MB"]/android.view.ViewGroup')
    EPISODE_TITLE_BEFORE_DOWNLOAD = (AppiumBy.XPATH,
    '(//android.view.ViewGroup[@resource-id="downloadButton"])[1]/preceding-sibling::android.view.ViewGroup[@content-desc][1]/android.widget.TextView[1]')

    #총 회차목록
    CONTENTS_EPISODE_ALL = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textMatches("총 \\\\d+(화|권).*")')

    #작품홈 선택구매 및 카트담기 화면
    SELECTBUY_CART_SORT_EPISODE     = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("회차순")')
    SELECTBUY_CART_SORT_LAST        = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("최신순")')
    SELECTBUY_CART_RENT_TAB         = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("대여")')
    SELECTBUY_CART_OWN_TAB          = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("소장")')
    SELECTBUY_CART_RENT_ITEM        = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("0고깔모자의 아틀리에 1권, 0고깔모자의 아틀리에 1권, 2019.04.18, 214쪽, 328.7MB")')
    SELECTBUY_CART_OWN_ITEM         = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("고깔모자의 아틀리에 1권, 고깔모자의 아틀리에 1권, 2019.04.18, 214쪽, 328.7MB, 소장 3,800원 3,420원")')
    SELECTBUY_CART_OWN_LAST_ITEM    = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("고깔모자의 아틀리에 15권, 고깔모자의 아틀리에 15권, 2026.05.01, 198쪽, 325.2MB, 소장 3,800원 3,420원")')
    SELECTBUY_CART_FIRST_TOGGLE     = (AppiumBy.XPATH,'(//android.view.ViewGroup[contains(@content-desc, "고깔모자의 아틀리에") and contains(@content-desc, "소장 3,800원")]/android.widget.ImageView[@enabled="true"])[1]')    
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
    CONTENTS_WATCHING_SORT  = (AppiumBy.ACCESSIBILITY_ID, '보던순')
    SELECTBUY_CART_BTN      = (AppiumBy.NAME, '선택 구매 / 카트 담기')
    SELECTBUY_CART_TITLE    = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeStaticText[`name == "고깔모자의 아틀리에 총 15권"`]')

    CONTENTS_EPISODE_FIRST          = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "1화"`][1]')
    CONTENTS_EPISODE_ANY            = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "화" OR name CONTAINS "권"`][1]')
    CONTENTS_EPISODE_DOWNLOAD       = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name == "downloadButton"`][1]')
    OWNERSHIP_LABEL                 = (AppiumBy.NAME, 'ownershipLabel')

    ALL_CONTENTS_THUMBNAIL_FIRST  = (AppiumBy.XPATH, '(//XCUIElementTypeOther[@name="두 명의 상속인 1화 2022.04.14, 18.1MB"])[3]')
    ALL_CONTENTS_THUMBNAIL_SECOND = (AppiumBy.XPATH, '(//XCUIElementTypeOther[@name="두 명의 상속인 2화 2022.04.14, 19.6MB"])[3]')
    EPISODE_TITLE_BEFORE_DOWNLOAD = (AppiumBy.XPATH, '(//XCUIElementTypeOther[@name="downloadButton"])[1]/../../XCUIElementTypeOther[1]')
    
    #총 회차목록
    CONTENTS_EPISODE_ALL = (AppiumBy.IOS_PREDICATE, 'type == "XCUIElementTypeOther" AND name MATCHES "총 \\\\d+(화|권)"')

    #작품홈 선택구매 및 카트담기 화면
    SELECTBUY_CART_SORT_EPISODE  = (AppiumBy.XPATH, '(//XCUIElementTypeOther[@name="회차순"])[2]')
    SELECTBUY_CART_SORT_LAST     = (AppiumBy.XPATH, '(//XCUIElementTypeOther[@name="최신순"])[2]')
    SELECTBUY_CART_RENT_TAB      = (AppiumBy.NAME, '대여 대여')
    SELECTBUY_CART_OWN_TAB       = (AppiumBy.NAME, '소장 소장')
    SELECTBUY_CART_RENT_ITEM     = (AppiumBy.XPATH, '(//XCUIElementTypeOther[@name="고깔모자의 아틀리에 1권 2019.04.18, 214쪽, 328.7MB"])[3]')
    SELECTBUY_CART_OWN_ITEM      = (AppiumBy.XPATH, '(//XCUIElementTypeOther[@name="고깔모자의 아틀리에 1권 2019.04.18, 214쪽, 328.7MB 소장 3,800원 3,420원"])[3]')
    SELECTBUY_CART_OWN_LAST_ITEM = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "고깔모자의 아틀리에" AND name CONTAINS "소장 3,800원" AND NOT name ENDSWITH "소장"`]')
    CART_BTN                     = (AppiumBy.NAME, '카트')
    CART_TOAST                   = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name == "카트에 작품을 담았습니다. 보기"`][2]')

    #결제팝업
    PAY_CASH_BTN = (AppiumBy.NAME, '캐시로 결제')
    PAY_RENT_TAB = (AppiumBy.NAME, '대여')
    PAY_RENT_BTN = (AppiumBy.NAME, '대여로 결제')
    PAY_OWN_BTN  = (AppiumBy.NAME, '소장으로 결제')