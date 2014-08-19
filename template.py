# when setup is complete, go to the command line and cd to the directory where this file would be located.
# type in "python template.py"
# this will run the baseline screenshots for the page (because we passed in True as the 3rd parameter to the constructor)
# if you were to make css changes then run
# python template.py again with True now set to False,
# the program will then generate the diff images that will be located in a folder called ui_testing in the directory where this file is located. Navigate to firefox and
# there will be baseline, diff and new folders which are self explanatory.

# I recommend just copying the ui_testing.py file to the directory where you will be writing selenium code,
# but if that is not feasible for any reason uncomment the code below which will allow you to access the ui_testing
# module no matter where the script you are writing is located. 

# uncomment below in your selenium script if you are not going to be running your selenium script in the same
# directory as where the ui_testing.py file is located.

#--------------------------------------------------------------------------------
#import site
## you probably cloned it, so copy that path to below.
#site.addsitedir('/path/to/ui_testing_tool')
#--------------------------------------------------------------------------------


# Code that needs to be added to the selenium script will be enclosed by #--------- and another #----------

#-------------------------------------------------------------------------------- 
from ui_testing import ui_testing
#--------------------------------------------------------------------------------


from selenium import webdriver

class Test(object):
    def __init__ (self):
        # Local server ip
        self.base_url = "http://www.github.com/"

        self.driver = webdriver.Firefox()

        #--------------------------------------------------------------------------------
        # remember to create an instance of the object, sending the driver, browser and if it is the baseline run to the constructor.
        # if you were to use chrome, multiple screenshots have to be taken of the same page because chromedriver can't
        # take full page screenshots.
        ui = ui_testing(self.driver, 'chrome', True) # change True to False to run in non baseline mode which will then generate the diff images. I don't have access to github's source code so i can't show a demo.
        #--------------------------------------------------------------------------------


        # I recommend to maximize the window. not necessary though. Analysis will show weird results however if comparisons are done w/ different browser window sizes
        self.driver.maximize_window()
        self.driver.get(self.base_url)

        #--------------------------------------------------------------------------------
        # This will take a screenshot of the whole page, note that method or element_specifier are not being passed
        ui.generateFileNameAndTakeScreenshot('github_landing')
        #--------------------------------------------------------------------------------

        #--------------------------------------------------------------------------------
        # This will take a screenshot of the whole page, and then crop the image to just this element. it will find the specified xpath
        ui.generateFileNameAndTakeScreenshot('github_logo', 'xpath', "/html/body/div[1]/div[1]/div/a")
        #--------------------------------------------------------------------------------

        # don't forget to quit the driver.
        self.driver.quit()
if __name__ == '__main__':
    Test()