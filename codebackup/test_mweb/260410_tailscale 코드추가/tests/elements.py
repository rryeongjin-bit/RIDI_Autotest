from selenium.webdriver.common.by import By
from config.settings import *

class URLs:
    HOME  = BASE_URL
    LOGIN = f"{BASE_URL}/account/login"
    
    # aos
    CONTENT_HOME_ALL_AOS = f"https://ridibooks.com/books/5847000001"  # 웹툰 > 두 명의 상속인
    CONTENT_HOME_ADULT_AOS = f"https://ridibooks.com/books/2057208584"  # 웹소설 > 꽃은 밤을 걷는다

    CONTENT_ALL_VIEW_AOS = f"https://ridibooks.com/books/5847000004/view"
    CONTENT_ALL_NEXTVIEW_AOS = f"https://ridibooks.com/books/5847000005/view"
    CONTENT_ADULT_VIEW_AOS = f"https://ridibooks.com/books/2057208587/view"
    CONTENT_ADULT_NEXTVIEW_AOS = f"https://ridibooks.com/books/2057208588/view"

    #ios
    CONTENT_HOME_ALL_IOS = f"https://ridibooks.com/books/1518000665"  # 웹툰 > 카야
    CONTENT_HOME_ADULT_IOS = f"https://ridibooks.com/books/3885042618"  # 웹소설 > 히든 피스 메이커

    CONTENT_ALL_VIEW_IOS = f"https://ridibooks.com/books/1518000668/view"
    CONTENT_ALL_NEXTVIEW_IOS = f"https://ridibooks.com/books/1518000669/view"
    CONTENT_ADULT_VIEW_IOS = f"https://ridibooks.com/books/3885043404/view"
    CONTENT_ADULT_NEXTVIEW_IOS = f"https://ridibooks.com/books/3885043405/view"

    CONTENT_HOME = f"https://ridibooks.com/books/4395000113" # 만화e북 > 마왕성 요리사
    CART = f"https://ridibooks.com/cart/"
    CHECKPOUT = f"https://ridibooks.com/order/checkout"

class GenreHome:
    MAIN_LOGIN_AOS = (By.CSS_SELECTOR, '#__next > div.fig-6bprg0 > header > nav > div > div:nth-child(3) > a')
    MAIN_LOGIN_IOS = (By.CLASS_NAME, 'fig-10qv71b')

class LoginPage:
    ID_INPUT  = (By.CSS_SELECTOR, "input[name='username']")
    PW_INPUT  = (By.CSS_SELECTOR, "input[name='password']")
    LOGIN_BTN = (By.CSS_SELECTOR, "#__next > div > section > div > form.fig-gx0lhm > button")

class LoginData:
    valid_aos =  {
        "id": "4qatest",
        "pw": "qwer1234!",
    }

    valid_ios =  {
        "id": "ridiadmin",
        "pw": "ridi0331!",
    }

class ContentHome:
    EPISODE = "4화" 
    RENT_BTN = (By.CSS_SELECTOR, f"button[data-book-title*='{EPISODE}'].serial_book_rent_button")
    BUY_BTN  = (By.CSS_SELECTOR, f"button[data-book-title*='{EPISODE}'].serial_book_buy_button")

    SELECT_ALL = (By.XPATH, "//*[contains(text(), '전체 선택')]")
    FIRST_EPISODE_CHECKBOX = (By.XPATH, "//input[@id='book4395000113']")

    CART_BTN = (By.CSS_SELECTOR, "button.btn_cart.js_add_cart_selected")
    TOAST_MSG_CART = (By.CSS_SELECTOR, "div.vex.RSGToast.vex-closing > div.vex-content.success > form > div.vex-dialog-message")

class PaymentPopup:
    FREE_VIEW_HEADER = (By.XPATH, "//*[contains(@class, 'header_title') and contains(text(), '무료로 보기')]")
    PAYMENT_METHOD_BTN = (By.CSS_SELECTOR, "#js_serial_free_rent_coupon_popup > div.popup_body.serial_checkout_wrapper > div.checkout_buttons > button.text_button.js_show_another_payment")

    PAYMENT_HEADER = (By.XPATH, "//*[contains(@class, 'header_title') and contains(text(), '결제하기')]") 
    PAYMENT_BTN = (By.CSS_SELECTOR,"#js_serial_checkout_cash_and_point_popup > div.popup_body.serial_checkout_wrapper > div.checkout_buttons > button.rui_button_blue_40.rui_button_eink_black_40.blue_button.js_payment_book_cash_and_point_immediate_view")

    SELECT_PAYMENT_HEADER = (By.XPATH, "//*[@id='serial_popup']/div[2]/div[1]/div[1]/h2[contains(text(), '결제 방법 선택')]")
    RENT_NEXT_BTN = (By.XPATH, "//*[@id='serial_popup']/div[2]/div[2]/div[2]/button[1]")
    NEXT_PAYMENT_METHOD_BTN = (By.CSS_SELECTOR, "#serial_popup > div.popup_wrapper > div.popup_body.serial_checkout_wrapper > div.checkout_buttons > button.button_size_40.text_button")
    NEXT_PAYMENT_BTN = (By.CSS_SELECTOR, "#serial_popup > div.popup_wrapper > div.popup_body.serial_checkout_wrapper > div.checkout_buttons > button")

class Viewer:
    NEXT_BTN  = (By.XPATH, "//button[.//span[contains(text(), '다음')]]")
    PREV_BTN  = (By.XPATH, "//button[.//span[contains(text(), '이전')]]")

class CartPage:
    BUY_TAB = (By.CSS_SELECTOR, "li.cart_tab.js_buy_tab")
    BUY_TAB_SELECTED = (By.CSS_SELECTOR, "li.cart_tab.js_buy_tab.selected")

    SELECT_ALL_CHECKBOX = (By.XPATH, "//*[contains(text(), '전체 선택')]")
    FIRST_CONTENTS_CHECKBOX = (By.XPATH, "//*[@id='book4395000113']")
    
    BUY_BTN = (By.CSS_SELECTOR, "#form > article.cart_summary_wrapper.js_cart_summary > div > div.buy_button_wrapper > button")

class CheckoutPage:
    PAYMENT_AGREE_TOGGLE = (By.CSS_SELECTOR, "#ISLANDS__Ridipay > div > div > section:nth-child(2) > div > label > span.ridipay-wzoz6w")
    PAYMENT_BTN = (By.CSS_SELECTOR, "#ISLANDS__Ridipay > div > div > section:nth-child(2) > form > button")
    PAYMENT_COMPLETE = (By.XPATH, "//*[@id='__next']/main/div/h2[contains(text(), '결제가 완료되었습니다.')]")
