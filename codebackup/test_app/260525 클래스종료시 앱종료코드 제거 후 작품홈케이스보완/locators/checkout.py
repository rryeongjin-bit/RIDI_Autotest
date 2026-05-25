from selenium.webdriver.common.by import By
from appium.webdriver.common.appiumby import AppiumBy

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