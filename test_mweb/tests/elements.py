from selenium.webdriver.common.by import By


class HomeElements:
    MAIN_TITLE  = (By.TAG_NAME, "h1")
    MENU_BUTTON = (By.XPATH, "//button[@class='menu']")


class LoginElements:
    ID_INPUT     = (By.ID, "username")
    PW_INPUT     = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-btn")



class TestData:
    LOGIN = {
        "valid": {
            "id": "test@example.com",
            "pw": "password123",
        },
        "invalid": {
            "id": "wrong@example.com",
            "pw": "wrongpassword",
        },
    }