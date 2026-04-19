from selenium.webdriver.common.by import By

# 공통 로케이터
class CommonLocators:
    LOADING_SPINNER = (By.XPATH, "")   # 로딩 스피너
    TOAST_MESSAGE   = (By.XPATH, "")   # 토스트 메시지
    BACK_BUTTON     = (By.XPATH, "")   # 뒤로가기 버튼
    ALERT_CONFIRM   = (By.XPATH, "")   # 얼럿 확인 버튼
    ALERT_CANCEL    = (By.XPATH, "")   # 얼럿 취소 버튼

# 로그인 페이지
class LoginLocators:
    ID_INPUT      = (By.XPATH, "") 
    PW_INPUT      = (By.XPATH, "")   
    LOGIN_BUTTON  = (By.XPATH, "")   
    ERROR_MESSAGE = (By.XPATH, "")   

