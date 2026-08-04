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

class SignUpData:
    SIGNUP_PASSWORD = "ridi1234!"
    SIGNUP_NAME     = "QAtest"

class DeepLinks:    
    COMIC_RECOMMEND_HOME             = "ridi://GenreHome/%EB%A7%8C%ED%99%94/%EB%A7%8C%ED%99%94/%EC%B6%94%EC%B2%9C"  
    WEBTOON_RECOMMEND_HOME           = "ridi://GenreHome/%EC%9B%B9%ED%88%B0/%EC%9B%B9%ED%88%B0/%EC%B6%94%EC%B2%9C"  
    WEBNOVEL_RECOMMEND_HOME          = "ridi://GenreHome/%EC%9B%B9%EC%86%8C%EC%84%A4/%EC%B6%94%EC%B2%9C"
    GENERAL_RECOMMEND_HOME           = "ridi://GenreHome/%EB%8F%84%EC%84%9C"


    #SEARCH           = "ridi://search"
    #LIBRARY          = "ridi://Library"
    #NOTIFICATION     = "ridi://NotificationCenter/%EC%A0%84%EC%B2%B4" #알림센터 전체탭
    MYRIDI            = "ridi://MyRidi"

    LOGIN             = "ridi://SignIn"
    LOGIN_JOIN        = "ridi://SignUp"
    #CART             = "ridi://CartWebView/https%3A%2F%2Fridibooks.com%2Fcart/%EC%B9%B4%ED%8A%B8"
    #WISH             = "ridi://CartWebView/https%3A%2F%2Fridibooks.com%2Fwishlist/%EC%9C%84%EC%8B%9C%EB%A6%AC%EC%8A%A4%ED%8A%B8"
    #IAP              = "ridi://CashCharge"
    #CHARGE_CASH      = "ridi://AutoCharge/balance"
    #CHARGE_MONTH     = "ridi://AutoCharge/period"

    CONTENT_ALL_AGES  = "ridi://ContentsHome/4403013103"  # 판타지 웹툰 > 바다새와 늑대
    CONTENT_ADULT     = "ridi://ContentsHome/120106230"  # BL 웹소설 > 여리여리
    CONTENT_CART      = "ridi://ContentsHome/297003061" # 만화e북 > 열혈강호

class TestContent:
    ALL_AGES = {
        "id":    "4403013103",
        "title": "바다새와 늑대",   
        "url":   DeepLinks.CONTENT_ALL_AGES,
    }

    ADULT = {
        "id":    "120106230",
        "title": "여리여리",
        "url":   DeepLinks.CONTENT_ADULT,
    }

    CART = {
       "id":    "297003061",
       "title": "열혈강호",
       "url":   DeepLinks.CONTENT_CART,
    }