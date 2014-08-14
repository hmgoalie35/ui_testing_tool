from selenium.common.exceptions import NoSuchElementException
from PIL import Image
import platform
import os
import inspect
import time
import math

# Valid methods selenium can use to search for an element on a page. See
# selenium python API for more info if desired.
methods = ['id', 'name', 'xpath', 'link_text',
           'partial_link_text', 'tag_name', 'class_name', 'css_selector']


class ui_testing(object):
    # Constructor that takes driver, browser, and is_baseline

    def __init__(self, driver, browser, is_baseline):
        self.file_path = None
        self.is_baseline = is_baseline
        self.browser = browser.lower()
        self.driver = driver
        # list to contain the names of files that have changed
        self.difference_list = []
        # Set up the directories, see function documentation below.
        self.setUpDirectories()
    """
    This only does anything if this is not the baseline run.
    Compares the files only if they match. What i mean by match is that they have the same generated file name, minus the _baseline. 
    Calls imagemagick on the command line and saves the result in the difference file.
    """

    def compareScreenshots(self):
        differences_found = False
        # only do this if not baseline
        if not self.is_baseline:
            # sort the list so files in each directory match up with one
            # another.
            baselines = sorted(os.listdir(self.baseline_location))
            newfiles = sorted(os.listdir(self.new_location))
            # Check to make sure both directories have the same number of
            # files, if not then there is no point to compare because there
            # would be an error at some point.
            if len(baselines) == len(newfiles):
                try:
                    print "Generating diff images (if any)..."
                    # iterate through all files
                    for i in range(len(baselines)):
                        # check to make sure the file names match, otherwise we would be comparing different pictures and this would show some drastic differences.
                        # see generateFileNameAndTakeScreenshot to see how
                        # filenames are being generated and why the check below
                        # works.
                        split = baselines[i].split('_baseline')
                        if (split[0] + split[1] == newfiles[i]):
                            # generate the difference file that will be saved
                            # in the diff location
                            difference_file = os.path.abspath(
                                os.path.join(self.diff_location, newfiles[i].replace('.png', '_diff.png')))
                            # for the .gif version, everything else is the same
                            # just change the extension.
                            difference_file_gif = difference_file.replace(
                                '.png', '.gif')

                            # os.listdir only lists the filenames, so add back
                            # on the full path to the file.

                            # TODO refactor this logic.
                            baselines[i] = os.path.abspath(
                                os.path.join(self.baseline_location, baselines[i]))
                            newfiles[i] = os.path.abspath(
                                os.path.join(self.new_location, newfiles[i]))
                            # compare the histograms of the 2 images, and if they are not the same then generate the diff image, otherwise no need to generate a diff image if the images havn't changed
                            i1 = Image.open(baselines[i])
                            i2 = Image.open(newfiles[i])
                            if i1.histogram() != i2.histogram():
                                differences_found = True
                                # keep track of the images reported as being changed.
                                self.difference_list.append(os.path.basename(newfiles[i]))
                                # if the generated diff file or diff gif file already exists prompt the user if they want to overwrite it.
                                # if os.path.exists(difference_file) or os.path.exists(difference_file_gif):
                                #     inp = str(raw_input(os.path.basename(difference_file) + " and " + os.path.basename(difference_file_gif) +  " already exist, overwrite BOTH? (y/n): "))
                                #     if inp.lower() == "y":
                                # the os.system calls below can be tweaked as desired, further digging into imagemagick's documentation may come up with a better way for comparison
                                # os.system("composite %s %s -compose difference x:" % (baseline_file, test_file))
                                #         os.system("composite %s %s -compose difference %s" % (baselines[i], newfiles[i], difference_file))
                                # print "[SUCCESS] %s overwritten." %
                                # os.path.basename((difference_file))

                                #         os.system("convert -delay 100 %s %s -loop 0 %s" % (baselines[i], newfiles[i], difference_file_gif))
                                #         print "[SUCCESS] %s overwritten." % os.path.basename(difference_file_gif)
                                # else:

                                # the os.system calls below can be tweaked as desired, further digging into imagemagick's documentation may come up with a better way for comparison
                                # os.system("composite %s %s -compose difference x:" % (baseline_file, test_file))
                                os.system(
                                    "composite %s %s -compose difference %s" %
                                    (baselines[i], newfiles[i], difference_file))
                                print "[SUCCESS] %s saved." % os.path.basename((difference_file))

                                os.system("convert -delay 100 %s %s -loop 0 %s" %
                                          (baselines[i], newfiles[i], difference_file_gif))
                                print "[SUCCESS] %s saved." % os.path.basename(difference_file_gif)


                                # os.system("compare -dissimilarity-threshold 1 -fuzz 20% -metric AE -highlight-color blue " + baselines[i] + " " + newfiles[i] + " " + difference_file.replace('_diff.png', '_alternatediff.png'))
                        else:
                            # ex: google_landing_page and google_search_results
                            # do not match.
                            print "[ERROR] files do not match, trying to compare %s and %s." % (baselines[i], newfiles[i])

                    if differences_found:
                        print "[INFO] differences found, the file(s) with differences are: \n" + '\n'.join(self.difference_list)
                    else:
                        print "[INFO] no differences found!"

                except IOError:
                    print "[ERROR] file or folder not found."
            else:
                print '[ERROR] differing number of files in %s & %s directories.' % (self.baseline_location, self.new_location)

        """
        Params:
            description: anything that can be used to uniquely identify what is being tested. REQUIRED
            method: the method to be used to search for the element_specifier. Valid methods are 'id', 
              'name', 'xpath','link_text', 'partial_link_text', 'tag_name', 'class_name', 'css_selector' OPTIONAL
            element_specifier: the element_specifier used to search for the element. OPTIONAL

        If method is passed to the function, then element_specifier needs to be passed to the function and vice versa
        By default a screenshot of the whole page is taken. If method and element_specifier are passed to the function then
        the full page screenshot will be cropped to just that element.
        ex: generateFileNameAndTakeScreenshot('google_landing_page_text_entry_box', 'id', 'whatever_the_id_is')
        """

    def generateFileNameAndTakeScreenshot(self, description, method=None, element_specifier=None):
        # What browser the selenium object was instantiated with.
        browser = self.driver.name
        if browser == "chrome" and (element_specifier or method):
            self.driver.quit()
            raise Exception(
                "Cropping specific elements is not supported when using chrome, this is due to a limitation of chromedriver. Please remove %s & %s from the generateFileNameAndTakeScreenshot function and run again." %
                (method, element_specifier))
        # File extension
        file_extension = '.png'
        # The operating system
        op_sys = platform.system().lower()

        if description:
            # Generate the baselines if this is a baseline run.
            if self.is_baseline:
                print "Generating baseline image..."
                # Generate the file name. This is created by taking the
                # description, browser and operating system. _baseline is also
                # appended for clarification.
                file_name = str(description) + '_' +  browser + \
                    '_' + op_sys + '_baseline' + file_extension
                # Add the directory where this file should be saved.
                self.file_path = os.path.join(self.baseline_location, file_name)
                if self.browser == 'chrome':
                    file_exists = os.path.exists(os.path.join(self.baseline_location, file_name.split('.png')[0] + '_0' + '.png')) or os.path.exists(os.path.join(self.baseline_location, file_name.split('.png')[0] + '_1' + '.png')) or os.path.exists(os.path.join(self.baseline_location, file_name.split('.png')[0] + '_2' + '.png')) or os.path.exists(os.path.join(self.baseline_location, file_name.split('.png')[0] + '_3' + '.png')) or os.path.exists(os.path.join(self.baseline_location, file_name.split('.png')[0] + '_4' + '.png')) or os.path.exists(os.path.join(self.baseline_location, file_name.split('.png')[0] + '_5' + '.png')) or os.path.exists(os.path.join(self.baseline_location, file_name.split('.png')[0] + '_6' + '.png'))
                else:
                    file_exists = os.path.exists(self.file_path)
                # If file already exists, prompt user to overwrite it or not.
                if file_exists:
                    inp = str(
                        raw_input(os.path.basename(self.file_path) + " already exists, overwrite? (y/n): "))
                    if inp.lower() == "y":
                        # cropping is not supported for chrome. due to the fact that chromedriver does not take fullscreen screenshots, have to manually
                        # scroll the browser window and take screenshots after
                        # each scroll.
                        if self.browser == "chrome":
                            js_code = "var scrollValue=document.body.scrollHeight/window.innerHeight;return scrollValue;"

                            val = math.floor(self.driver.execute_script(js_code))
                            i = 0
                            if self.driver.get_screenshot_as_file(self.file_path.split('.png')[0] + '_' + str(i) + '.png'): 
                                print "[SUCCESS] %s saved." % os.path.basename((self.file_path.split('.png')[0] + '_' + str(i) + '.png'))
                            else:
                                print "[ERROR] saving %s failed." % os.path.basename((self.file_path.split('.png')[0] + '_' + str(i) + '.png'))
                            while i < val:
                                self.driver.execute_script('window.scrollBy(0, window.innerHeight);')
                                time.sleep(3)
                                if self.driver.get_screenshot_as_file(self.file_path.split('.png')[0] + '_' + str(i+1) + '.png'):
                                    print "[SUCCESS] %s saved." % os.path.basename((self.file_path.split('.png')[0] + '_' + str(i+1) + '.png'))
                                else:
                                    print "[ERROR] saving %s failed." % os.path.basename((self.file_path.split('.png')[0] + '_' + str(i+1) + '.png'))
                                i+=1
                        else:
                            # get_screenshot_as_file returns true if screenshot
                            # was successfully saved.
                            if self.driver.get_screenshot_as_file(self.file_path):
                                print "[SUCCESS] %s overwritten." % os.path.basename(self.file_path)
                                # if element_specifier was passed to the
                                # function
                                if element_specifier:
                                    # make sure user also passed in a valid
                                    # method.
                                    if method in methods:
                                        # crop the element, returns true if
                                        # successful.
                                        if self.cropElement(element_specifier, method):
                                            print "[SUCCESS] %s cropped." % (os.path.basename(self.file_path))
                                        else:
                                            print "[ERROR] cropping %s failed." % element_specifier
                                    else:
                                        # user did not pass element_specifier
                                        # and a valid method to the function.
                                        msg = "[ERROR] invalid parameters, please make sure an element specifier AND a method are being passed, see valid methods: \n" + str(
                                            methods)
                                        self.driver.quit()
                                        raise Exception(msg)
                            else:
                                print "[ERROR] saving %s failed." % os.path.basename(self.file_path)
                else:
                    # cropping is not supported for chrome. due to the fact that chromedriver does not take fullscreen screenshots, have to manually
                    # scroll the browser window and take screenshots after each
                    # scroll.
                    if self.browser == "chrome":
                        js_code = "var scrollValue=document.body.scrollHeight/window.innerHeight;return scrollValue;"

                        val = math.floor(self.driver.execute_script(js_code))
                        i = 0
                        if self.driver.get_screenshot_as_file(self.file_path.split('.png')[0] + '_' + str(i) + '.png'): 
                            print "[SUCCESS] %s saved." % os.path.basename((self.file_path.split('.png')[0] + '_' + str(i) + '.png'))
                        else:
                            print "[ERROR] saving %s failed." % os.path.basename((self.file_path.split('.png')[0] + '_' + str(i) + '.png'))
                        # only bother scrolling if the page needs to be scrolled.
                        if self.driver.execute_script('window.scrollTo(0,1);return 0!=window.pageYOffset?(window.scrollTo(0,0),!0):(window.scrollTo(0,0),!1);'):
                            while i < val:
                                self.driver.execute_script('window.scrollBy(0, window.innerHeight);')
                                time.sleep(3)
                                if self.driver.get_screenshot_as_file(self.file_path.split('.png')[0] + '_' + str(i+1) + '.png'):
                                    print "[SUCCESS] %s saved." % os.path.basename((self.file_path.split('.png')[0] + '_' + str(i+1) + '.png'))
                                else:
                                    print "[ERROR] saving %s failed." % os.path.basename((self.file_path.split('.png')[0] + '_' + str(i+1) + '.png'))
                                i+=1
                    else:
                        # get_screenshot_as_file returns true if screenshot was
                        # successfully saved.
                        if self.driver.get_screenshot_as_file(self.file_path):
                            print "[SUCCESS] %s saved." % os.path.basename(self.file_path)
                            # if element_specifier was passed to the function
                            if element_specifier:
                                # make sure user also passed in a valid method.
                                if method in methods:
                                    # crop the element, returns true if
                                    # successful.
                                    if self.cropElement(element_specifier, method):
                                        print "[SUCCESS] %s cropped." % (os.path.basename(self.file_path))
                                    else:
                                        print "[ERROR] cropping %s failed." % element_specifier
                                else:
                                    # user did not pass element_specifier and a
                                    # valid method to the function.
                                    msg = "[ERROR] invalid parameters, please make sure an element specifier AND a method are being passed, see valid methods: \n" + str(
                                        methods)
                                    self.driver.quit()
                                    raise Exception(msg)
                        else:
                            print "[ERROR] saving %s failed." % os.path.basename(self.file_path)

            else:
                # if it is not the baseline run then we want to create the new
                # images that will be used to create the diff images.
                print "Generating new image..."
                # create the filename for the new file. use description,
                # browser, operating system. note there is no _baseline
                file_name = str(description) + '_' + \
                    browser + '_' + op_sys + file_extension
                # add the directory where the file will be saved.
                self.file_path = os.path.join(self.new_location, file_name)
                # if the file already exists prompt the user if they want to overwrite or not.
                # if os.path.exists(self.file_path):
                #     inp = str(raw_input(os.path.basename(self.file_path) + " already exists, overwrite? (y/n): "))
                #     if inp.lower() == 'y':
                        # cropping is not supported for chrome. due to the fact that chromedriver does not take fullscreen screenshots, have to manually
                        # scroll the browser window and take screenshots after each scroll.
                        # if self.browser == "chrome":
                        #     self.driver.get_screenshot_as_file(self.file_path)
                        #     self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
                        #     time.sleep(3)
                        #     self.driver.get_screenshot_as_file(self.file_path.split('.png')[0] + '_1.png')
                        #     self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                        #     time.sleep(3)
                        #     self.driver.get_screenshot_as_file(self.file_path.split('.png')[0] + '_2.png')
                        #     self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/1);")
                        #     time.sleep(3)
                        #     self.driver.get_screenshot_as_file(self.file_path.split('.png')[0] + '_3.png')
                        # else:
                    # get_screenshot_as_file returns true if successful.
                    #         if self.driver.get_screenshot_as_file(self.file_path):
                    #             print "[SUCCESS] %s overwritten." % os.path.basename(self.file_path)
                    # if user passed in element_specifier
                    #             if element_specifier:
                    # check to make sure a valid method was also passed in.
                    #                 if method in methods:
                    # crop the element, returns true if successful
                    #                     if self.cropElement(element_specifier, method):
                    #                         print "[SUCCESS] %s cropped." % (os.path.basename(self.file_path))
                    #                     else:
                    #                         print "[ERROR] cropping %s failed." % element_specifier
                    #                 else:
                    # user did not pass element_specifier and a valid method to the function.
                    #                     msg = "[ERROR] invalid parameters, please make sure an element specifier AND a method are being passed, see valid methods: \n" + str(methods)
                    #                     self.driver.quit()
                    #                     raise Exception(msg)
                    #         else:
                    #             print "[ERROR] saving %s failed." % os.path.basename(self.file_path)
                # else:
                # cropping is not supported for chrome. due to the fact that chromedriver does not take fullscreen screenshots, have to manually
                # scroll the browser window and take screenshots after each
                # scroll.
                if self.browser == "chrome":
                    js_code = "var scrollValue=document.body.scrollHeight/window.innerHeight;return scrollValue;"

                    val = math.floor(self.driver.execute_script(js_code))
                    i = 0
                    if self.driver.get_screenshot_as_file(self.file_path.split('.png')[0] + '_' + str(i) + '.png'): 
                        print "[SUCCESS] %s saved." % os.path.basename((self.file_path.split('.png')[0] + '_' + str(i) + '.png'))
                    else:
                        print "[ERROR] saving %s failed." % os.path.basename((self.file_path.split('.png')[0] + '_' + str(i) + '.png'))
                    while i < val:
                        self.driver.execute_script('window.scrollBy(0, window.innerHeight);')
                        time.sleep(3)
                        if self.driver.get_screenshot_as_file(self.file_path.split('.png')[0] + '_' + str(i+1) + '.png'):
                            print "[SUCCESS] %s saved." % os.path.basename((self.file_path.split('.png')[0] + '_' + str(i+1) + '.png'))
                        else:
                            print "[ERROR] saving %s failed." % os.path.basename((self.file_path.split('.png')[0] + '_' + str(i+1) + '.png'))
                        i+=1
                else:
                    # if file doesn't already exist, save the file,
                    # get_screenshot_as_file returns true if successful
                    if self.driver.get_screenshot_as_file(self.file_path):
                        print "[SUCCESS] %s saved." % os.path.basename(self.file_path)
                        # if user passed in an element_specifier
                        if element_specifier:
                            # make sure user also passed in a valid method
                            if method in methods:
                                # crop the element, returns true if successful.
                                if self.cropElement(element_specifier, method):
                                    print "[SUCCESS] %s cropped." % (os.path.basename(self.file_path))
                                else:
                                    print "[ERROR] cropping %s failed." % element_specifier
                            else:
                                # user did not pass element_specifier and a
                                # valid method.
                                msg = "[ERROR] invalid parameters, please make sure an element specifier AND a method are being passed, see valid methods: \n" + str(
                                    methods)
                                self.driver.quit()
                                raise Exception(msg)
                    else:
                        print "[ERROR] saving %s failed." % os.path.basename(self.file_path)

        else:
            print "[ERROR] You need to specify a description."

    """
    Params:
        element_specifier: what will be used to search for the element.
        method: the method to search for the element_specifier. ex: (id, name, xpath)
    Crop the whole page screenshot to just the element specified
    """

    def cropElement(self, element_specifier, method):
        element = None
        try:
            if method == "id":
                element = self.driver.find_element_by_id(element_specifier)
            elif method == "name":
                element = self.driver.find_element_by_name(element_specifier)
            elif method == "xpath":
                element = self.driver.find_element_by_xpath(element_specifier)
            elif method == "link_text":
                element = self.driver.find_element_by_link_text(
                    element_specifier)
            elif method == "partial_link_text":
                element = self.driver.find_element_by_partial_link_text(
                    element_specifier)
            elif method == "tag_name":
                element = self.driver.find_element_by_tag_name(
                    element_specifier)
            elif method == "class_name":
                element = self.driver.find_element_by_class_name(
                    element_specifier)
            elif method == "css_selector":
                element = self.driver.find_element_by_css_selector(
                    element_specifier)
            else:
                # unknown method
                self.driver.quit()
                raise Exception("Invalid Method Specified")
                return False
            location = element.location
            size = element.size
            # open the current file
            im = Image.open(self.file_path)
            left = location['x']
            top = location['y']
            right = location['x'] + size['width']
            bottom = location['y'] + size['height']
            # crop it.
            im = im.crop((left, top, right, bottom))
            # save it to the same file.
            im.save(self.file_path)
            return True
        except NoSuchElementException:
            print "[ERROR] element with the %s,  %s doesn't exist, or cannot be located." % (method, element_specifier)
            return False
    """
    Create the necessary directories used to store the images.
    """

    def setUpDirectories(self):
        # Get the location of the caller script.
        caller_location = os.path.abspath(inspect.stack()[2][1])
        # The current directory is where the caller script is located
        self.current_directory = os.path.abspath(
            os.path.dirname(caller_location))
        # Create a ui_testing folder in the current directory
        self.ui_testing_folder = os.path.abspath(
            os.path.join(self.current_directory, 'ui_testing/'))
        # Create a folder that uses the name of the browser
        self.browser_folder = os.path.abspath(
            os.path.join(self.ui_testing_folder, self.browser))
        # Create a folder in the browser folder called baseline, and do this for new and diff folders.
        # The new folder is where the new images are saved, the diff folder is
        # where the imagemagick results are saved
        self.baseline_location = os.path.abspath(
            os.path.join(self.browser_folder, 'baseline/'))
        self.new_location = os.path.abspath(
            os.path.join(self.browser_folder, 'new/'))
        self.diff_location = os.path.abspath(
            os.path.join(self.browser_folder, 'diff/'))

        # Make sure the comand line arg for --browser and the actual driver
        # selenium is using match.
        driverName = self.driver.name
        if driverName == 'internet explorer':
            driverName = 'ie'
        if driverName != self.browser:
            self.driver.quit()
            raise Exception(
                "[ERROR] the %s driver being used does not match the %s browser specified on the command line." %
                (self.driver.name, self.browser))

        # Create the directories if they do not already exist.
        if not os.path.exists(self.ui_testing_folder):
            os.mkdir(self.ui_testing_folder)
        if not os.path.exists(self.browser_folder):
            os.mkdir(self.browser_folder)
        if not os.path.exists(self.baseline_location):
            os.mkdir(self.baseline_location)
        if not os.path.exists(self.new_location):
            os.mkdir(self.new_location)
        if not os.path.exists(self.diff_location):
            os.mkdir(self.diff_location)
    def __str__(self):
        return "Baseline: %s \nBrowser: %s" % (self.is_baseline, self.browser)
# if __name__ == '__main__':
#      ui_testing(webdriver.Firefox())
