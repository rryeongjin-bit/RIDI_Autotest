from pages.base_page import *
from locators.viewer import *

class ViewerPage(BasePage):
    def click_all_viewer(self):
        try:
            if self.platform == "aos":
                self.wait_for_element_visible(AOS_ViewerLocators.ALL_VIEWER_CONTENT, timeout=10)
                self.click(AOS_ViewerLocators.ALL_VIEWER_CONTENT)
            else:
                self.wait_for_element_visible(IOS_ViewerLocators.ALL_VIEWER_CONTENT, timeout=10)
                self.click(IOS_ViewerLocators.ALL_VIEWER_CONTENT)
        except Exception:
            self.log.warning(f"[click_all_viewer] 요소 타임아웃 - 뷰어 터치 시도 ({self.platform})")
            size = self.driver.get_window_size()
            x = size["width"] // 2
            y = size["height"] // 2
            actions = ActionChains(self.driver)
            actions.w3c_actions.pointer_action.move_to_location(x, y)
            actions.w3c_actions.pointer_action.pointer_down()
            actions.w3c_actions.pointer_action.pause(0.1)
            actions.w3c_actions.pointer_action.pointer_up()
            actions.perform()
            time.sleep(5) 

    def click_adult_viewer(self):
        try:
            if self.platform == "aos":
                self.wait_for_element_visible(AOS_ViewerLocators.ADULT_VIEWER_CONTENT, timeout=10)
                self.click(AOS_ViewerLocators.ADULT_VIEWER_CONTENT)
            else:
                self.wait_for_element_visible(IOS_ViewerLocators.ADULT_VIEWER_CONTENT, timeout=10)
                self.click(IOS_ViewerLocators.ADULT_VIEWER_CONTENT)
        except Exception:
            self.log.warning(f"[click_adult_viewer] 요소 타임아웃 - 뷰어 터치 시도 ({self.platform})")
            size = self.driver.get_window_size()
            x = size["width"] // 2
            y = size["height"] // 2
            actions = ActionChains(self.driver)
            actions.w3c_actions.pointer_action.move_to_location(x, y)
            actions.w3c_actions.pointer_action.pointer_down()
            actions.w3c_actions.pointer_action.pause(0.1)
            actions.w3c_actions.pointer_action.pointer_up()
            actions.perform()
            time.sleep(5) 

    def is_all_viewer_top_title(self, contents_title: str) -> bool:
        viewer_title = self.get_all_viewer_title()
        self.log.info(f"\n뷰어 타이틀: {viewer_title}")
        self.log.info(f"콘텐츠 타이틀: {contents_title}")
        return contents_title in viewer_title
    
    def is_adult_viewer_top_title(self, contents_title: str) -> bool:
        viewer_title = self.get_adult_viewer_title()
        self.log.info(f"뷰어 타이틀: {viewer_title}")
        self.log.info(f"콘텐츠 타이틀: {contents_title}")
        return contents_title in viewer_title
    
    def is_all_viewer_displayed(self) -> bool:
        if self.platform == "aos":
            return self.is_element_present(AOS_ViewerLocators.ALL_VIEWER_CONTENT, timeout=3)
        else:
            return self.is_element_present(IOS_ViewerLocators.ALL_VIEWER_CONTENT, timeout=3)
    
    def is_adult_viewer_displayed(self) -> bool:
        if self.platform == "aos":
            return self.is_element_present(AOS_ViewerLocators.ADULT_VIEWER_CONTENT, timeout=3)
        else:
            return self.is_element_present(IOS_ViewerLocators.ADULT_VIEWER_CONTENT, timeout=3)

    def click_next_episode_displayed(self) -> bool:
        if self.platform == "aos":
            self.click(AOS_ViewerLocators.NEXT_EPISODE_BTN)
        else:
            self.click(IOS_ViewerLocators.NEXT_EPISODE_BTN)
    
    def get_all_viewer_title(self) -> str:
        if self.platform == "aos":
            return self.find_element(AOS_ViewerLocators.VIEWER_TOP_TITLE).text
        else:
            return self.find_element(IOS_ViewerLocators.ALL_VIEWER_TOP_TITLE).get_attribute("name")
        
    def get_adult_viewer_title(self) -> str:
        if self.platform == "aos":
            return self.find_element(AOS_ViewerLocators.VIEWER_TOP_TITLE).text
        else:
            return self.find_element(IOS_ViewerLocators.ADULT_VIEWER_TOP_TITLE).get_attribute("name")
        
    def click_back_all(self):
        if self.platform == "aos":
            if not self.is_present(AOS_ViewerLocators.VIEWER_BACK_BTN):
                self.click(AOS_ViewerLocators.ALL_VIEWER_CONTENT)
            self.click(AOS_ViewerLocators.VIEWER_BACK_BTN)
        else:
            if not self.is_present(IOS_ViewerLocators.VIEWER_BACK_BTN):
                self.click(IOS_ViewerLocators.ALL_VIEWER_CONTENT)
            self.click(IOS_ViewerLocators.VIEWER_BACK_BTN)
    
    def click_back_adult(self):
        if self.platform == "aos":
            if not self.is_present(AOS_ViewerLocators.VIEWER_BACK_BTN):
                self.click(AOS_ViewerLocators.ADULT_VIEWER_CONTENT)
            self.click(AOS_ViewerLocators.VIEWER_BACK_BTN)
        else:
            if not self.is_present(IOS_ViewerLocators.VIEWER_BACK_BTN):
                self.click(IOS_ViewerLocators.ADULT_VIEWER_CONTENT)
            self.click(IOS_ViewerLocators.VIEWER_BACK_BTN)