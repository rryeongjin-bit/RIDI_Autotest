from config.settings import * 

class TestAccount:
    AOS = {
        "id": AOS_TEST_ID,
        "pw": AOS_TEST_PW,
    }
    IOS = {
        "id": IOS_TEST_ID,
        "pw": IOS_TEST_PW,
    }

class DeepLinks:
    HOME             = "ridi://GenreHome/%EC%9B%B9%ED%88%B0/%EC%9B%B9%ED%88%B0/%EC%B6%94%EC%B2%9C"  #웹툰 추천탭
    SEARCH           = "ridi://search"
    LIBRARY          = "ridi://Library"
    NOTIFICATION     = "ridi://NotificationCenter/%EC%A0%84%EC%B2%B4" #알림센터 전체탭
    MYRIDI           = "ridi://MyRidi"

    LOGIN            = "ridi://SignIn"
    LOGIN_JOIN       = "ridi://SignUp"
    CART             = "ridi://CartWebView/https%3A%2F%2Fridibooks.com%2Fcart/%EC%B9%B4%ED%8A%B8"
    WISH             = "ridi://CartWebView/https%3A%2F%2Fridibooks.com%2Fwishlist/%EC%9C%84%EC%8B%9C%EB%A6%AC%EC%8A%A4%ED%8A%B8"
    IAP              = "ridi://CashCharge"
    CHARGE_CASH      = "ridi://AutoCharge/balance"
    CHARGE_MONTH     = "ridi://AutoCharge/period"

    CONTENT_ALL_AGES = "ridi://ContentsHome/5847000001"  # 로판 웹툰 > 두 명의 상속인
    CONTENT_ADULT    = "ridi://ContentsHome/2057208584"  # BL 웹소설 > 꽃은 밤을 걷는다
    CONTENT_CART     = "ridi://ContentsHome/4395000113" # 만화e북 > 마왕성 요리사

class TestContent:
    ALL_AGES = {
        "id":    "5847000001",
        "title": "두 명의 상속인",   
        "url":   DeepLinks.CONTENT_ALL_AGES,
    }
