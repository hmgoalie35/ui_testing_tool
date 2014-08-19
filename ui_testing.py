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

    """
    Params:
        [REQUIRED] description: anything that can be used to uniquely identify what the screenshot will be of.

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
        # python's platform.system() returns 'darwin' on macs so change it for clarification.
        if op_sys == 'darwin':
            op_sys = 'mac'

        # Throw an error if a description was not passed in.
        if description:
            # Generate the baselines if this is a baseline run.
            if self.is_baseline:
                # Generate the file name. This is created by concatenating the
                # description, browser and operating system. _baseline is also
                # appended for clarification.
                file_name = str(description) + '_' +  self.browser + \
                    '_' + op_sys + '_baseline' + file_extension
                # Add the directory where this file should be saved.
                self.file_path = os.path.join(self.baseline_location, file_name)
                # if the browser is chrome then the screenshots that are generated all have NUMBER_ prepended to the file name. So need to check if those already exist.
                if self.browser == 'chrome':
                    # for clarification purposes, i am adding in a running count to the beginning of the file names generated for chrome so need to test to see if the file with the current
                    # self.count exists.
                    # ex: 1_description, 2_description.
                    split = os.path.split(self.file_path)
                    file_exists = os.path.exists(os.path.join(split[0], str(self.count) + '_' + split[1]))

                # for other browsers just use the normal file_path that was generated.
                else:
                    file_exists = os.path.exists(self.file_path)
                # If file already exists, prompt user to overwrite it or not.
                # Entering in y will overwrite all of the screenshots for a webpage on chrome. 1_description ... 4_description will all be overwritten
                if file_exists:
                    # get user input (y or n)
                    inp = str(
                        raw_input('\n' + os.path.basename(self.file_path) + " already exists, overwrite? (y/n): "))
                    if inp.lower() == "y":
                        # cropping is not supported for chrome. due to the fact that chromedriver does not take fullscreen screenshots, have to manually
                        # scroll the browser window and take screenshots after
                        # each scroll.
                        # call the corresponding functions if using chrome or not, see function documentation.
                        if self.browser == "chrome":
                            self.whenInChrome('overwritten')
                        # browser isn't chrome
                        else:
                            self.notUsingChrome('overwritten', method, element_specifier)
                    else:
                        # this block of code is needed in case the user enters 'n' when asked to overwrite the files when using chrome
                        # this is because the self.count will not increment itself because the baseline files are never being generated again. So if the user was to enter in n, the following baseline images
                        # would have numbers being appened that are all screwy. This fixes that by adding the correct # to the count. 
                        # the number we are generating is how many files have that certain description in the baseline directory. This is therefore the amount of #'s we need to 'skip' to get to 
                        # what the real value of self.count would be if the baselines were overwritten.
                        
                        # get list of files in the directory
                        files = os.listdir(self.baseline_location)
                        # iterate through the files
                        for i in files:
                            # check if the file name contains the description
                            if description in i:
                                # if so, increment the count.
                                self.count+=1
                else:
                    # cropping is not supported for chrome. due to the fact that chromedriver does not take fullscreen screenshots, have to manually
                    # scroll the browser window and take screenshots after each
                    # scroll.
                    # call the corresponding functions if using chrome or not, see function documentation.
                    if self.browser == "chrome":
                        self.whenInChrome('saved')
                    # browser isn't chrome.
                    else:
                        self.notUsingChrome('saved', method, element_specifier)
            # if it was not the baseline run.
            else:
                # if it is not the baseline run then we want to create the new
                # images that will be used to create the diff images.

                # create the filename for the new file. use description,
                # browser, operating system. note there is no _baseline
                file_name = str(description) + '_' + \
                    self.browser + '_' + op_sys + file_extension
                # add the directory where the file will be saved.
                self.file_path = os.path.join(self.new_location, file_name)

                # cropping is not supported for chrome. due to the fact that chromedriver does not take fullscreen screenshots, have to manually
                # scroll the browser window and take screenshots after each
                # scroll.
                # call the corresponding functions if using chrome or not, see function documentation.
                if self.browser == "chrome":
                    self.whenInChrome('saved')
                # browser isn't chrome
                else:
                    self.notUsingChrome('saved', method, element_specifier)

        else:
            print "[ERROR] You need to specify a description."
            raise Exception()

    """
    Params: mode - the mode this function is being used for (overwriting or saving). [REQUIRED]

    This function is called whenever the browser being used is chrome. It handles the generation and naming of images. It also
    handles the comparison of screenshots if it is not the baseline run

    Does everything for the chrome browser.
    """
    def whenInChrome(self, mode):
        # display the correct message to user depending on if baseline or not.
        if self.is_baseline:
            print "\nGenerating baseline images..."
        else:
            print "\nGenerating new images..."

        # javascript code that is executed by selenium driver to determine how many scrolls need to occur in order to capture
        # the whole page in screenshots.
        js_code = "window.scrollTo(0,0);var scrollValue=document.body.scrollHeight/window.innerHeight;return scrollValue;"

        # returns largest integer <= what the js code returns.
        # This was honestly figured out from pure trial and error.
        val = math.floor(self.driver.execute_script(js_code))

        # split the directory and file name so i can append the number to the beginning of the file name.
        split =  os.path.split(self.file_path)

        # add in the number specifier
        file_name = os.path.join(split[0], str(self.count) + '_' + split[1])
        self.count +=1

        # Take the initial screenshot of the page no scrolling occurred yet.
        # Note a specific number is being prepended to the beginning of the file name.
        # selenium's get_screenshot_as_file returns true if all is well.
        if self.driver.get_screenshot_as_file(file_name): 
            print "[SUCCESS] %s %s." % (os.path.basename(file_name), mode)
            # compare screenshots only if not baseline run.
            if not self.is_baseline:
                self.compareScreenshots(file_name)
        else:
            print "[ERROR] %s not %s." % (os.path.basename(file_name), mode)

        # only bother scrolling if the page needs to be scrolled. note this is compiled code.
        if self.driver.execute_script('window.scrollTo(0,1);return 0!=window.pageYOffset?(window.scrollTo(0,0),!0):(window.scrollTo(0,0),!1);'):
            i = 0
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
                    print "[SUCCESS] %s %s." % (os.path.basename(file_name), mode)
                    # compare screenshots only if not baseline run.
                    if not self.is_baseline:
                        self.compareScreenshots(file_name)
                else:
                    print "[ERROR] %s not %s." % (os.path.basename(file_name), mode)
                i+=1


    """
    Params: mode - the mode this function is being used for (overwriting or saving) [REQUIRED]
            method - the method to be sent to the cropElement function (see its documentation) [OPTIONAL], required if element_specifier is passed in
            element_specifier - the element specifier to be sent to the cropElement functio (see its documentation) [OPTIONAL], required if method is passed in

    This funct is called whenever the browser being used is not chrome. It handles generation and naming of images. Also, if it is not the baseline run it compares the screenshots
    """
    def notUsingChrome(self, mode, method, element_specifier):
        if self.is_baseline:
            print "\nGenerating baseline images..."
        else:
            print "\nGenerating new images..."
        # get_screenshot_as_file returns true if screenshot
        # was successfully saved.
        if self.driver.get_screenshot_as_file(self.file_path):
            print "[SUCCESS] %s %s." % (os.path.basename(self.file_path), mode)

            # if element_specifier was passed to the
            # function
            if element_specifier:
                # make sure user also passed in a valid
                # method.
                if method in VALID_METHODS:
                    # crop the element, returns true if
                    # successful. see function documentation below.
                    if self.cropElement(element_specifier, method):
                        print "[SUCCESS] %s cropped." % os.path.basename(self.file_path)
                    else:
                        print "[ERROR] %s not  %s." % (element_specifier, mode)
                else:
                    # user did not pass element_specifier
                    # and a valid method to the function.
                    msg = "[ERROR] invalid parameters, please make sure an element specifier AND a method are being passed, see valid methods: \n" + str(
                        VALID_METHODS)
                    self.driver.quit()
                    raise Exception(msg)
            if not self.is_baseline:
                # compare the newly generated screenshot w/ the baseline (if the baseline exists) see function documentation.
                self.compareScreenshots(self.file_path)
        else:
            print "[ERROR] %s not %s." % (os.path.basename(self.file_path), mode)

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
    Params: path_to_new_file: the path to the new file that was just generated that is to be compared with the baseline.
        Note: the filename of the new file and the filename of the baseline file are the same, they just differ by _baseline. So 
        adding this, we can generate what the baseline file name should be. (before we actually compare we make sure that this generated
        file name actually exists.)

    Compares the files only if they match. What i mean by match is that they have the same generated file name, minus the _baseline. 
    Calls imagemagick on the command line and saves the result in the difference file, which is a .gif and .png
    """
    def compareScreenshots(self, path_to_new_file):
        # get the file name, splitting off the path to the file.
        new_file_name = os.path.basename(path_to_new_file)
        # the baseline file is of the same form of the new file but it contains _baseline, so append this on.
        baseline_file_name = new_file_name.replace('.png', '_baseline.png')
        # add in the path to the baseline file, and now we have the full path to the baseline file.
        # note that we still do not know if this file exists, which is what the next if statement does.
        path_to_baseline_file = os.path.join(self.baseline_location, baseline_file_name)
        try:
            # make sure both the new file and baseline file exist.
            if os.path.exists(path_to_new_file) and os.path.exists(path_to_baseline_file):
                # generate the difference file name that will be saved
                # in the diff location. The file name is the same, all we have to do is add in _diff. Which is what is being done below.
                difference_file = os.path.abspath(
                    os.path.join(self.diff_location, new_file_name.replace('.png', '_diff.png')))
                # for the .gif version, everything else is the same
                # just change the extension.
                difference_file_gif = difference_file.replace(
                    '.png', '.gif')

                # compare the histograms of the 2 images, and if they are different then generate the diff image, otherwise no need to generate a diff image if the images havn't changed
                i1 = Image.open(path_to_baseline_file)
                i2 = Image.open(path_to_new_file)
                if i1.histogram() != i2.histogram():
                    print "Differences found, generating diff images..."
                    # keep track of the images reported as being changed.
                    self.difference_list.append(os.path.basename(new_file_name))

                   # the os.system calls below can be tweaked as desired, further digging into imagemagick's documentation may come up with a better way for comparison
                    os.system(
                        "composite %s %s -compose difference %s" %
                        (path_to_baseline_file, path_to_new_file, difference_file))
                    print "[SUCCESS] %s saved." % os.path.basename((difference_file))

                    # generate the .gif (pulled right from imagemagick's documentation)
                    os.system("convert -delay 100 %s %s -loop 0 %s" %
                              (path_to_baseline_file, path_to_new_file, difference_file_gif))
                    print "[SUCCESS] %s saved.\n" % os.path.basename(difference_file_gif)

                    # this imagemagick call can be commented in to have a different type of diff image generated (highlights differences in a blue.)
                    # remember to change the name of the file it will be saved as if desired. --> difference_file.replace('_diff.png', '_alternatediff.png') --> difference_file.replace('_diff.png', 'THE_FILE_NAME_YOU_WANT.png')
                    
                    # os.system("compare -dissimilarity-threshold 1 -fuzz 20% -metric AE -highlight-color blue " + baselines[i] + " " + newfiles[i] + " " + difference_file.replace('_diff.png', '_alternatediff.png'))
                
                else:
                    print "No differences found."
            else:
                # if the new file caused the above if statement to fail, notify the user with the specifics
                if not os.path.exists(path_to_new_file):
                    print "[ERROR] new file %s does not exist, can't compare." % new_file_name
                # if the baseline file caused the above if statement to fail, notify the user with the specifics
                elif not os.path.exists(path_to_baseline_file):
                    print "[ERROR] trying to compare with the baseline file %s, but it does not exist." % os.path.basename(path_to_baseline_file)

        # Could not find one of the baseline, new or diff folders. Did you delete them in the middle of running the program?
        except IOError:
            print "[ERROR] file or folder not found."


    """
    Called when object is destroyed (the desctructor). Notifies the user of the status and if any diffs were found.
    """
    def __del__(self):
        if not self.is_baseline:
            # if anything was added to the difference list, then we know there were difference files generated, notify the user which files changed.
            if len(self.difference_list) > 0:
                print "\n[INFO] the file(s) with differences are: \n" + '\n'.join(self.difference_list)
            else:
                print "\n[INFO] no differences found!"
    # to string.
    def __str__(self):
        return "Baseline: %s \nBrowser: %s" % (self.is_baseline, self.browser)