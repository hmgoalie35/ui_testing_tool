#import ui_testing
from ui_testing import *
from selenium import webdriver

class test(object):
# Your local server ip
    def __init__ (self):
        # Start selenium code -----------------------------------------------------------------------------------------------------------------
        # TODO add flag to specify which browser
        self.base_url = "http://localhost:8000/"
        self.driver = webdriver.Firefox()

        ui = ui_testing(self.driver)

        ui.setUpDirectories()

        self.driver.implicitly_wait(30)
        self.driver.maximize_window()
        self.driver.get(self.base_url)

        ui.generateFileNameAndTakeScreenshot('dashboard_anonymous')
        
        self.driver.find_element_by_link_text("Log In").click()

        self.driver.find_element_by_id("id_email").clear()
        self.driver.find_element_by_id("id_email").send_keys("offlinestudent@verificient.com")
        self.driver.find_element_by_id("id_password").clear()
        self.driver.find_element_by_id("id_password").send_keys("offline3")
        self.driver.find_element_by_xpath("//button[@type='submit']").click()
        self.driver.find_element_by_id("funct-browsetest-1").click()
        self.driver.find_element_by_id("funct-continue-Offline Test A").click()
        self.driver.find_element_by_id("check-id").click()
        self.driver.find_element_by_id("next_step_btn").click()

        ui.generateFileNameAndTakeScreenshot('async_download_page')
        ui.generateFileNameAndTakeScreenshot('async_download_page_back_btn', "back_btn")

        self.driver.quit()
        # End selenium code ---------------------------------------------------------------------------------------------------------------------
        ui.compareScreenshots()

if __name__ == '__main__':
    test()