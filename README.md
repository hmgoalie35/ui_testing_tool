ui_testing_tool
===============

Utilizes ImageMagick and Selenium to test UI elements that may have changed due to css or html changes

For info and a getting started guide, see template.py. The ui_testing.py code is also very well documented so delve into that for more info. See the demo and ui_test_examples folders to see what the program does.

Extremely basic example, see the baseline and new images to see what changed. Below are the diff images.

The .gif generated

![ui_testing_gif](https://raw.githubusercontent.com/hmgoalie35/ui_testing_tool/master/ui_testing_examples/chrome/diff/1_whats_up_link_chrome_windows_diff.gif)

The .png generated

![ui_testing_png](https://raw.githubusercontent.com/hmgoalie35/ui_testing_tool/master/ui_testing_examples/chrome/diff/1_whats_up_link_chrome_windows_diff.png)

The beauty is that these diff images can be tweaked as you desired, just dig into ImageMagick's documentation and then change the os.system call in the ui_testing.py

Dependencies (Linux):

```
sudo apt-get imagemagick
[sudo] pip install selenium
[sudo] pip install pillow
```

Other OS's 

ImageMagick

http://www.imagemagick.org/script/binary-releases.php

Selenium

http://docs.seleniumhq.org/download/

In order to use Chrome, IE or Safari with selenium you will need to download the appropriate drivers. See above.

PIL

http://www.pythonware.com/products/pil/

Use:

Beware that if you are running the script again in baseline mode, then you might be generating file names that already exist, the selenium program may seem like it is stuck, but just go to the terminal window and there should be a prompt to overwrite the file or not.

The status of every operation is logged in the console.

In your selenium code, create a ui_testing object, passing in the driver, browser and True or False if the run is baseline or not. Make sure ui_testing.py is in the same folder as the selenium script you are writing, or see the template.py file for instructions on running scripts in different directories from the ui_testing.py file.
```
from selenium import webdriver
self.driver = webdriver.Firefox()
ui = ui_testing(self.driver, 'firefox', True)# change True to False to run in non-baseline mode and generate diff images (if any)
```
You can now use all of the functions in the ui_testing module.

This will take a screenshot and label the output file with the description 'test_1' file name will be test_1_firefox_linux_baseline.png. this varies depending on OS and browser being used.

```
ui.generateFileNameAndTakeScreenshot('test_1')
# selenium code
# selenium code
```

say there is an anchor tag on the page with the id back_btn

```
<a href="http://www.google.com" id='back_btn' style="color:red;">Press Me</a>
```
the below line will take a screenshot and then crop the image to just this anchor tag.
'id' is passed to tell the function that it should search for the element by id. There are also other possibilities such as xpath, css name, etc. See ui_testing.py for more info. (cropping only supported when using firefox, due to a limitation of chromedriver.)
```
ui.generateFileNameAndTakeScreenshot('test_2', 'id', 'back_btn')

```

After you have run the baseline mode, running in non baseline mode will automatically generate diff files if there were any differences found b/w the baseline and new files. (no need to call the compareScreenshots() method, which was previously needed)

Running the script:
Just run your selenium code as you would.

Terminal output looks like this.

```
[SUCCESS] test_1_firefox_linux_baseline.png saved.
```

Remember to first generate your baseline images.

Shoot me an email if you have any questions, hpittin1@binghamton.edu
