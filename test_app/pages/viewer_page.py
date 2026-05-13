from pages.base_page import *
from pages.locators import *

class ViewerPage(BasePage):
    def click_viewer(self):
        if self.platform == "aos":
            self.click(AOS_ViewerLocators.VIEWER_CONTENT)
        else:
            self.click(IOS_ViewerLocators.VIEWER_CONTENT)

    def is_viewer_top_title(self, contents_title: str) -> bool:
        viewer_title = self.get_viewer_title()
        print(f"\n뷰어 타이틀: {viewer_title}")
        print(f"\n콘텐츠 타이틀: {contents_title}")
        return contents_title in viewer_title

    def is_next_episode_displayed(self) -> bool:
        if self.platform == "aos":
            self.click(AOS_ViewerLocators.NEXT_EPISODE_BTN)
        else:
            self.click(IOS_ViewerLocators.NEXT_EPISODE_BTN)
    
    def get_viewer_title(self) -> str:
        if self.platform == "aos":
            return self.find_element(AOS_ViewerLocators.VIEWER_TOP_TITLE).text
        else:
            return self.find_element(IOS_ViewerLocators.VIEWER_TOP_TITLE).get_attribute("name")