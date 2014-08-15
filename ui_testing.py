# Import necessary modules
from selenium.common.exceptions import NoSuchElementException
from PIL import Image
import platform
import os
import inspect
import time
import math

# Valid methods selenium can use to search for an element on a page. See
# selenium python API for more info if desired.
VALID_METHODS = ['id', 'name', 'xpath', 'link_text',
           'partial_link_text', 'tag_name', 'class_name', 'css_selector']

"""
Notes: 
    Baseline images are those that everything should be compared to. If you want to change the baseline files you can just delete the baseline folder, or just simply run the program in baseline mode
and the program will prompt you if you want to overwrite the current baselines, enter in 'y'. If you want to only change one baseline photo, you can just copy the new baseline file to the baseline folder
or run the program and type 'y' only for the file name you want overwritten.
    New images are the ones generated when the program is not in baseline mode, these are the images that have had some html or css changes. The corresponding baseline and new images will be compared to generate
the diff images.
    Diff images are those that show the differences between the baseline and new images. I have the program currently generating a .gif that visually shows the change as well as a normal .png that just shows
what the change was as an overlay.
"""
class ui_testing(object):

    # Constructor that takes a selenium driver, browser, and is_baseline.
    # is_baseline tells the code if it should generate the diff files or not.
    def __init__(self, driver, browser, is_baseline):
        # Used to keep track of the generated file name.
        self.file_path = None
        # if baseline or not.
        self.is_baseline = is_baseline

        # the browser and selenium driver have to both be the same or the program throws an error. ex: can't use Firefox() driver while passing in firefox to the constructor.

        # The browser the test is being run on. 
        self.browser = browser.lower()
        # The selenium driver being used.
        self.driver = driver
        # list to contain the names of files that have changed, if any.
        self.difference_list = []

        # used in generating file names for chrome
        self.count = 1

        # Set up the directories, see function documentation below.
        self.setUpDirectories()
    """
        Params: None

        This only does anything if this is not the baseline run.
        Compares the files only if they match. What i mean by match is that they have the same generated file name, minus the _baseline. 
        Calls imagemagick on the command line and saves the result in the difference file, which is a .gif and .png
    """

    def compareScreenshots(self):
        # only do this if not baseline
        if not self.is_baseline:
            # sort the list so files in each directory match up with one
            # another.
            baselines = sorted(os.listdir(self.baseline_location))
            newfiles = sorted(os.listdir(self.new_location))
            # Check to make sure both directories have the same number of
            # files, if not then there is no point to compare because there
            # would be an error at some point when comparing the files.
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
                            # in the diff location. The file name is the same, all we have to do is add in _diff. Which is what is being done below.
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

                            # compare the histograms of the 2 images, and if they are different then generate the diff image, otherwise no need to generate a diff image if the images havn't changed
                            i1 = Image.open(baselines[i])
                            i2 = Image.open(newfiles[i])
                            if i1.histogram() != i2.histogram():
                                # keep track of the images reported as being changed.
                                self.difference_list.append(os.path.basename(newfiles[i]))

                               # the os.system calls below can be tweaked as desired, further digging into imagemagick's documentation may come up with a better way for comparison
                                os.system(
                                    "composite %s %s -compose difference %s" %
                                    (baselines[i], newfiles[i], difference_file))
                                print "[SUCCESS] %s saved." % os.path.basename((difference_file))

                                # generate the .gif (pulled right from imagemagick's documentation)
                                os.system("convert -delay 100 %s %s -loop 0 %s" %
                                          (baselines[i], newfiles[i], difference_file_gif))
                                print "[SUCCESS] %s saved." % os.path.basename(difference_file_gif)

                                # this imagemagick call can be commented in to have a different type of diff image generated (highlights differences in a blue.)
                                # remember to change the name of the file it will be saved as if desired. --> difference_file.replace('_diff.png', '_alternatediff.png') --> difference_file.replace('_diff.png', 'THE_FILE_NAME_YOU_WANT.png')
                                # os.system("compare -dissimilarity-threshold 1 -fuzz 20% -metric AE -highlight-color blue " + baselines[i] + " " + newfiles[i] + " " + difference_file.replace('_diff.png', '_alternatediff.png'))
                        else:
                            # ex: google_landing_page and google_search_results
                            # do not match.
                            print "[ERROR] files do not match, trying to compare %s and %s." % (baselines[i], newfiles[i])

                    # if anything was added to the difference list, then we know there were difference files generated, notify the user which files changed.
                    if len(self.difference_list) > 0:
                        print "[INFO] differences found, the file(s) with differences are: \n" + '\n'.join(self.difference_list)
                    else:
                        print "[INFO] no differences found!"
                # Could not find one of the baseline, new or diff folders. Did you delete them in the middle of running the program?
                except IOError:
                    print "[ERROR] file or folder not found."
            # Different # of files in the baseline and new directories. Error because every baseline file should have a corresponding new file.
            else:
                print '[ERROR] differing number of files in %s & %s directories.' % (self.baseline_location, self.new_location)

        """
        Params:
            [REQUIRED] description: anything that can be used to uniquely identify what the screenshot will be of..

            [OPTIONAL] method: the method to be used to search for the element_specifier. Valid methods are 'id', 
              'name', 'xpath', 'link_text', 'partial_link_text', 'tag_name', 'class_name', 'css_selector'. This is to be passed
              if you want to crop the screenshot to just an element of the page (ex: just have a picture of a certain button). It is required
              if you pass in element_specifier.

            [OPTIONAL] element_specifier: the element_specifier used to search for the element. This is to be passed
              if you want to crop the screenshot to just an element of the page (ex: just have a picture of a certain button). It is required
              if you pass in method.

        *****Element cropping is not supported on chrome!!!! This is due to a limitation of chromedriver*****

        If method is passed to the function, then element_specifier needs to be passed to the function and vice versa
        By default a screenshot of the whole page is taken. If method and element_specifier are passed to the function then
        the full page screenshot will be cropped to just that element.
        ex: generateFileNameAndTakeScreenshot('google_landing_page_text_entry_box', 'id', 'whatever_the_id_is')

        This function generates a file name for the image that is going to be saved and then takes a screenshot. If the browser being used is chrome, 
        then we need to take multiple screenshots because chromedriver does not support full page screenshots.
        """

    def generateFileNameAndTakeScreenshot(self, description, method=None, element_specifier=None):
        # If the browser is chrome and an element_specifier or method was passed (i.e. user is trying to crop an element) throw an error.
        if self.browser == "chrome" and (element_specifier or method):
            self.driver.quit()
            raise Exception(
                "Cropping specific elements is not supported when using chrome, this is due to a limitation of chromedriver. Please remove %s & %s from the generateFileNameAndTakeScreenshot function and run again." %
                (method, element_specifier))
        # File extension
        file_extension = '.png'
        # The operating system
        op_sys = platform.system().lower()
        # Throw an error if a description was not passed in.
        if description:
            # Generate the baselines if this is a baseline run.
            if self.is_baseline:
                print "Generating baseline image..."
                # Generate the file name. This is created by concatenating the
                # description, browser and operating system. _baseline is also
                # appended for clarification.
                file_name = str(description) + '_' +  self.browser + \
                    '_' + op_sys + '_baseline' + file_extension
                # Add the directory where this file should be saved.
                self.file_path = os.path.join(self.baseline_location, file_name)
                # if the browser is chrome then the screenshots that are generated all have _baseline_NUMBER_HERE.png. So need to check if those already exist.
                # it is likely that if _baseline_0.png exists then the others do also but the chained or's are for safety.
                #TODO enable check for any number at the end of the file (currently goes up to 7)
                if self.browser == 'chrome':
                    split = os.path.split(self.file_path)
                    file_exists = os.path.exists(os.path.join(split[0], str(0) + '_' + split[1])) or os.path.exists(os.path.join(split[0], str(1) + '_' + split[1])) or os.path.exists(os.path.join(split[0], str(2) + '_' + split[1])) or os.path.exists(os.path.join(split[0], str(3) + '_' + split[1])) or os.path.exists(os.path.join(split[0], str(4) + '_' + split[1])) or os.path.exists(os.path.join(split[0], str(5) + '_' + split[1])) or os.path.exists(os.path.join(split[0], str(6) + '_' + split[1])) or os.path.exists(os.path.join(split[0], str(7) + '_' + split[1]))
                # for other browsers just use the normal file_path that was generated.
                else:
                    file_exists = os.path.exists(self.file_path)
                # If file already exists, prompt user to overwrite it or not.
                # Entering in y will overwrite all of the screenshots for a webpage on chrome. 1_description ... 4_description will all be overwritten
                if file_exists:
                    # get user input (y or n)
                    inp = str(
                        raw_input(os.path.basename(self.file_path) + " already exists, overwrite? (y/n): "))
                    if inp.lower() == "y":
                        # cropping is not supported for chrome. due to the fact that chromedriver does not take fullscreen screenshots, have to manually
                        # scroll the browser window and take screenshots after
                        # each scroll.
                        if self.browser == "chrome":
                            # javascript code that is executed by selenium driver to determine how many scrolls need to occur in order to capture
                            # the whole page in screenshots.
                            js_code = "window.scrollTo(0,0);var scrollValue=document.body.scrollHeight/window.innerHeight;return scrollValue;"
                            # returns largest integer <= what the js code returns.
                            # This was honestly figured out from pure trial and error.
                            val = math.floor(self.driver.execute_script(js_code))
                            i = 0
                            # split the directory and file name so i can append the number to the beginning of the file name.
                            split =  os.path.split(self.file_path)
                            # add in the number specifier
                            file_name = os.path.join(split[0], str(self.count) + '_' + split[1])
                            self.count +=1
                            # Take the initial screenshot of the page no scrolling occurred yet.
                            # Note specific number is being appended to the beginning of the file name.
                            # selenium's get_screenshot_as_file returns true if all is well.
                            if self.driver.get_screenshot_as_file(file_name): 
                                print "[SUCCESS] %s saved." % os.path.basename(file_name)
                            else:
                                print "[ERROR] saving %s failed." % os.path.basename(file_name)
                            # only bother scrolling if the page needs to be scrolled. note this is compiled code.
                            if self.driver.execute_script('window.scrollTo(0,1);return 0!=window.pageYOffset?(window.scrollTo(0,0),!0):(window.scrollTo(0,0),!1);'):
                                # val is the number of times we need to scroll, so need to generate this # of screenshots.     
                                while i < val:
                                    # scroll the page, because we already took the initial screenshot above.
                                    self.driver.execute_script('window.scrollBy(0, window.innerHeight);')
                                    # this sleep is needed because selenium tends to advance to the next webpage before this code can finish.
                                    time.sleep(3)

                                    file_name = os.path.join(split[0], str(self.count) + '_' + split[1])
                                    self.count +=1

                                    # selenium's get_screenshot_as_file returns true if all is well.
                                    if self.driver.get_screenshot_as_file(file_name):
                                        print "[SUCCESS] %s saved." % os.path.basename(file_name)
                                    else:
                                        print "[ERROR] saving %s failed." % os.path.basename(file_name)
                                    i+=1
                        # browser isn't chrome
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
                                    if method in VALID_METHODS:
                                        # crop the element, returns true if
                                        # successful. see function documentation below.
                                        if self.cropElement(element_specifier, method):
                                            print "[SUCCESS] %s cropped." % (os.path.basename(self.file_path))
                                        else:
                                            print "[ERROR] cropping %s failed." % element_specifier
                                    else:
                                        # user did not pass element_specifier
                                        # and a valid method to the function.
                                        msg = "[ERROR] invalid parameters, please make sure an element specifier AND a method are being passed, see valid methods: \n" + str(
                                            VALID_METHODS)
                                        self.driver.quit()
                                        raise Exception(msg)
                            else:
                                print "[ERROR] saving %s failed." % os.path.basename(self.file_path)
                else:
                    # cropping is not supported for chrome. due to the fact that chromedriver does not take fullscreen screenshots, have to manually
                    # scroll the browser window and take screenshots after each
                    # scroll.
                    if self.browser == "chrome":
                        # javascript code that is executed by selenium driver to determine how many scrolls need to occur in order to capture
                        # the whole page in screenshots.
                        js_code = "window.scrollTo(0,0);var scrollValue=document.body.scrollHeight/window.innerHeight;return scrollValue;"
                        # returns largest integer <= what the js code returns.
                        # This was honestly figured out from pure trial and error.
                        val = math.floor(self.driver.execute_script(js_code))
                        i = 0
                        # split the directory and file name so i can append the number to the beginning of the file name.
                        split =  os.path.split(self.file_path)
                        # add in the number specifier
                        file_name = os.path.join(split[0], str(self.count) + '_' + split[1])
                        self.count +=1

                        # Take the initial screenshot of the page no scrolling occurred yet.
                        # Note baseline_NUMBER_HERE is being appended.
                        # selenium's get_screenshot_as_file returns true if all is well.
                        if self.driver.get_screenshot_as_file(file_name): 
                            print "[SUCCESS] %s saved." % os.path.basename(file_name)
                        else:
                            print "[ERROR] saving %s failed." % os.path.basename(file_name)
                        # only bother scrolling if the page needs to be scrolled. note this is compiled code.
                        if self.driver.execute_script('window.scrollTo(0,1);return 0!=window.pageYOffset?(window.scrollTo(0,0),!0):(window.scrollTo(0,0),!1);'):
                            # val is the number of times we need to scroll, so need to generate this # of screenshots.     
                            while i < val:
                                # scroll the page, because we already took the initial screenshot above.
                                self.driver.execute_script('window.scrollBy(0, window.innerHeight);')
                                # this sleep is needed because selenium tends to advance to the next webpage before this code can finish.
                                time.sleep(3)

                                file_name = os.path.join(split[0], str(self.count) + '_' + split[1])
                                self.count +=1

                                # selenium's get_screenshot_as_file returns true if all is well.
                                if self.driver.get_screenshot_as_file(file_name):
                                    print "[SUCCESS] %s saved." % os.path.basename(file_name)
                                else:
                                    print "[ERROR] saving %s failed." % os.path.basename(file_name)
                                i+=1
                    else:
                        # get_screenshot_as_file returns true if screenshot was
                        # successfully saved.
                        if self.driver.get_screenshot_as_file(self.file_path):
                            print "[SUCCESS] %s saved." % os.path.basename(self.file_path)
                            # if element_specifier was passed to the function
                            if element_specifier:
                                # make sure user also passed in a valid method.
                                if method in VALID_METHODS:
                                    # crop the element, returns true if
                                    # successful. see function documentation below.
                                    if self.cropElement(element_specifier, method):
                                        print "[SUCCESS] %s cropped." % (os.path.basename(self.file_path))
                                    else:
                                        print "[ERROR] cropping %s failed." % element_specifier
                                else:
                                    # user did not pass element_specifier and a
                                    # valid method to the function.
                                    msg = "[ERROR] invalid parameters, please make sure an element specifier AND a method are being passed, see valid methods: \n" + str(
                                        VALID_METHODS)
                                    self.driver.quit()
                                    raise Exception(msg)
                        else:
                            print "[ERROR] saving %s failed." % os.path.basename(self.file_path)
            # if it was not the baseline run.
            else:
                # if it is not the baseline run then we want to create the new
                # images that will be used to create the diff images.
                print "Generating new image..."
                # create the filename for the new file. use description,
                # browser, operating system. note there is no _baseline
                file_name = str(description) + '_' + \
                    self.browser + '_' + op_sys + file_extension
                # add the directory where the file will be saved.
                self.file_path = os.path.join(self.new_location, file_name)

                # cropping is not supported for chrome. due to the fact that chromedriver does not take fullscreen screenshots, have to manually
                # scroll the browser window and take screenshots after each
                # scroll.
                if self.browser == "chrome":
                    # javascript code that is executed by selenium driver to determine how many scrolls need to occur in order to capture
                    # the whole page in screenshots.
                    js_code = "window.scrollTo(0,0);var scrollValue=document.body.scrollHeight/window.innerHeight;return scrollValue;"
                    # returns largest integer <= what the js code returns.
                    # This was honestly figured out from pure trial and error.
                    val = math.floor(self.driver.execute_script(js_code))
                    i = 0

                    # split the directory and file name so i can append the number to the beginning of the file name.
                    split =  os.path.split(self.file_path)

                    file_name = os.path.join(split[0], str(self.count) + '_' + split[1])
                    self.count +=1
                    # Take the initial screenshot of the page no scrolling occurred yet.
                    # Note baseline_NUMBER_HERE is being appended.
                    # selenium's get_screenshot_as_file returns true if all is well.
                    if self.driver.get_screenshot_as_file(file_name): 
                        print "[SUCCESS] %s saved." % os.path.basename(file_name)
                    else:
                        print "[ERROR] saving %s failed." % os.path.basename(file_name)
                    # only bother scrolling if the page needs to be scrolled. note this is compiled code.
                    if self.driver.execute_script('window.scrollTo(0,1);return 0!=window.pageYOffset?(window.scrollTo(0,0),!0):(window.scrollTo(0,0),!1);'):
                        # val is the number of times we need to scroll, so need to generate this # of screenshots.     
                        while i < val:
                            # scroll the page, because we already took the initial screenshot above.
                            self.driver.execute_script('window.scrollBy(0, window.innerHeight);')
                            # this sleep is needed because selenium tends to advance to the next webpage before this code can finish.
                            time.sleep(3)

                            file_name = os.path.join(split[0], str(self.count) + '_' + split[1])
                            self.count +=1

                            # selenium's get_screenshot_as_file returns true if all is well.
                            if self.driver.get_screenshot_as_file(file_name):
                                print "[SUCCESS] %s saved." % os.path.basename(file_name)
                            else:
                                print "[ERROR] saving %s failed." % os.path.basename(file_name)
                            i+=1
                # browser isn't chrome
                else:
                    # if file doesn't already exist, save the file,
                    # get_screenshot_as_file returns true if successful
                    if self.driver.get_screenshot_as_file(self.file_path):
                        print "[SUCCESS] %s saved." % os.path.basename(self.file_path)
                        # if user passed in an element_specifier
                        if element_specifier:
                            # make sure user also passed in a valid method
                            if method in VALID_METHODS:
                                # crop the element, returns true if successful. see function documentation below.
                                if self.cropElement(element_specifier, method):
                                    print "[SUCCESS] %s cropped." % (os.path.basename(self.file_path))
                                else:
                                    print "[ERROR] cropping %s failed." % element_specifier
                            else:
                                # user did not pass element_specifier and a
                                # valid method.
                                msg = "[ERROR] invalid parameters, please make sure an element specifier AND a method are being passed, see valid methods: \n" + str(
                                    VALID_METHODS)
                                self.driver.quit()
                                raise Exception(msg)
                    else:
                        print "[ERROR] saving %s failed." % os.path.basename(self.file_path)

        else:
            print "[ERROR] You need to specify a description."

    """
    Params:
        element_specifier: what will be used to search for the element. ex: the actual element id, xpath, etc.
        method: the method to search for the element_specifier. ex: (id, name, xpath)

    Crop the whole page screenshot to just the element specified and save it in the same file.
    """

    def cropElement(self, element_specifier, method):
        element = None
        # attempt to search for the elemnent using the method and element_specifier provided by the user.
        # if it cannot be found selenium throws a NoSuchElementException exception.
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
            # get the location of the element.
            location = element.location
            # get the size of the element
            size = element.size
            # open the current file
            im = Image.open(self.file_path)
            # get the x coordinate
            left = location['x']
            # get the y coordinate
            top = location['y']
            # compute the bottom corner
            right = location['x'] + size['width']
            # compute the othe bottom corner
            bottom = location['y'] + size['height']
            # crop it to size.
            im = im.crop((left, top, right, bottom))
            # save it to the same file.
            im.save(self.file_path)
            return True
        except NoSuchElementException:
            print "[ERROR] element with the %s,  %s doesn't exist, or cannot be located." % (method, element_specifier)
            return False
    """
    Create the necessary directories used to store the images. All of the housekeeping stuff.
    """

    def setUpDirectories(self):
        # Get the location of the caller script by inspecting the stack. This is probably not necessary, will revisit.
        # TODO fix logic behind where the ui_testing folder is created.
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
        # Create a folder in the browser folder called baseline, and do this for new and diff folders also.
        # The new folder is where the new images are saved, the diff folder is
        # where the imagemagick results are saved
        self.baseline_location = os.path.abspath(
            os.path.join(self.browser_folder, 'baseline/'))
        self.new_location = os.path.abspath(
            os.path.join(self.browser_folder, 'new/'))
        self.diff_location = os.path.abspath(
            os.path.join(self.browser_folder, 'diff/'))

        # Make sure the browser driver and the browser specified in the constructor match.
        driverName = self.driver.name
        # internet explorer specific nuance.
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
    # to string.
    def __str__(self):
        return "Baseline: %s \nBrowser: %s" % (self.is_baseline, self.browser)