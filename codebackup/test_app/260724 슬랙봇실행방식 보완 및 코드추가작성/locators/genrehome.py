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

    #BL 서브탭 섹션 (아래 섹션들도 화면 전체가 하나의 XCUIElementTypeOther 블롭에 뭉쳐서
    #노출됨 - 다른 섹션들과 동일한 이유로 CONTAINS 형태로 블롭을 조회한다)
    SECTION_BL_KEYWORD_SEARCH = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "BL 키워드 검색"`]')
    SECTION_BL_RANKING        = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "BL만화 실시간 랭킹"`]')
    SECTION_BL_BEST           = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "BL만화 베스트"`]')
    SECTION_BL_EVENT          = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "BL만화 e북 이벤트"`]')
    SECTION_BL_RIDI_EXCLUSIVE = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "리디에서만 볼 수 있는 BL만화"`]')
    SECTION_BL_NEW_ARRIVALS   = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name CONTAINS "BL만화 e북 신간"`]')


#웹툰 장르홈 (요소값은 추후 실기기 확인 후 보완 예정 - 우선 진입 확인용 최소 구성)
class AOS_WEBTOON_GENRE:
    MAIN_TAB                = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("웹툰")')
    SUBTAB_RECOMMEND        = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("추천")')
    # 실기기 미확인 - 만화 카테고리("만화 카테고리")와 동일한 문구 패턴으로 추정한 값.
    # 실기기 확인 후 실제 문구로 보완 필요.
    CATEGORY_TITLE          = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("웹툰 카테고리")')
    CATEGORY_TOPMENU_WEBTOON    = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("웹툰")')
    CATEGORY_TOPMENU_BL_WEBTOON = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("BL 웹툰")')
    # 퀵메뉴: 사용자가 확인해준 4개만 우선 반영(전체 11개 중 나머지 7개는 실기기 확인 필요)
    MONTHLY_NEW_QUICK       = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("이달의 신작")')
    EVENT_QUICK             = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("이벤트")')
    RIDIONLY_QUICK          = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("리디온리")')
    RIDAMU_QUICK            = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("리다무")')
    # 추천 탭 섹션 - 실기기 미확인, 사용자가 알려준 명칭 기준 textContains로 안전 매칭
    # (정확한 문구/공백은 실기기 확인 후 보완 필요)
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


class IOS_WEBTOON_GENRE:
    MAIN_TAB                = (AppiumBy.ACCESSIBILITY_ID, '웹툰 웹툰')
    SUBTAB_RECOMMEND        = (AppiumBy.ACCESSIBILITY_ID, '추천 추천')
    # 실기기 미확인 - 추정값(위 AOS_WEBTOON_GENRE.CATEGORY_TITLE과 동일 사유)
    CATEGORY_TITLE          = (AppiumBy.ACCESSIBILITY_ID, '웹툰 카테고리')
    CATEGORY_TOPMENU_WEBTOON    = (AppiumBy.ACCESSIBILITY_ID, '웹툰')
    CATEGORY_TOPMENU_BL_WEBTOON = (AppiumBy.ACCESSIBILITY_ID, 'BL 웹툰')
    # 퀵메뉴: 사용자가 확인해준 4개만 우선 반영(전체 11개 중 나머지 7개는 실기기 확인 필요)
    MONTHLY_NEW_QUICK       = (AppiumBy.ACCESSIBILITY_ID, '이달의 신작')
    EVENT_QUICK             = (AppiumBy.ACCESSIBILITY_ID, '이벤트')
    RIDIONLY_QUICK          = (AppiumBy.ACCESSIBILITY_ID, '리디온리')
    RIDAMU_QUICK            = (AppiumBy.ACCESSIBILITY_ID, '리다무')
    # 추천 탭 섹션 - 실기기 미확인, 사용자가 알려준 명칭 기준 CONTAINS로 안전 매칭
    # (정확한 문구/공백은 실기기 확인 후 보완 필요)
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


#웹소설 장르홈 (요소값은 추후 실기기 확인 후 보완 예정 - 우선 진입 확인용 최소 구성)
class AOS_WEBNOVEL_GENRE:
    SUBTAB_RECOMMEND        = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("추천")')
    # 실기기 미확인 - 만화 카테고리("만화 카테고리")와 동일한 문구 패턴으로 추정한 값.
    # 실기기 확인 후 실제 문구로 보완 필요.
    CATEGORY_TITLE                    = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("웹소설 카테고리")')
    CATEGORY_TOPMENU_ROMANCE_NOVEL    = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("로맨스 웹소설")')
    CATEGORY_TOPMENU_ROMANCE_EBOOK    = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("로맨스 e북")')
    CATEGORY_TOPMENU_FANTASY_ROMANCE_NOVEL = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("로판 웹소설")')
    CATEGORY_TOPMENU_FANTASY_ROMANCE_EBOOK  = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("로판 e북")')
    CATEGORY_TOPMENU_FANTASY_NOVEL    = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("판타지 웹소설")')
    CATEGORY_TOPMENU_FANTASY_EBOOK    = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("판타지 e북")')
    CATEGORY_TOPMENU_BL_NOVEL         = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("BL 웹소설")')
    CATEGORY_TOPMENU_BL_EBOOK         = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("BL 소설 e북")')


class IOS_WEBNOVEL_GENRE:
    SUBTAB_RECOMMEND        = (AppiumBy.ACCESSIBILITY_ID, '추천 추천')
    # 실기기 미확인 - 추정값(위 AOS_WEBNOVEL_GENRE.CATEGORY_TITLE과 동일 사유)
    CATEGORY_TITLE                    = (AppiumBy.ACCESSIBILITY_ID, '웹소설 카테고리')
    CATEGORY_TOPMENU_ROMANCE_NOVEL    = (AppiumBy.ACCESSIBILITY_ID, '로맨스 웹소설')
    CATEGORY_TOPMENU_ROMANCE_EBOOK    = (AppiumBy.ACCESSIBILITY_ID, '로맨스 e북')
    CATEGORY_TOPMENU_FANTASY_ROMANCE_NOVEL = (AppiumBy.ACCESSIBILITY_ID, '로판 웹소설')
    CATEGORY_TOPMENU_FANTASY_ROMANCE_EBOOK  = (AppiumBy.ACCESSIBILITY_ID, '로판 e북')
    CATEGORY_TOPMENU_FANTASY_NOVEL    = (AppiumBy.ACCESSIBILITY_ID, '판타지 웹소설')
    CATEGORY_TOPMENU_FANTASY_EBOOK    = (AppiumBy.ACCESSIBILITY_ID, '판타지 e북')
    CATEGORY_TOPMENU_BL_NOVEL         = (AppiumBy.ACCESSIBILITY_ID, 'BL 웹소설')
    CATEGORY_TOPMENU_BL_EBOOK         = (AppiumBy.ACCESSIBILITY_ID, 'BL 소설 e북')


#일반도서 장르홈 (요소값은 추후 실기기 확인 후 보완 예정 - 우선 진입 확인용 최소 구성)
class AOS_GENERALBOOK_GENRE:
    SUBTAB_RECOMMEND        = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("추천")')
    # 실기기 미확인 - 만화 카테고리("만화 카테고리")와 동일한 문구 패턴으로 추정한 값.
    # 실기기 확인 후 실제 문구로 보완 필요.
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


class IOS_GENERALBOOK_GENRE:
    SUBTAB_RECOMMEND        = (AppiumBy.ACCESSIBILITY_ID, '추천 추천')
    # 실기기 미확인 - 추정값(위 AOS_GENERALBOOK_GENRE.CATEGORY_TITLE과 동일 사유)
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