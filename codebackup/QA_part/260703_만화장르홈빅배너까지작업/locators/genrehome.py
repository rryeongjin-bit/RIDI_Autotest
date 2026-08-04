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
    # 고정 탭 4개만 정의 (나머지는 계정/상황에 따라 유동적 — iOS와 동일 정책)
    SUBTAB_RECOMMEND        = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("추천")')
    SUBTAB_BEST             = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("베스트")')
    SUBTAB_NEW              = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("신작")')
    SUBTAB_BL               = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("BL")')

    # ── 빅배너 (content-desc 있는 클릭 가능 ViewGroup, y 범위는 페이지 함수에서 필터) ──
    BIG_BANNER              = (AppiumBy.XPATH, '//android.view.ViewGroup[@clickable="true" and @content-desc!=""]')

    # ── 퀵메뉴 ───────────────────────────────────────────
    FREE_QUICK              = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("무료")')
    EVENT_QUICK             = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("이벤트")')
    CALENDER_QUICK          = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("월간캘린더")')
    RIDIONLY_QUICK          = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("리디온리")')
    NEW_QUICK               = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("신작")')
    BEST_QUICK              = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("베스트")')

    # ── 섹션 헤더 ─────────────────────────────────────────
    SECTION_SIMILAR_RECENT  = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("방금")')
    SECTION_READING_NOW     = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("지금읽고")')
    SECTION_TODAY_DISCOVERY = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("오늘, 리디의 발견")')
    SECTION_AI_PURCHASE     = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("구매이력")')
    SECTION_RIDI_ONLY       = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("오직리디")')
    SECTION_NEW_ARRIVALS    = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("새로나온 작품")')
    SECTION_SPOTLIGHT       = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("이 작품을 주목")')
    SECTION_BEST            = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("만화 베스트")')
    SECTION_SIMILAR_WORK    = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("비슷한")')
    SECTION_KEYWORD_SEARCH  = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("키워드 검색")')
    SECTION_EVENT           = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("이벤트")')
    SECTION_SEASONAL        = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("애니원작")')
    SECTION_SPECIAL_SET     = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("특가 세트")')
    SECTION_FREE_PREVIEW    = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("앞권 무료로 맛보기")')
    SECTION_RIDI_EXCLUSIVE  = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("리디에서만")')
    SECTION_MONTHLY_NEW     = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("주목 신작")')
    SECTION_SPORTS          = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("스포츠 만화")')
    SECTION_HUMANITY        = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("그냥 인류는 떠올랐다")')
    SECTION_FREE_FIRST_VOL  = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("추억의 만화")')
    SECTION_RIDI_GUIDE      = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("제대로 즐기는")')
    SECTION_HALL_OF_FAME    = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("명예의 전당")')
    SECTION_AWARD           = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("만화대상")')
    SECTION_EVENT_MORE      = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("이벤트 더보기")')
    SECTION_AI_TASTE        = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("취향 저격")')

    # ── 더보기 버튼 / 푸터 ────────────────────────────────
    MORE_BTN                = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("더보기")')
    FOOTER                  = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("(주)리디")')


class IOS_COMIC_GENRE:
    MAIN_TAB                = (AppiumBy.ACCESSIBILITY_ID, '만화')
    # iOS에서 서브탭 name 값이 텍스트 2회 반복됨 (e.g. '추천 추천')
    # 고정 탭 4개만 정의 (나머지는 계정/상황에 따라 유동적)
    SUBTAB_RECOMMEND        = (AppiumBy.ACCESSIBILITY_ID, '추천 추천')
    SUBTAB_BEST             = (AppiumBy.ACCESSIBILITY_ID, '베스트 베스트')
    SUBTAB_NEW              = (AppiumBy.ACCESSIBILITY_ID, '신작 신작')
    SUBTAB_BL               = (AppiumBy.ACCESSIBILITY_ID, 'BL BL')

    # ── 빅배너 ───────────────────────────────────────────
    # y=179, h=330 영역의 렌더링된 배너 아이템 (name이 있는 Other 요소)
    BIG_BANNER              = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name != ""`]')

    # ── 퀵메뉴 ───────────────────────────────────────────
    FREE_QUICK              = (AppiumBy.ACCESSIBILITY_ID, '무료')
    EVENT_QUICK             = (AppiumBy.ACCESSIBILITY_ID, '이벤트')
    CALENDER_QUICK          = (AppiumBy.ACCESSIBILITY_ID, '월간캘린더')
    RIDIONLY_QUICK          = (AppiumBy.ACCESSIBILITY_ID, '리디온리')
    NEW_QUICK               = (AppiumBy.ACCESSIBILITY_ID, '신작')
    BEST_QUICK              = (AppiumBy.ACCESSIBILITY_ID, '베스트')

    # ── 섹션 헤더 ─────────────────────────────────────────
    SECTION_SIMILAR_RECENT  = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeStaticText[`name CONTAINS "방금"`]')
    SECTION_READING_NOW     = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeStaticText[`name CONTAINS "지금읽고"`]')
    SECTION_TODAY_DISCOVERY = (AppiumBy.ACCESSIBILITY_ID, '오늘, 리디의 발견')
    SECTION_AI_PURCHASE     = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeStaticText[`name CONTAINS "구매이력"`]')
    SECTION_RIDI_ONLY       = (AppiumBy.ACCESSIBILITY_ID, '오직리디')
    SECTION_NEW_ARRIVALS    = (AppiumBy.ACCESSIBILITY_ID, '새로나온 작품')
    SECTION_SPOTLIGHT       = (AppiumBy.ACCESSIBILITY_ID, '이 작품을 주목')
    SECTION_BEST            = (AppiumBy.ACCESSIBILITY_ID, '만화 베스트')
    SECTION_SIMILAR_WORK    = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeStaticText[`name CONTAINS "비슷한"`]')
    SECTION_KEYWORD_SEARCH  = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeStaticText[`name CONTAINS "키워드 검색"`]')
    SECTION_EVENT           = (AppiumBy.ACCESSIBILITY_ID, '이벤트')
    SECTION_SEASONAL        = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeStaticText[`name CONTAINS "애니원작"`]')
    SECTION_SPECIAL_SET     = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeStaticText[`name CONTAINS "특가 세트"`]')
    SECTION_FREE_PREVIEW    = (AppiumBy.ACCESSIBILITY_ID, '앞권 무료로 맛보기')
    SECTION_RIDI_EXCLUSIVE  = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeStaticText[`name CONTAINS "리디에서만"`]')
    SECTION_MONTHLY_NEW     = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeStaticText[`name CONTAINS "주목 신작"`]')
    SECTION_SPORTS          = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeStaticText[`name CONTAINS "스포츠 만화"`]')
    SECTION_HUMANITY        = (AppiumBy.ACCESSIBILITY_ID, '그냥 인류는 떠올랐다')
    SECTION_FREE_FIRST_VOL  = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeStaticText[`name CONTAINS "추억의 만화"`]')
    SECTION_RIDI_GUIDE      = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeStaticText[`name CONTAINS "제대로 즐기는"`]')
    SECTION_HALL_OF_FAME    = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeStaticText[`name CONTAINS "명예의 전당"`]')
    SECTION_AWARD           = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeStaticText[`name CONTAINS "만화대상"`]')
    SECTION_EVENT_MORE      = (AppiumBy.ACCESSIBILITY_ID, '이벤트 더보기')
    SECTION_AI_TASTE        = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeStaticText[`name CONTAINS "취향 저격"`]')

    # ── 더보기 버튼 / 푸터 ────────────────────────────────
    MORE_BTN                = (AppiumBy.ACCESSIBILITY_ID, '더보기')
    FOOTER                  = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeStaticText[`name CONTAINS "(주)리디"`]')