## comments with 2 #'s signify code that has to be added to your selenium code. If there are no comments, then it is just selenium code.
# the generateFileNameAndTakeScreenshot function is the one that will be used the most. Look at its documentation for clarification.

# when setup is complete, go to the command line and cd to the directory where this file would be located.
# the below line will generate the baseline images for firefox.
# python template.py --baseline --browser firefox
# if you were to make css changes then run
# python template.py --browser firefox
# the program will then generate the diff images that will be located in a folder called ui_testing in the directory where this file is located. Navigate to firefox and
# there will be baseline, diff and new folders which are self explanatory.


## If the selenium script is not in the same directory as the ui_testing_tool file, then the below line is necessary.
import site
## you probably cloned it, so copy that path to below.
site.addsitedir('/path/to/ui_testing_tool')

from ui_testing import *

from selenium import webdriver

class test(object):
    def __init__ (self):
        # Local server ip
        self.base_url = "http://www.google.com/"
        self.driver = webdriver.Firefox()

        ## remember to create an instance of the object, sending the driver to the constructor.
        ui = ui_testing(self.driver)
        
        self.driver.implicitly_wait(30)
        # recommended to maximize the window. not necessary though. Analysis will show weird results however if comparisons are done w/ different browser window sizes
        self.driver.maximize_window()
        self.driver.get(self.base_url)

        ## This will take a screenshot of the whole page, note that method or element_specifier are not being passed
        ui.generateFileNameAndTakeScreenshot('google_landing_page')
    
        self.driver.find_element_by_id("gbqfq").clear()
        self.driver.find_element_by_id("gbqfq").send_keys("this is a test")

        ## This will take a screenshot of the whole page, and then crop the image to just this element. it will find gbqfq by id.
        ui.generateFileNameAndTakeScreenshot('search_bar_with_text','id', 'gbqfq')

        ## don't forget to quit the driver before calling the compareScreenshots() function
        self.driver.quit()


        ## this needs to be the last thing that is called, otherwise the diff images will never be generated.
        ui.compareScreenshots()

if __name__ == '__main__':
    test()