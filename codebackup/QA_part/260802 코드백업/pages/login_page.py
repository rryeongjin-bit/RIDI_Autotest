from pages.base_page import *
from locators.myridi import *
from locators.common import *
# 로그인/로그아웃 전체 플로우를 이 파일로 모으기 위한 import(2026-07-31).
# my_page.py는 login_page.py를 참조하지 않고, data/test_data.py는 pages를 전혀 참조하지 않아
# 순환참조가 없다(확인 완료).
from pages.my_page import MyridiPage
from data.test_data import *

class LoginPage(BasePage):
    def click_login_btn(self):
        if self.platform == "aos":
            self.click(AOS_LoginLocators.LOGIN_BTN)
        else:
            self.click(IOS_LoginLocators.LOGIN_BTN)
    
    def input_id(self, value: str):
        if self.platform == "aos":
            self.send_keys(AOS_LoginLocators.ID_INPUT, value)
        else:
            self.send_keys(IOS_LoginLocators.ID_INPUT,value)

    def input_pw(self, value: str):
        if self.platform == "aos":
            self.send_keys(AOS_LoginLocators.PW_INPUT, value)
        else:
            self.send_keys(IOS_LoginLocators.PW_INPUT,value)

    def click_login(self):
        if self.platform == "aos":
            self.click(AOS_LoginLocators.LOGIN_BUTTON)
        else:
            self.click(IOS_LoginLocators.LOGIN_BUTTON)

    def login(self, id: str, pw: str):
        self.input_id(id)
        self.input_pw(pw)
        self.click_login()
    
    def is_login_success(self, timeout: int = DEFAULT_TIMEOUT) -> bool:
        """MY 화면에 "로그아웃" 버튼이 보이는지로 로그인 여부를 판정한다.

        timeout: 로그인 성공 여부를 최종 확인하는 용도(기본값)와, 로그인 시도 전에 "이미
        로그인된 상태인지" 미리 확인하는 용도로 함께 쓰인다. 후자는 비로그인 상태에서
        기본 대기(10초)를 그대로 소모하면 정상 로그인 흐름이 그만큼 느려지므로 호출측에서
        짧은 값을 넘긴다."""
        locator = AOS_LoginLocators.LOGOUT_BTN if self.platform == "aos" \
                  else IOS_LoginLocators.LOGOUT_BTN
        return self.is_displayed(locator, timeout=timeout)
    
    def click_logout(self):
        if self.platform == "aos":
            self.click(AOS_LoginLocators.LOGOUT_BTN)
        else:
            self.click(IOS_LoginLocators.LOGOUT_BTN)
    
    def confirm_logout(self) -> bool:
        locator = AOS_LogoutLocators.LOGOUT_CONFIRM_POPUP if self.platform == "aos" \
                  else IOS_LogoutLocators.LOGOUT_CONFIRM_POPUP
        return self.is_displayed(locator)
    
    def click_confirm_logout(self):
        if self.platform == "aos":
            self.click(AOS_LogoutLocators.LOGOUT_CONFIRM_BTN)
        else:
            self.click(IOS_LogoutLocators.LOGOUT_CONFIRM_BTN)

    def is_login_page_displayed(self) -> bool:
        locator = AOS_LoginLocators.LOGIN_BTN if self.platform == "aos" \
                  else IOS_LoginLocators.LOGIN_BTN
        return self.is_displayed(locator)

    def logout_if_logged_in(self) -> tuple:
        """로그인 상태면 로그아웃한다. (성공여부, 실패이유) 반환.

        6개 모듈의 TestLogoutIfNeeded가 복붙으로 갖고 있던 코드를 여기로 모았다(2026-07-31).
        이 플로우는 실패 지점이 3곳(마이리디 진입 / 확인 팝업 / 로그아웃 완료)이라 bool 하나로는
        어디서 실패했는지 알 수 없어, 실패 이유 문자열을 함께 반환한다."""
        myridi = MyridiPage(self.driver, self.platform)

        self.open_deeplink(DeepLinks.MYRIDI)
        if not myridi.is_mypage_entered():
            return False, "❌ 마이리디 화면 진입 실패"

        if not self.is_login_success():
            self.log.info("[SKIP] 로그아웃 상태 - 로그아웃 불필요")
            return True, ""

        self.click_logout()
        if not self.confirm_logout():
            return False, "❌ 로그아웃 확인 팝업 미노출"
        self.click_confirm_logout()
        if not self.is_login_page_displayed():
            return False, "❌ 로그아웃 실패"
        return True, ""

    def login_if_needed(self, wait_after_deeplink: int = 10) -> bool:
        """MY 화면으로 진입해 로그인이 필요하면 수행한다. 최종 로그인 상태를 bool로 반환.

        6개 모듈의 TestLogin이 복붙으로 갖고 있던 코드를 여기로 모았다(2026-07-31).
        wait_after_deeplink: MY 딥링크 직후 대기(초). test_basic.py만 20초를 쓰고 나머지 모듈은
        10초를 써서, 그 차이만 파라미터로 받는다.

        아래 두 처리는 실기기에서 확인된 문제 때문에 반드시 이 순서로 있어야 한다(2026-07-29 iOS):
         - 시스템 팝업 정리: 알림/ATT 권한 팝업이 떠 있으면 WDA가 알럿 창만 보게 되어 뒤에 있는
           앱 요소를 아무것도 못 찾는다. 그 상태에선 "로그아웃"/"로그인"이 연달아 타임아웃나고
           실제로는 로그인돼 있는데도 실패로 기록된다. 대기를 늘려도 팝업이 있는 동안은 영원히
           못 찾으므로 먼저 치운다. 알림/ATT가 겹쳐 뜰 수 있어 두 번 연달아 호출한다.
         - 이미 로그인 시 조기 반환: watchdog 재시작은 --reset=skip + --login=auto로 들어와
           이전 실행의 로그인 세션이 앱에 남는다. 그 상태에서는 MY 화면에 "로그인" 버튼 자체가
           없어 click_login_btn이 타임아웃 난다."""
        account = TestAccount.AOS if self.platform == "aos" else TestAccount.IOS
        replace = Replacedevicelist(self.driver, self.platform)

        self.open_deeplink(DeepLinks.MYRIDI)
        time.sleep(wait_after_deeplink)

        self.dismiss_ios_system_alert()
        self.dismiss_ios_system_alert()

        if self.is_login_success(timeout=5):
            self.log.info("[SKIP] 이미 로그인된 상태 - 재로그인 불필요")
            return True

        self.click_login_btn()
        self.switch_to_webview_with_retry()
        self.log.info(f"현재 컨텍스트: {self.driver.contexts}")
        self.login(id=account["id"], pw=account["pw"])
        self.switch_to_native()
        self.wait_for_native()

        if replace.is_replace_device_displayed():
            replace.click_replace_toggle()
            replace.click_replace_btn()
        else:
            self.log.info("[SKIP] 기기 대체 화면 미노출")

        return self.is_login_success()


class Replacedevicelist(BasePage):
    def is_replace_device_displayed(self) -> bool:
        """기기 대체 시트 노출 여부. click_replace_btn과 동일한 렌더링 지연(2026-07-29 실기기
        확인)에 걸리면 시트가 실제로는 뜨는데도 False로 판정되어 대체 플로우 자체를 건너뛰고
        이후 로그인 검증이 실패한다. 시트가 안 뜨는 정상 케이스(등록기기 여유 있음)에서는
        이 대기시간을 그대로 소모하므로, 무한정 늘리지 않고 click_replace_btn과 같은 30초로
        맞춘다."""
        locator = AOS_ReplacedeviceLocators.REPLACEDEVICE_LIST_TITLE if self.platform == "aos" \
                  else IOS_ReplacedeviceLocators.REPLACEDEVICE_LIST_TITLE
        return self.is_present(locator, timeout=30)
    
    def click_replace_toggle(self):
        if self.platform == "aos":
            self.click(AOS_ReplacedeviceLocators.REPLACEDEVICE_TOGGLE_FIRST)
       
    def click_replace_btn(self):
        """기기 대체 시트의 "대체하기" 버튼 클릭.

        로그인 직후 서버에서 등록기기 목록을 받아와 시트를 그리는데, 하단 "대체하기" 버튼은
        타이틀보다 늦게 붙어서 base_page의 기본 대기(DEFAULT_TIMEOUT=10초)를 넘기는 경우가
        실기기로 확인되었다(2026-07-29 iOS - 10초 타임아웃 직후 1.3초 뒤 찍힌 실패 스크린샷에는
        버튼이 이미 정상 노출돼 있었고, 같은 로케이터로 수동 조회하면 XCUIElementTypeButton으로
        정확히 1개 잡힌다 = 로케이터/요소값 문제가 아니라 순수 렌더링 지연).
        타이틀 확인(is_replace_device_displayed)은 통과하고 이 버튼에서만 실패하는 것도 같은
        이유다. 네트워크 상황에 따라 갈리는 경계 케이스라 대기를 넉넉하게 준다."""
        locator = AOS_ReplacedeviceLocators.REPLACEDEVICE_BTN if self.platform == "aos" \
                  else IOS_ReplacedeviceLocators.REPLACEDEVICE_BTN
        self.wait_for_element_clickable(locator, timeout=30).click()
        self.log.info(f"[click] {locator}")
