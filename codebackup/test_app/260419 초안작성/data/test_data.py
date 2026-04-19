from config.settings import * 

# 테스트 계정
class TestAccount:
    AOS = {
        "id": AOS_TEST_ID,
        "pw": AOS_TEST_PW,
    }
    IOS = {
        "id": IOS_TEST_ID,
        "pw": IOS_TEST_PW,
    }

# 딥링크 URL (앱 내부 페이지 진입용)
class DeepLinks:
    # 메인홈
    HOME             = "ridi://home"

    # 검색
    SEARCH           = "ridi://search"

    # 내서재
    LIBRARY          = "ridi://myridi"

    # 알림
    NOTIFICATION     = "ridi://notification"

    # 작품 상세 (전연령) - 작품 ID 치환 필요
    CONTENT_ALL_AGES = "ridi://content/YOUR_CONTENT_ID"

    # 작품 상세 (성인) - 작품 ID 치환 필요
    CONTENT_ADULT    = "ridi://content/YOUR_ADULT_CONTENT_ID"


# 테스트 작품 데이터
class TestContent:
    ALL_AGES = {
        "id":    "YOUR_ALL_AGES_CONTENT_ID",
        "title": "전연령 테스트 작품",
    }
    ADULT = {
        "id":    "YOUR_ADULT_CONTENT_ID",
        "title": "성인 테스트 작품",
    }
    CART = {
        "id":    "YOUR_CART_CONTENT_ID",
        "title": "카트 담기 테스트 작품",
    }
    PAYMENT = {
        "id":    "YOUR_PAYMENT_CONTENT_ID",
        "title": "결제 테스트 작품",
    }