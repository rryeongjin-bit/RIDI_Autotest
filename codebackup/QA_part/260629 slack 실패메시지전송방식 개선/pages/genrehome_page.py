from pages.base_page import *
from locators.contentshome import *
from locators.genrehome import *
from locators.common import *
from data.test_data import *

class MainhomePage(BasePage):
    def is_genrehome_displayed(self) -> bool:
        locator = AOS_GenrehomeLocators.COMIC_RECOMMEND_TAB if self.platform == "aos" \
                  else IOS_GenrehomeLocators.COMIC_NEW_QUICK
        return self.is_present(locator)
    
    def click_cart_icon(self):
        if self.platform == "aos":
            self.tap_coordinate(1006, 156)
        else:
            self.tap_coordinate(363, 69)
