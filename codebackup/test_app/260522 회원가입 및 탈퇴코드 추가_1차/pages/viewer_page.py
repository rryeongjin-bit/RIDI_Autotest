from pages.base_page import *
from locators.viewer import *

class ViewerPage(BasePage):
    def click_all_viewer(self):
        if self.platform == "aos":
            self.click(AOS_ViewerLocators.ALL_VIEWER_CONTENT)
        else:
            self.click(IOS_ViewerLocators.ALL_VIEWER_CONTENT)
    
    def click_adult_viewer(self):
        if self.platform == "aos":
            self.click(AOS_ViewerLocators.ADULT_VIEWER_CONTENT)
        else:
            self.click(IOS_ViewerLocators.ADULT_VIEWER_CONTENT)

    def is_all_viewer_top_title(self, contents_title: str) -> bool:
        viewer_title = self.get_all_viewer_title()
        print(f"\n뷰어 타이틀: {viewer_title}")
        print(f"\n콘텐츠 타이틀: {contents_title}")
        return contents_title in viewer_title
    
    def is_adult_viewer_top_title(self, contents_title: str) -> bool:
        viewer_title = self.get_adult_viewer_title()
        print(f"\n뷰어 타이틀: {viewer_title}")
        print(f"\n콘텐츠 타이틀: {contents_title}")
        return contents_title in viewer_title

    def is_next_episode_displayed(self) -> bool:
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