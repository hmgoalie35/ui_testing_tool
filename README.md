ui_testing_tool
===============

Utilizes ImageMagick and Selenium to test UI elements that may have changed due to css or html changes


Dependencies (Linux):

```
sudo apt-get imagemagick
[sudo] pip install selenium
[sudo] pip install pillow
```

For other OS's http://www.imagemagick.org/script/binary-releases.php

See the selenium documentation http://docs.seleniumhq.org/download/

In order to use Chrome, IE or Safari with selenium you will need to download the appropriate drivers.

PIL -- http://www.pythonware.com/products/pil/

Use:
In your selenium code, create a ui_testing object, passing in the driver. Make sure ui_testing.py is in the same folder as the selenium script you are writing, or see the template.py file. 
```
from selenium import webdriver
self.driver = webdriver.Firefox()
ui = ui_testing(self.driver)
```
You can now use all of the functions in the ui_testing module.

```Python
# This will take a screenshot and label the output file with the description 'test_1'
ui.generateFileNameAndTakeScreenshot('test_1')
# selenium code
# selenium code
```
say there is an anchor tag on the page

```
<a href="http://www.google.com" id='back_btn' style="color:red;"><Press Me</a>
```
the below line will take a screenshot and then crop the image to just this anchor tag.
'id' is passed to tell the function that it should search for the element by id. There are also other possibilities such as xpath, css name, etc. See ui_testing.py for more info.
```
ui.generateFileNameAndTakeScreenshot('test_2', 'id', 'back_btn'

```
When you are all done taking screenshots, the last line of code has to be. It is also good practice to quit the driver before comparing the screenshots.
```
self.driver.quit()
ui.compareScreenshots()
```
Running the script:
on the command line
the first time you run the program you need to generate baseline images. That is what the --baseline flag is for it is an optional flag.
--browser is required for every run. make sure that you have the appropriate drivers installed for running chrome, IE, etc.
```
python yourFile.py --baseline --browser chrome
```
Alternatively, below will generate the new images on chrome.
```
python yourFile.py --browser chrome 
```
