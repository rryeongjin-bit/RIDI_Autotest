
from selenium.webdriver.common.by import By
from appium.webdriver.common.appiumby import AppiumBy

class AOS_SignUpLocators:
    SIGNUP_TITLE        = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("com.initialcoms.ridi:id/title_text")')
    LOGIN_JOIN_BTN      = (AppiumBy.XPATH, '//div[@id="__next"]/div/div/div[2]/a[3]')
    INPUT_ID            = (AppiumBy.XPATH, '//input[@name="userId"]')
    INPUT_PW            = (AppiumBy.XPATH, '//input[@name="password"]')
    INPUT_PW_CONFIRM    = (AppiumBy.XPATH, '//input[@name="passwordConfirm"]')
    INPUT_EMAIL         = (AppiumBy.XPATH, '//input[@name="email"]')
    INPUT_NAME          = (AppiumBy.XPATH, '//input[@name="name"]')
    AGREE_FIRST         = (AppiumBy.XPATH, '//form/div[2]/div/div[1]/label/div')
    AGREE_SECOND        = (AppiumBy.XPATH, '//form/div[2]/div/div[3]/label/div')
    AGREE_CHECK         = (AppiumBy.XPATH, '//form/div[2]/div[2]/span')
    SIGNUP_BTN          = (AppiumBy.XPATH, '//form/div[3]/div/button[1]')
    SIGNUP_VERIFY       = (AppiumBy.XPATH, '//main/div[1]/div[1]')
    SIGNUP_COMPLET      = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("com.initialcoms.ridi:id/title_text")')
    CONFIRM_BTN         = (AppiumBy.XPATH, '//button[contains(text(),"확인")]')

class AOS_WithdrawAccountLocators:
    WITHDRAW_ACCOUNT_TITLE          = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("회원탈퇴")')
    AGREE_CHECKBOX                  = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("위 내용을 이해했으며, 모두 동의합니다.")')
    REASON_WITHDRAW_CHECKBOX_FIRST  = (AppiumBy.XPATH, '//android.view.View[@resource-id="__next"]/android.view.View/android.view.View/android.view.View[1]/android.view.View/android.widget.TextView[1]')
    PW_INPUT                        = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.widget.EditText")')
    WITHDRAW_BTN                    = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("회원 탈퇴")')
    CHECK_WITHDRAW_ACCOUNT_POPUP    = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("android:id/alertTitle")')
    CHECK_WITHDRAW_ACCOUNT_OK_BTN   = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("android:id/button1")')
    WITHDRAW_ACCOUNT_COMPLETE_POPUP = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("android:id/message").textContains("탈퇴처리가 완료되었습니다")')

class IOS_SignUpLocators:
    SIGNUP_TITLE        = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeStaticText[`name == "회원가입"`][2]')
    LOGIN_JOIN_BTN      = (AppiumBy.NAME, '이메일로 가입하기')
    INPUT_ID            = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeTextField[`name == "아이디"`]')
    INPUT_PW            = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeSecureTextField[`name == "비밀번호 비밀번호 보이기"`]')
    INPUT_PW_CONFIRM    = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeSecureTextField[`name == "비밀번호 확인 비밀번호 보이기"`]')
    INPUT_EMAIL         = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeTextField[`name == "이메일 주소"`]')
    INPUT_NAME          = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeTextField[`name == "이름"`]')
    AGREE_FIRST         = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeSwitch[`name == "선택 포함 전체 약관 동의"`]')
    AGREE_SECOND        = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeSwitch[`name == "개인정보 수집 및 이용(필수)"`]')
    AGREE_CHECK         = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeStaticText[`name == "개인정보 수집 및 이용에 동의해주세요."`]')
    SIGNUP_BTN          = (AppiumBy.NAME, '일반 회원가입')
    SIGNUP_VERIFY       = (AppiumBy.IOS_CLASS_CHAIN,  '**/XCUIElementTypeStaticText[`name == "회원가입"`][2]')
    SIGNUP_COMPLET      = (AppiumBy.XPATH, '(//XCUIElementTypeStaticText[@name="회원가입 완료"])[2]')
    CONFIRM_BTN         = (AppiumBy.XPATH, '//XCUIElementTypeButton[@name="확인"]')

class IOS_WithdrawAccountLocators:
    WITHDRAW_ACCOUNT_TITLE          = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeStaticText[`name == "회원 탈퇴"`]')
    AGREE_CHECKBOX                  = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeSwitch[`name == "위 내용을 이해했으며, 모두 동의합니다."`]')
    REASON_WITHDRAW_CHECKBOX_FIRST  = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeSwitch[`name == "원하는 작품이 부족해서"`]')
    WITHDRAW_BTN                    = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeButton[`name == "회원 탈퇴"`]')
   #CHECK_WITHDRAW_ACCOUNT_POPUP    
    CHECK_WITHDRAW_ACCOUNT_OK_BTN   = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeButton[`name == "확인"`]')
    WITHDRAW_ACCOUNT_COMPLETE_POPUP = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeStaticText[`name == "탈퇴처리가 완료되었습니다. 이용해 주셔서 감사합니다."`]')

    @staticmethod
    def CHECK_WITHDRAW_ACCOUNT_POPUP(user_id: str) -> tuple:
        return (AppiumBy.IOS_CLASS_CHAIN, f'**/XCUIElementTypeStaticText[`name == "{user_id} 계정의 회원 탈퇴를 진행하시겠습니까?"`]')