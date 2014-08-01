from selenium.common.exceptions import NoSuchElementException
from PIL import Image
import platform
import os
import argparse

parser = argparse.ArgumentParser(prog=__file__,formatter_class=argparse.ArgumentDefaultsHelpFormatter, description="Run a selenium script and take screenshots of ui elements, to see if your code changes broke anything")
parser.add_argument('--baseline', action='store_true', help="Generate the baseline images.")
# parser.add_argument('--baseline', action='store', choices=[True, False], required=True, help="Generate the baseline images or not.")
# parser.add_argument('--browser', action='store', type=str, choices=['chrome', 'firefox', 'ie', 'safari'], required=True, help="The browser to run the test on.")
args = vars(parser.parse_args())

class ui_testing(object):

    def __init__(self, driver):
        self.file_path = None
        self.is_baseline = args['baseline']
        # self.browser = args['browser']
        self.driver = driver

    def compareScreenshots(self):
        if not self.is_baseline:          
            baselines = sorted(os.listdir(self.baseline_location))
            newfiles = sorted(os.listdir(self.new_location))
            if len(baselines) == len(newfiles):
                try:
                    print "Generating diff images..."
                    for i in range(len(baselines)):
                        if ((baselines[i].split('_baseline')[0] + '.png') == newfiles[i]):
                            difference_file = os.path.abspath(os.path.join(self.diff_location, newfiles[i].replace('.png', '_diff.png')))

                            baselines[i] = os.path.abspath(os.path.join(self.baseline_location, baselines[i]))
                            newfiles[i] = os.path.abspath(os.path.join(self.new_location, newfiles[i]))

                            # os.system("composite %s %s -compose difference x:" % (baseline_file, test_file))

                            os.system("composite %s %s -compose difference %s" % (baselines[i], newfiles[i], difference_file))
                            print "difference file %s successfully saved" % os.path.basename((difference_file))
                            os.system("convert -delay 100 %s %s -loop 0 %s" % (baselines[i], newfiles[i], difference_file.replace('.png', '.gif')))
                            print ".gif difference file %s successfully saved" % os.path.basename(difference_file)

                        else:
                            print "Files do not match, trying to compare %s and %s" % (baselines[i], newfiles[i])  
                except IOError:
                    print "File or folder not found"
            else:
                print 'Error, differing amount of files in %s & %s directories' % (self.baseline_location, self.new_location)

        # description is anything that can be used to uniquely identify what is
        # being tested. (this can be an element id, name of the html file, etc.)
        # if elementID is specified, then the screenshot will be cropped to only that image.
        # by default a screenshot is taken of the whole page.
    def generateFileNameAndTakeScreenshot(self, description, elementID=None):
        browser = self.driver.name
        file_extension = '.png'
        op_sys = platform.system().lower()

        if description:
            if self.is_baseline:
                print "Generating baseline image..."

                file_name = str(description) + '_' +  browser + '_' + op_sys + '_baseline' + file_extension
                self.file_path = os.path.join(self.baseline_location, file_name)

                if os.path.exists(self.file_path):
                    inp = str(raw_input(os.path.basename(self.file_path) + " already exists, overwrite? (y/n): "))
                    if inp == "y":                      
                        if self.driver.get_screenshot_as_file(self.file_path):
                            print "%s successfully saved" % os.path.basename(self.file_path) 
                            if elementID:
                                if self.cropElement(elementID):
                                    print "%s successfully cropped and saved as %s" % (elementID, os.path.basename(self.file_path))
                                else:
                                    print "error cropping %s" % elementID
                        else:
                            print "error saving %s" % os.path.basename(self.file_path)
                else:                   
                    if self.driver.get_screenshot_as_file(self.file_path):
                        print "%s successfully saved" % os.path.basename(self.file_path) 
                        if elementID:
                            if self.cropElement(elementID):
                                print "%s successfully cropped and saved as %s" % (elementID, os.path.basename(self.file_path))
                            else:
                                print "error cropping %s" % elementID
                    else:
                        print "error saving %s" % os.path.basename(self.file_path)
                
            else:
                print "Generating new image..."
                file_name = str(description) + '_' + browser + '_' + op_sys + file_extension
                self.file_path = os.path.join(self.new_location, file_name)

                if os.path.exists(self.file_path):
                    inp = str(raw_input(os.path.basename(self.file_path) + " already exists, overwrite? (y/n): "))
                    if inp.lower() == 'y':                       
                        if self.driver.get_screenshot_as_file(self.file_path):
                            print "%s successfully saved" % os.path.basename(self.file_path)
                            if elementID:
                                if self.cropElement(elementID):
                                    print "%s successfully cropped and saved as %s" % (elementID, os.path.basename(self.file_path))
                                else:
                                    print "error cropping %s" % elementID
                        else:
                            print "error saving %s" % os.path.basename(self.file_path)
                else:
                    if self.driver.get_screenshot_as_file(self.file_path):
                        print "%s successfully saved" % os.path.basename(self.file_path) 
                        if elementID:
                            if self.cropElement(elementID):
                                print "%s successfully cropped and saved as %s" % (elementID, os.path.basename(self.file_path))
                            else:
                               print "error cropping %s" % elementID
                    else:
                        print "error saving %s" % os.path.basename(self.file_path)
                
        else:
            print "Please specify a description"


    def cropElement(self, elementID, method):
        # used if want to test a single element on the page, replace elementID
        # with the desired id, there are also plenty of other ways to locate an
        # element.
        element = None
        try:           
            if method == "id":
                element = self.driver.find_element_by_id(elementID)
            elif method == "name":
                element = self.driver.find_element_by_name(elementID)
            elif method == "xpath":
                element = self.driver.find_element_by_xpath(elementID)
            elif method == "link_text":
                element = self.driver.find_element_by_link_text(elementID)
            elif method == "partial_link_text":
                element = self.driver.find_element_by_partial_link_text(elementID)
            elif method == "tag_name":
                element = self.driver.find_element_by_tag_name(elementID)
            elif method == "class_name":
                element = self.driver.find_element_by_class_name(elementID)
            elif method == "css_selector":
                element = self.driver.find_element_by_css_selector(elementID)
            else:
                # unknown method
                return False
            location = element.location
            size = element.size
            im = Image.open(self.file_path)
            left = location['x']
            top = location['y']
            right = location['x'] + size['width']
            bottom = location['y'] + size['height']
            im = im.crop((left, top, right, bottom))
            im.save(self.file_path)
            return True
        except NoSuchElementException:
            print "Element with the id %s doesn't exist" % (elementID)
            return False

    def setUpDirectories(self):
        # current directory where file is being executed -- need to change this so folders are created local to the computer, or just add folders to .gitignore 
        self.current_directory = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
        self.ui_testing_folder = os.path.abspath(os.path.join(self.current_directory, 'ui_testing/'))
        self.baseline_location = os.path.abspath(os.path.join(self.ui_testing_folder, 'baseline/'))
        self.new_location = os.path.abspath(os.path.join(self.ui_testing_folder, 'new/'))
        self.diff_location = os.path.abspath(os.path.join(self.ui_testing_folder, 'diff/'))

        if not os.path.exists(self.ui_testing_folder):
            os.mkdir(self.ui_testing_folder)
        if not os.path.exists(self.baseline_location):
            os.mkdir(self.baseline_location)
        if not os.path.exists(self.new_location):
            os.mkdir(self.new_location)
        if not os.path.exists(self.diff_location):
            os.mkdir(self.diff_location)

# if __name__ == '__main__':
#      ui_testing(webdriver.Firefox())