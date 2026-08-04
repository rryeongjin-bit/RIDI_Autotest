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

    #BL 서브탭 섹션
    SECTION_BL_KEYWORD_SEARCH = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("BL 키워드 검색")')
    SECTION_BL_RANKING        = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("BL만화 실시간 랭킹")')
    SECTION_BL_BEST           = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("BL만화 베스트")')
    SECTION_BL_EVENT          = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("BL만화 e북 이벤트")')
    SECTION_BL_RIDI_EXCLUSIVE = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("리디에서만 볼 수 있는 BL만화")')
    SECTION_BL_NEW_ARRIVALS   = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("BL만화 e북 신간")')


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
    SECTION_SIMILAR_RECENT  = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "방금"`]')
    SECTION_READING_NOW     = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "읽고 있는"`]')
    SECTION_TODAY_DISCOVERY = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "오늘, 리디의 발견"`]')
    SECTION_AI_PURCHASE     = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "구매이력"`]')
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
    SECTION_BL_KEYWORD_SEARCH = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "BL 키워드 검색"`]')
    SECTION_BL_RANKING        = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "BL만화 실시간 랭킹"`]')
    SECTION_BL_BEST           = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "BL만화 베스트"`]')
    SECTION_BL_EVENT          = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "BL만화 e북 이벤트"`]')
    SECTION_BL_RIDI_EXCLUSIVE = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "리디에서만 볼 수 있는 BL만화"`]')
    SECTION_BL_NEW_ARRIVALS   = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "BL만화 e북 신간"`]')

class AOS_WEBTOON_GENRE:
    MAIN_TAB                = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("웹툰")')
    SUBTAB_RECOMMEND        = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("추천")')
    SUBTAB_ROMANCE          = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("로맨스")')
    SUBTAB_BL               = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("BL")')
    SUBTAB_FANTASY_SF       = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("판타지/SF")')
   
    CATEGORY_TITLE          = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("웹툰 카테고리")')
    CATEGORY_TOPMENU_WEBTOON    = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("웹툰")')
    CATEGORY_TOPMENU_BL_WEBTOON = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("BL 웹툰")')
    MONTHLY_NEW_QUICK       = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("이달의 신작")')
    EVENT_QUICK             = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("이벤트")')
    RIDIONLY_QUICK          = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("리디온리")')
    RIDAMU_QUICK            = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("리다무")')

    SECTION_SIMILAR_RECENT  = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("방금 본 작품과 비슷한")')
    SECTION_REALTIME_RANKING = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("실시간 랭킹")')
    SECTION_WEEKDAY_WEBTOON = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("요일별")')
    SECTION_WAIT_FREE       = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("기다리면 무료")')
    SECTION_TODAY_DISCOVERY = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("리디의 발견")')
    SECTION_AI_PURCHASE     = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("구매이력")')
    SECTION_KEYWORD_SEARCH  = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("키워드 검색")')
    SECTION_BEST            = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("웹툰 베스트")')
    SECTION_RIDI_EXCLUSIVE  = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("리디에서만")')
    SECTION_NEW_ARRIVALS    = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("새로 나온")')
    SECTION_AI_TASTE        = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("취향 저격")')

    SECTION_ROMANCE_BEST    = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("로맨스 베스트")')
    SECTION_RIDI_ONLY_EXCLAIM = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("오직 리디에서만!")')

    SECTION_BL_BEST           = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("BL웹툰 베스트")')
    SECTION_RIDI_ONLY_NEW_COLLECTION = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("RIDI ONLY 신작 모음")')
    SECTION_HOW_ABOUT_THIS    = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("이 작품 어때요")')

    SECTION_FANTASY_BEST      = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("판타지 베스트")')
    SECTION_RIDI_ONLY_FANTASY = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("RIDI ONLY 판타지")')
    SECTION_HOW_ABOUT_FANTASY = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("이 판타지 어때요?")')
 
    BIG_BANNER              = (AppiumBy.XPATH, '//android.view.ViewGroup[@clickable="true" and @content-desc!=""]')
    FOOTER                  = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("리디(주)")')


class IOS_WEBTOON_GENRE:
    MAIN_TAB                = (AppiumBy.ACCESSIBILITY_ID, '웹툰 웹툰')
    SUBTAB_RECOMMEND        = (AppiumBy.ACCESSIBILITY_ID, '추천 추천')
    SUBTAB_ROMANCE          = (AppiumBy.ACCESSIBILITY_ID, '로맨스 로맨스')
    SUBTAB_BL               = (AppiumBy.ACCESSIBILITY_ID, 'BL BL')
    SUBTAB_FANTASY_SF       = (AppiumBy.ACCESSIBILITY_ID, '판타지/SF 판타지/SF')

    CATEGORY_TITLE          = (AppiumBy.ACCESSIBILITY_ID, '웹툰 카테고리')
    CATEGORY_TOPMENU_WEBTOON    = (AppiumBy.ACCESSIBILITY_ID, '웹툰')
    CATEGORY_TOPMENU_BL_WEBTOON = (AppiumBy.ACCESSIBILITY_ID, 'BL 웹툰')
    
    MONTHLY_NEW_QUICK       = (AppiumBy.ACCESSIBILITY_ID, '이달의 신작')
    EVENT_QUICK             = (AppiumBy.ACCESSIBILITY_ID, '이벤트')
    RIDIONLY_QUICK          = (AppiumBy.ACCESSIBILITY_ID, '리디온리')
    RIDAMU_QUICK            = (AppiumBy.ACCESSIBILITY_ID, '리다무')
 
    SECTION_SIMILAR_RECENT  = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "방금 본 작품과 비슷한"`]')
    SECTION_REALTIME_RANKING = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "실시간 랭킹"`]')
    SECTION_WEEKDAY_WEBTOON = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "요일별"`]')
    SECTION_WAIT_FREE       = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "기다리면 무료"`]')
    SECTION_TODAY_DISCOVERY = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "리디의 발견"`]')
    SECTION_AI_PURCHASE     = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "구매이력"`]')
    SECTION_KEYWORD_SEARCH  = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "키워드 검색"`]')
    SECTION_BEST            = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "웹툰 베스트"`]')
    SECTION_RIDI_EXCLUSIVE  = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "리디에서만"`]')
    SECTION_NEW_ARRIVALS    = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "새로 나온"`]')
    SECTION_AI_TASTE        = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "취향 저격"`]')

    SECTION_ROMANCE_BEST    = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "로맨스 베스트"`]')
    SECTION_RIDI_ONLY_EXCLAIM = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "오직 리디에서만!"`]')

    SECTION_BL_BEST           = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "BL웹툰 베스트"`]')
    SECTION_RIDI_ONLY_NEW_COLLECTION = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "RIDI ONLY 신작 모음"`]')
    SECTION_HOW_ABOUT_THIS    = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "이 작품 어때요"`]')
 
    SECTION_FANTASY_BEST      = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "판타지 베스트"`]')
    SECTION_RIDI_ONLY_FANTASY = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "RIDI ONLY 판타지"`]')
    SECTION_HOW_ABOUT_FANTASY = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "이 판타지 어때요?"`]')

    BIG_BANNER              = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name != ""`]')
    FOOTER                  = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeStaticText[`name CONTAINS "리디(주)"`]')


class AOS_WEBNOVEL_GENRE:
    SUBTAB_RECOMMEND        = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("추천")')

    CATEGORY_TITLE                    = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("웹소설 카테고리")')
    CATEGORY_TOPMENU_ROMANCE_NOVEL    = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("로맨스 웹소설")')
    CATEGORY_TOPMENU_ROMANCE_EBOOK    = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("로맨스 e북")')
    CATEGORY_TOPMENU_FANTASY_ROMANCE_NOVEL = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("로판 웹소설")')
    CATEGORY_TOPMENU_FANTASY_ROMANCE_EBOOK  = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("로판 e북")')
    CATEGORY_TOPMENU_FANTASY_NOVEL    = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("판타지 웹소설")')
    CATEGORY_TOPMENU_FANTASY_EBOOK    = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("판타지 e북")')
    CATEGORY_TOPMENU_BL_NOVEL         = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("BL 웹소설")')
    CATEGORY_TOPMENU_BL_EBOOK         = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("BL 소설 e북")')

    SUBTAB_ROMANCE          = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("로맨스")')
    SUBTAB_ROMANCE_FANTASY  = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("로판")')
    SUBTAB_BL               = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("BL")')
    SUBTAB_FANTASY          = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("판타지")')

    BIG_BANNER              = (AppiumBy.XPATH, '//android.view.ViewGroup[@clickable="true" and @content-desc!=""]')
    FOOTER                  = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("리디(주)")')

    NEW_QUICK               = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("신작")')
    BEST_QUICK              = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("베스트")')
    EVENT_QUICK             = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("이벤트")')
    CALENDAR_QUICK          = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("캘린더")')

    SECTION_SIMILAR_RECENT  = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("방금 본 작품과 비슷한")')
    SECTION_MY_TASTE_NEW    = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("내 취향 추천 신작")')
    SECTION_REALTIME_RANKING = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("실시간 랭킹")')
    SECTION_NEW_ARRIVALS    = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("새로 나온")')
    SECTION_AI_PURCHASE     = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("구매이력")')
    SECTION_ONGOING_EVENT   = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("진행중인 이벤트")')
    SECTION_AI_TASTE        = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("취향 저격")')


class IOS_WEBNOVEL_GENRE:
    # 서브탭 접근성 id는 라벨이 한 번만 들어간다(2026-08-03 실기기 실측).
    # 기존에는 '추천 추천'처럼 라벨을 두 번 반복한 값이 등록돼 있어 5개 전부 미검출로
    # 11초씩 타임아웃까지 갔다(is_subtab_visible만 이 값을 쓰고, 웹소설 iOS click_subtab은
    # "딥링크로 이미 선택됨 - 탭 생략"이라 클릭 경로는 이 로케이터를 안 써서 그동안 드러나지
    # 않았다). 조회 결과: '추천'/'로맨스'/'로판'/'BL'/'판타지' 각 1개, 중복형은 모두 0개.
    # 화면 노출 순서는 추천 → 로맨스 → 로판 → 판타지 → BL 이다.
    # 만화/웹툰은 장르별로 값이 다를 수 있어(웹툰은 탭 전환이 정상 동작 확인됨) 손대지 않는다.
    SUBTAB_RECOMMEND        = (AppiumBy.ACCESSIBILITY_ID, '추천')

    CATEGORY_TITLE                    = (AppiumBy.ACCESSIBILITY_ID, '웹소설 카테고리')
    CATEGORY_TOPMENU_ROMANCE_NOVEL    = (AppiumBy.ACCESSIBILITY_ID, '로맨스 웹소설')
    CATEGORY_TOPMENU_ROMANCE_EBOOK    = (AppiumBy.ACCESSIBILITY_ID, '로맨스 e북')
    CATEGORY_TOPMENU_FANTASY_ROMANCE_NOVEL = (AppiumBy.ACCESSIBILITY_ID, '로판 웹소설')
    CATEGORY_TOPMENU_FANTASY_ROMANCE_EBOOK  = (AppiumBy.ACCESSIBILITY_ID, '로판 e북')
    CATEGORY_TOPMENU_FANTASY_NOVEL    = (AppiumBy.ACCESSIBILITY_ID, '판타지 웹소설')
    CATEGORY_TOPMENU_FANTASY_EBOOK    = (AppiumBy.ACCESSIBILITY_ID, '판타지 e북')
    CATEGORY_TOPMENU_BL_NOVEL         = (AppiumBy.ACCESSIBILITY_ID, 'BL 웹소설')
    CATEGORY_TOPMENU_BL_EBOOK         = (AppiumBy.ACCESSIBILITY_ID, 'BL 소설 e북')

    SUBTAB_ROMANCE          = (AppiumBy.ACCESSIBILITY_ID, '로맨스')
    SUBTAB_ROMANCE_FANTASY  = (AppiumBy.ACCESSIBILITY_ID, '로판')
    SUBTAB_BL               = (AppiumBy.ACCESSIBILITY_ID, 'BL')
    SUBTAB_FANTASY          = (AppiumBy.ACCESSIBILITY_ID, '판타지')

    BIG_BANNER              = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "/"`]')
    FOOTER                  = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "리디(주)"`]')

    NEW_QUICK               = (AppiumBy.ACCESSIBILITY_ID, '신작')
    BEST_QUICK              = (AppiumBy.ACCESSIBILITY_ID, '베스트')
    EVENT_QUICK             = (AppiumBy.ACCESSIBILITY_ID, '이벤트')
    CALENDAR_QUICK          = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "캘린더"`]')

    SECTION_SIMILAR_RECENT  = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "방금 본 작품과 비슷한"`]')
    SECTION_MY_TASTE_NEW    = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "내 취향 추천 신작"`]')
    SECTION_REALTIME_RANKING = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "실시간 랭킹"`]')
    SECTION_NEW_ARRIVALS    = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "새로 나온"`]')
    SECTION_AI_PURCHASE     = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "구매이력"`]')
    SECTION_ONGOING_EVENT   = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "진행중인 이벤트"`]')
    SECTION_AI_TASTE        = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "취향 저격"`]')


class AOS_GENERALBOOK_GENRE:
    SUBTAB_RECOMMEND        = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("추천")')
    
    CATEGORY_TITLE                 = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("도서 카테고리")')
    CATEGORY_TOPMENU_NOVEL         = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("소설")')
    CATEGORY_TOPMENU_BUSINESS      = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("경영/경제")')
    CATEGORY_TOPMENU_HUMANITIES    = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("인문/사회/역사")')
    CATEGORY_TOPMENU_SELF_HELP     = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("자기계발")')
    CATEGORY_TOPMENU_ESSAY_POETRY  = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("에세이/시")')
    CATEGORY_TOPMENU_TRAVEL        = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("여행")')
    CATEGORY_TOPMENU_RELIGION      = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("종교")')
    CATEGORY_TOPMENU_FOREIGN_LANG  = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("외국어")')
    CATEGORY_TOPMENU_SCIENCE       = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("과학")')
    CATEGORY_TOPMENU_CAREER_EDU    = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("진로/교육/교재")')
    CATEGORY_TOPMENU_COMPUTER_IT   = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("컴퓨터/IT")')
    CATEGORY_TOPMENU_HEALTH_DIET   = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("건강/다이어트")')
    CATEGORY_TOPMENU_HOME_LIFE     = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("가정/생활")')
    CATEGORY_TOPMENU_KIDS_TEEN     = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("어린이/청소년")')
    CATEGORY_TOPMENU_FOREIGN_BOOK  = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("해외도서")')
    CATEGORY_TOPMENU_MAGAZINE      = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("잡지")')

    # ── 도서 장르홈 추천탭 (2026-08-03 AOS 에뮬레이터 실측 / logs/diag/aos_general_explore2.out) ──
    # 섹션 노출 순서와 더보기 유무를 페이지소스로 직접 확인했다. 더보기 x좌표는 전 섹션 공통
    # 939~1041(중심 990)이다. 아래 3개는 실측에서 함께 나왔지만 사용자가 지정한 검증 대상이
    # 아니라 로케이터만 남기지 않는다: "지금, 리디에서만! 선 출간 신작" /
    # "히가시노 게이고 작가 대표작" / "짧지만 강렬한 서사, 우주라이크소설"(기획성 섹션).
    # 도서 장르홈 빅배너는 다른 장르홈의 bannerViewPager가 아니라 topCarouselCover를 쓴다
    # (2026-08-03 실기기 실측: y 371~1401 ViewGroup id='topCarouselCover',
    #  그 위에 y 0~371 'topCarouselSafeArea'). 배너 영역에 텍스트 요소가 없어(이미지만)
    # 문구 수집 방식의 검증은 이 지면에 성립하지 않는다.
    BIG_BANNER              = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("com.initialcoms.ridi:id/topCarouselCover")')
    FOOTER                  = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("리디(주)")')

    # 퀵메뉴 - 실측 노출: 신간 / 북스 베스트 / 이벤트 / 리디온리 / 이달의 쿠폰 / 대여
    # (검증 대상은 사용자 지정 4개)
    # text(라벨) 대신 description을 쓴다 - 라벨 TextView는 clickable=false이고, 실제 터치
    # 대상은 그 부모 ViewGroup(content-desc에 메뉴명)이다(2026-08-03 실기기 실측:
    # TextView[627,1626][735,1663] clickable=false / 부모 ViewGroup[602,1446][759,1685]
    # desc='리디온리' clickable=true). 라벨을 누르면 아무 일도 일어나지 않아 "리디온리" 선택이
    # 장르홈에 그대로 머물렀다.
    NEW_QUICK               = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("신간")')
    BEST_QUICK              = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("북스 베스트")')
    EVENT_QUICK             = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("이벤트")')
    RIDIONLY_QUICK          = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("리디온리")')

    SECTION_SIMILAR_RECENT  = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("방금 본 작품과 비슷한")')
    SECTION_MOST_READ       = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("지금 많이 읽고 있는 작품")')
    SECTION_TODAY_DISCOVERY = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("오늘, 리디의 발견")')
    SECTION_AI_PURCHASE     = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("구매이력 기반 AI 추천")')
    SECTION_ONGOING_EVENT   = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("이벤트")')
    SECTION_BEST            = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("베스트")')
    SECTION_NEW_ARRIVALS    = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("새로 나온 작품")')
    SECTION_RIDI_ONLY_BOOK  = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("지금, 리디에서만 볼 수 있는 도서")')
    SECTION_AI_TASTE        = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("취향 저격")')


class IOS_GENERALBOOK_GENRE:
    # 서브탭은 라벨이 두 번 반복된 형태다(2026-08-04 실기기 실측: '추천 추천'/'기획전 기획전'/
    # '소설 소설'/'인문/사회/역사 인문/사회/역사'/'경영/경제 경영/경제'/'종교 종교'/
    # '자기계발 자기계발'). 웹소설만 단일 형태('추천')였고 도서는 중복형이라 장르별로 다르다.
    SUBTAB_RECOMMEND        = (AppiumBy.ACCESSIBILITY_ID, '추천 추천')

    # ── 도서 장르홈 추천탭 (2026-08-04 iOS 실기기 실측, 로그인 상태) ────────────────────
    # 이 지면도 만화/웹툰/웹소설과 같은 **블롭 구조**다 - 화면 전체 텍스트가 하나의
    # XCUIElementTypeOther(2203자)에 뭉쳐 노출된다. 섹션명을 exact accessibility id로 찾으면
    # 0~2건뿐이고 CONTAINS(Other)는 25~31건 전부 블롭 컨테이너라, 로케이터로 블롭을 찾은 뒤
    # 문자열을 잘라내는 기존 방식(IOS_SECTION_SWIPE_COUNT 결정론적 스크롤 + 좌표 탭)을 쓴다.
    BIG_BANNER              = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "/"`]')
    FOOTER                  = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "리디(주)"`]')

    # 퀵메뉴 - 4개 모두 exact accessibility id로 2건씩 잡힌다(실측).
    NEW_QUICK               = (AppiumBy.ACCESSIBILITY_ID, '신간')
    BEST_QUICK              = (AppiumBy.ACCESSIBILITY_ID, '북스 베스트')
    EVENT_QUICK             = (AppiumBy.ACCESSIBILITY_ID, '이벤트')
    RIDIONLY_QUICK          = (AppiumBy.ACCESSIBILITY_ID, '리디온리')

    # 섹션 - 블롭 요소를 찾기 위한 CONTAINS 조회. 계정ID 접두사가 붙는 두 섹션
    # ("4qa... 님의 구매이력 기반 AI 추천"/"님의 취향 저격 AI 추천")은 고정부로 잡는다.
    SECTION_SIMILAR_RECENT  = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "방금 본 작품과 비슷한"`]')
    SECTION_MOST_READ       = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "지금 많이 읽고 있는 작품"`]')
    SECTION_TODAY_DISCOVERY = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "오늘, 리디의 발견"`]')
    SECTION_AI_PURCHASE     = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "구매이력 기반 AI 추천"`]')
    SECTION_ONGOING_EVENT   = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "이벤트"`]')
    SECTION_BEST            = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "베스트"`]')
    SECTION_NEW_ARRIVALS    = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "새로 나온 작품"`]')
    SECTION_RIDI_ONLY_BOOK  = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "리디에서만 볼 수 있는 도서"`]')
    SECTION_AI_TASTE        = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "취향 저격"`]')

    CATEGORY_TITLE                 = (AppiumBy.ACCESSIBILITY_ID, '도서 카테고리')
    CATEGORY_TOPMENU_NOVEL         = (AppiumBy.ACCESSIBILITY_ID, '소설')
    CATEGORY_TOPMENU_BUSINESS      = (AppiumBy.ACCESSIBILITY_ID, '경영/경제')
    CATEGORY_TOPMENU_HUMANITIES    = (AppiumBy.ACCESSIBILITY_ID, '인문/사회/역사')
    CATEGORY_TOPMENU_SELF_HELP     = (AppiumBy.ACCESSIBILITY_ID, '자기계발')
    CATEGORY_TOPMENU_ESSAY_POETRY  = (AppiumBy.ACCESSIBILITY_ID, '에세이/시')
    CATEGORY_TOPMENU_TRAVEL        = (AppiumBy.ACCESSIBILITY_ID, '여행')
    CATEGORY_TOPMENU_RELIGION      = (AppiumBy.ACCESSIBILITY_ID, '종교')
    CATEGORY_TOPMENU_FOREIGN_LANG  = (AppiumBy.ACCESSIBILITY_ID, '외국어')
    CATEGORY_TOPMENU_SCIENCE       = (AppiumBy.ACCESSIBILITY_ID, '과학')
    CATEGORY_TOPMENU_CAREER_EDU    = (AppiumBy.ACCESSIBILITY_ID, '진로/교육/교재')
    CATEGORY_TOPMENU_COMPUTER_IT   = (AppiumBy.ACCESSIBILITY_ID, '컴퓨터/IT')
    CATEGORY_TOPMENU_HEALTH_DIET   = (AppiumBy.ACCESSIBILITY_ID, '건강/다이어트')
    CATEGORY_TOPMENU_HOME_LIFE     = (AppiumBy.ACCESSIBILITY_ID, '가정/생활')
    CATEGORY_TOPMENU_KIDS_TEEN     = (AppiumBy.ACCESSIBILITY_ID, '어린이/청소년')
    CATEGORY_TOPMENU_FOREIGN_BOOK  = (AppiumBy.ACCESSIBILITY_ID, '해외도서')
    CATEGORY_TOPMENU_MAGAZINE      = (AppiumBy.ACCESSIBILITY_ID, '잡지')