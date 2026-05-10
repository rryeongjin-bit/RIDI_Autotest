from selenium.webdriver.common.by import By
from appium.webdriver.common.appiumby import AppiumBy

class CommonLocators:
    ALERT_ALLOW    = (By.ID, "com.android.permissioncontroller:id/permission_message")
    ALLOW_BTN      = (By.ID, "com.android.permissioncontroller:id/permission_allow_button")
    BRAZEPOPUP_CLOSE_AOS = (By.ID, "never_show_again")
    BRAZEPOPUP_CLOSE_IOS = (AppiumBy.ACCESSIBILITY_ID, "다시 보지 않기")
    #TWOFACTOR_ALERT_AOS = (AppiumBy.ANDROID_UIAUTOMATOR,"new UiSelector().text('2단계 인증으로 계정을 더 안전하게')")
    #TWOFACTOR_ALERT_CLOSE_AOS = (AppiumBy.ANDROID_UIAUTOMATOR, "new UiSelector().contentDescription('다시 보지 않기')")

class AOS_ReplacedeviceLocators:
    REPLACEDEVICE_LIST_TITLE   = (By.ID, "com.initialcoms.ridi:id/title") 
    REPLACEDEVICE_TOGGLE_FIRST = (By.XPATH, "(//android.widget.RadioButton[@resource-id='com.initialcoms.ridi:id/selection_radio_button'])[1]")
    REPLACEDEVICE_BTN          = (By.ID, "com.initialcoms.ridi:id/replace_button")

class IOS_ReplacedeviceLocators:
    REPLACEDEVICE_LIST_TITLE   = (By.XPATH, "//XCUIElementTypeStaticText[@name='기기 대체']")
    # REPLACEDEVICE_TOGGLE_FIRST 
    REPLACEDEVICE_BTN          = (By.XPATH, "//XCUIElementTypeButton[@name='대체하기']")

class AOS_LoginLocators:
    LOGIN_BTN    = (By.XPATH, "//android.widget.TextView[@resource-id='button-label']")
    ID_INPUT     = (By.XPATH, "//android.widget.EditText[@resource-id=':Rauqtm:']")
    PW_INPUT     = (By.XPATH, "//android.widget.EditText[@resource-id=':RauqtmH1:']")
    LOGIN_BUTTON = (By.XPATH, "//android.widget.Button[@text='로그인']") 
    LOGOUT_BNT   = (AppiumBy.ANDROID_UIAUTOMATOR, "new UiSelector().text('로그아웃')")

class IOS_LoginLocators:
    LOGIN_BTN    = (By.NAME, "로그인")
    ID_INPUT     = (By.CLASS_NAME, "XCUIElementTypeTextField")
    PW_INPUT     = (By.CLASS_NAME, "XCUIElementTypeSecureTextField")
    LOGIN_BUTTON = (By.XPATH, "//XCUIElementTypeButton[@name='로그인']") #로그인인앱웹뷰에 name = 로그인 2개있어서 xpath로 변경필요
    LOGOUT_BTN   = (AppiumBy.ACCESSIBILITY_ID, "로그아웃")

class GenrehomeLocators:
    WEBTOON_TAB_AOS = (By.XPATH, "//android.widget.TextView[@text='웹툰']")
    GENREHOME_TAB_IOS = (By.NAME, "웹툰 웹툰 만화 만화 웹소설 웹소설 도서 도서 셀렉트 셀렉트 추천 추천 로맨스 로맨스 BL BL 판타지/SF 판타지/SF 액션/무협 액션/무협 공포/추리 공포/추리 드라마 드라마 GL GL 말도 안 돼.\n내가? 쟤한테? <심술의 끝은 순정> 론칭, 최대 2,000P! ⓒ김감토,퀼라,이노/대원씨아이 5월 웹툰\n신작 캘린더 오픈! 이벤트와 신작 모두 모아 보기! 시즌 3! 단 7일,\n감상 전원 포인트백! <내게 빌어봐> 시즌 3로 컴백! ⓒ 리베냐 / ⓒ 아이린, 이서, 스튜디오 담 / 재담미디어, 디키 <파륜> 론칭!\n기간 한정 전원 포인트백 거래를 하자. 내 아이를 낳아 다오. ⓒ핫퍼지코믹스 잊을 수 없던,\n그 여름의 뜨거운 로맨스 <맴맴> 최신 화, 전원 포인트! ⓒ오은지,서단/재담 이렇게 미칠 것 같은\n감정이, 사랑인가? <상류 사회> 연참, 포인트백 & 8H 리다무! ⓒ스르륵코믹스 12H 리다무 &\n정주행 5천 리디포인트! <메리 사이코> 시즌 2 완결! ⓒ핫퍼지코믹스 외전까지 최종 완결!\n전원 포인트 & 4천P <우리는 가을에 끝난다> 12H 리다무 중! ©DCCxRCC 말도 안 돼.\n내가? 쟤한테? <심술의 끝은 순정> 론칭, 최대 2,000P! ⓒ김감토,퀼라,이노/대원씨아이 5월 웹툰\n신작 캘린더 오픈! 이벤트와 신작 모두 모아 보기! 시즌 3! 단 7일,\n감상 전원 포인트백! <내게 빌어봐> 시즌 3로 컴백! ⓒ 리베냐 / ⓒ 아이린, 이서, 스튜디오 담 / 재담미디어, 디키 <파륜> 론칭!\n기간 한정 전원 포인트백 거래를 하자. 내 아이를 낳아 다오. ⓒ핫퍼지코믹스 10 12 50% 할인 이달의 신작 이벤트 리디온리 리다무 완결작 All100 웹툰 실시간 랭킹 더보기 1 상수리나무 아래 P 외 3명 4화 무료 4.9 (52,522) 2 백조 무덤 [개정판] 앤트 스튜디오 외 2명 3화 무료 4.8 (67) 3 안개를 삼킨 나비 스르륵코믹스 외 1명 4화 무료 4.9 (3,540) 4 파륜(破倫) [개정판] 핫퍼지코믹스 3화 무료 5 (62) 5 상류 사회 스르륵코믹스 외 1명 7화 무료 4.9 (3,930) 6 계약 결혼일 뿐이었다 스르륵코믹스 외 1명 7화 무료 4.9 (4,617) 7 오달리스크 스르륵코믹스 외 1명 4화 무료 4.9 (2,756) 8 당신과 나는 사는 세계가 다르다 치울 외 2명 10화 무료 4.9 (168) 9 내게 빌어봐 이서 외 3명 15화 무료 4.8 (1,061) 요일별 웹툰 더보기 월 화 수 목 금 토 일 수직 스크롤 막대, 2페이지 기다리면 무료로 시작해! 더보기 오늘, 리디의 발견 웹툰 키워드 검색 더보기 #로맨스판타지 #피폐물 #빙의/영혼체인지 #로맨스 #집착남 #사내연애 #완결 웹툰 베스트 더보기 이벤트 보러가기 더보기 질투가 나서 그랬어.\n이제는.. 나랑만 해. ⓒ스르륵코믹스 여전히 재수 없고\n여전히 예쁘네. 너. ⓒDCCENT 마침 대공비가 필요하거든.\n아일린, 우리 결혼할까? ⓒ스르륵코믹스 지금, 리디에서만 볼 수 있는 웹툰 더보기 상수리나무 아래 P, 서말, 나무, 김수지 4.9 (52,522) 상수리나무 아래 4컷 만화 스르륵코믹스, 김수지, P 4.9 (2,508) 요한은 티테를 사랑한다 혜닝, 안경원숭이 4.9 (1,285) 오직 리디에서만! 수직 스크롤 막대, 4페이지 새로 나온 작품 더보기 늘 짜릿한 신작! #BL 더보기 리디(주) 사업자 정보 이용약관 개인정보 처리방침 고객센터 ⓒ RIDI Corp. 도구 막대 내 서재 검색 홈 알림 MY")
