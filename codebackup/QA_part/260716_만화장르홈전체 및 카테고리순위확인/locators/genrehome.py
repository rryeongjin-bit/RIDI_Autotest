from selenium.webdriver.common.by import By
from appium.webdriver.common.appiumby import AppiumBy

class AOS_GenrehomeLocators:
    WEBTOON_RECOMMEND_TAB         = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("웹툰")')
    COMIC_RECOMMEND_TAB           = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("만화")')
    #CART_ICON          

class IOS_GenrehomeLocators:    
    WEBTOON_NEW_QUICK   = (AppiumBy.NAME, '이달의 신작') 
    COMIC_NEW_QUICK     = (AppiumBy.NAME, '무료')
    #CART_ICON


class AOS_COMIC_GENRE:
    MAIN_TAB                = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("만화")')
    SUBTAB_RECOMMEND        = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("추천")')
    SUBTAB_BEST             = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("베스트")')
    SUBTAB_NEW              = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("신작")')
    SUBTAB_BL               = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("BL")')

    #빅배너
    BIG_BANNER              = (AppiumBy.XPATH, '//android.view.ViewGroup[@clickable="true" and @content-desc!=""]')

    #퀵메뉴
    FREE_QUICK              = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("무료")')
    EVENT_QUICK             = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("이벤트")')
    LOWEST_PRICE_QUICK      = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("최저가 세트")')
    MONTHLY_CALENDER_QUICK  = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("월간 캘린더")')
    RIDIONLY_QUICK          = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("리디온리")')

    #섹션별
    SECTION_SIMILAR_RECENT  = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("방금")')
    SECTION_READING_NOW     = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("읽고 있는")')
    SECTION_TODAY_DISCOVERY = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("오늘, 리디의 발견")')
    SECTION_AI_PURCHASE     = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("구매이력")')
    SECTION_RIDI_ONLY       = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("오직 리디!")')
    SECTION_NEW_ARRIVALS    = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("새로 나온 작품")')
    SECTION_SPOTLIGHT       = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("이 작품을 주목!")')
    SECTION_BEST            = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("만화 베스트")')
    SECTION_SIMILAR_WORK    = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("비슷한")')
    SECTION_KEYWORD_SEARCH  = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("키워드 검색")')
    SECTION_EVENT           = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("이벤트")')
    SECTION_SEASONAL        = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("애니 원작")')
    SECTION_SPECIAL_SET     = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("특가 세트")')
    SECTION_FREE_PREVIEW    = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("앞권 무료로 맛보기!")')
    SECTION_RIDI_EXCLUSIVE  = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("리디에서만")')
    SECTION_MONTHLY_NEW     = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("주목 신작")')
    SECTION_HALF_YEAR_BEST  = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("상반기 베스트 만화")')
    SECTION_SPORTS          = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("스포츠 만화")')
    SECTION_HUMANITY        = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("그날 인류는 떠올렸다")')
    SECTION_FREE_FIRST_VOL  = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("추억의 만화")')
    SECTION_RIDI_GUIDE      = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("제대로 즐기는")')
    SECTION_HALL_OF_FAME    = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("명예의 전당")')
    SECTION_AWARD           = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("만화 대상")')
    SECTION_EVENT_MORE      = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("이벤트 더 보기")')
    SECTION_AI_TASTE        = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("취향 저격")')

    #섹션더보기 및 푸터
    MORE_BTN                = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("더보기")')
    FOOTER                  = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("리디(주)")')

    #만화 카테고리
    CATEGORY_TITLE              = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("만화 카테고리")')
    CATEGORY_TOPMENU_EBOOK      = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("만화 e북")')
    CATEGORY_TOPMENU_SERIAL     = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("만화 연재")')
    CATEGORY_TOPMENU_BL_EBOOK   = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("BL 만화 e북")')
    CATEGORY_TOPMENU_LIGHTNOVEL = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("라이트노벨")')


class IOS_COMIC_GENRE:
    MAIN_TAB                = (AppiumBy.ACCESSIBILITY_ID, '만화')
    SUBTAB_RECOMMEND        = (AppiumBy.ACCESSIBILITY_ID, '추천 추천')
    SUBTAB_BEST             = (AppiumBy.ACCESSIBILITY_ID, '베스트 베스트')
    SUBTAB_NEW              = (AppiumBy.ACCESSIBILITY_ID, '신작 신작')
    SUBTAB_BL               = (AppiumBy.ACCESSIBILITY_ID, 'BL BL')

    #빅배너
    BIG_BANNER              = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name != ""`]')

    #퀵메뉴
    FREE_QUICK              = (AppiumBy.ACCESSIBILITY_ID, '무료')
    EVENT_QUICK             = (AppiumBy.ACCESSIBILITY_ID, '이벤트')
    LOWEST_PRICE_QUICK      = (AppiumBy.ACCESSIBILITY_ID, '최저가 세트')
    MONTHLY_CALENDER_QUICK  = (AppiumBy.ACCESSIBILITY_ID, '월간 캘린더')
    RIDIONLY_QUICK          = (AppiumBy.ACCESSIBILITY_ID, '리디온리')

    #섹션별
    # iOS는 이 영역 텍스트들이 개별 StaticText가 아니라 XCUIElementTypeOther 하나에
    # 화면 텍스트 전체가 이어붙여진 채로 노출됨 (SwiftUI 접근성 트리 병합 추정)
    SECTION_SIMILAR_RECENT  = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "방금"`]')
    SECTION_READING_NOW     = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "읽고 있는"`]')
    SECTION_TODAY_DISCOVERY = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "오늘, 리디의 발견"`]')
    SECTION_AI_PURCHASE     = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "구매이력"`]')
    # 아래 섹션들도 방금본작품/지금많이/오늘발견/구매이력과 동일하게 하나의 XCUIElementTypeOther
    # 블롭에 뭉쳐서 노출됨이 실기기(Appium MCP)로 확인됨 (개별 StaticText/접근성ID 요소 없음).
    # ACCESSIBILITY_ID 정확일치나 XCUIElementTypeStaticText 지정은 어떤 요소도 찾지 못해
    # 반드시 XCUIElementTypeOther CONTAINS 형태로 블롭을 조회해야 한다.
    SECTION_RIDI_ONLY       = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "오직 리디"`]')
    SECTION_NEW_ARRIVALS    = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "새로 나온 작품"`]')
    SECTION_SPOTLIGHT       = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "이 작품을 주목"`]')
    SECTION_BEST            = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "만화 베스트"`]')
    SECTION_SIMILAR_WORK    = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "비슷한"`]')
    SECTION_KEYWORD_SEARCH  = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "키워드 검색"`]')
    SECTION_EVENT           = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "이벤트"`]')
    SECTION_SEASONAL        = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "애니 원작"`]')
    SECTION_SPECIAL_SET     = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "특가 세트"`]')
    SECTION_FREE_PREVIEW    = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "앞권 무료로 맛보기"`]')
    SECTION_RIDI_EXCLUSIVE  = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "리디에서만"`]')
    SECTION_MONTHLY_NEW     = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "주목 신작"`]')
    SECTION_HALF_YEAR_BEST  = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "상반기 베스트 만화"`]')
    SECTION_SPORTS          = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "스포츠 만화"`]')
    SECTION_HUMANITY        = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "그날 인류는 떠올렸다"`]')
    SECTION_FREE_FIRST_VOL  = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "추억의 만화"`]')
    SECTION_RIDI_GUIDE      = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "제대로 즐기는"`]')
    SECTION_HALL_OF_FAME    = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "명예의 전당"`]')
    SECTION_AWARD           = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "만화 대상"`]')
    SECTION_EVENT_MORE      = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "이벤트 더 보기"`]')
    SECTION_AI_TASTE        = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "취향 저격"`]')

    #섹션더보기 및 푸터
    MORE_BTN                = (AppiumBy.ACCESSIBILITY_ID, '더보기')
    FOOTER                  = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeStaticText[`name CONTAINS "리디(주)"`]')

    #만화 카테고리
    CATEGORY_TITLE              = (AppiumBy.ACCESSIBILITY_ID, '만화 카테고리')
    CATEGORY_TOPMENU_EBOOK      = (AppiumBy.ACCESSIBILITY_ID, '만화 e북')
    CATEGORY_TOPMENU_SERIAL     = (AppiumBy.ACCESSIBILITY_ID, '만화 연재')
    CATEGORY_TOPMENU_BL_EBOOK   = (AppiumBy.ACCESSIBILITY_ID, 'BL 만화 e북')
    CATEGORY_TOPMENU_LIGHTNOVEL = (AppiumBy.ACCESSIBILITY_ID, '라이트노벨')