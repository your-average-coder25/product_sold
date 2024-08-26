
# Pip if selenium or webdriver_manager is not installed already
from selenium import webdriver
#https://pypi.org/project/webdriver-manager/
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
#https://selenium-python.readthedocs.io/locating-elements.html
from selenium.webdriver.common.by import By
import time
#https://pypi.org/project/print-color/
from print_color import print

#https://pypi.org/project/pandas/
import pandas

import os
from dotenv import load_dotenv
from pathlib import Path
import re

#variables that are hidden so they aren't accidentally pushed into github
#variables are all called using os.environ[variableName]
dotenv_path = Path('local.env')
load_dotenv(dotenv_path=dotenv_path)

#File path to where your chromedrive is located. Should be in the same directory as your project
PATH = os.environ["CHROMEDRIVER_PATH"]

#Had to add the handling in the next three lines because the chrome service stopped working the previous way it was done
chrome_install = ChromeDriverManager().install()
folder = os.path.dirname(chrome_install)
chromedriver_path = os.path.join(folder, PATH)

options = webdriver.ChromeOptions()
#Mainly used to reduce some messages on command line so it isn't as cluttered
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
options.add_argument("--disable-proxy-certificate-handler")
#driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
driver = webdriver.Chrome(service=ChromeService(chromedriver_path),options=options)

lightspeedLoginURL = "https://manager.lsk.lightspeed.app/"
driver.get(lightspeedLoginURL)

usernameTextBox = driver.find_element(By.XPATH,'//*[@id="username"]')

pwTextBox = driver.find_element(By.XPATH,'//*[@id="password"]')

loginButton = driver.find_element(By.XPATH,'//*[@id="login"]/div[3]/button')


usernameTextBox.send_keys(os.environ["LIGHTSPEED_USERNAME"])
pwTextBox.send_keys(os.environ["LIGHTSPEED_PASSWORD"])
loginButton.click()
#YYYY-MM-DD
startDate="2024-02-05"
endDate="2024-02-18"

driver.get(f'https://manager.lsk.lightspeed.app/stats/productBreakdown/custom/{startDate}/{endDate}')
print("Product sales")

#Full Table Path
#tableXPath = '/html/body/div[2]/div/div[2]/section/div[5]/div/table'
#Table Body XPath
#Tried using full XPath but it seems like the website can eventually change the path down the line. So maybe don't use full xpaths
tableXPath = '/html/body/div[2]/div/div[2]/section/div[5]/div/table/tbody'
#This seems to be a relative XPath I think it looks for the first instance of table then tbody. The page seems to have 2 table but the one we are interested in is the first one.
tableXPath2 = '//table/tbody'
tableClass = "table table-condensed table-stripped table-bordered breakdown"
tableTag = "table"

time.sleep(5)

table = driver.find_element(By.XPATH, tableXPath2)

rows = table.find_elements(By.XPATH, ".//tr")
print("Number of Rows: " + str(len(rows)))

csvFile = pandas.DataFrame(data=None,columns=('textField', 'posID', 'quantity', 'regular', 'large', 'noSize', 'optionsList'))

for i in range(len(rows)):
    posID = 'NA'
    quantity = 'NA'
    regular = 'NA'
    large = 'NA'
    noSize = 'NA'
    optionsList = 'NA'
    firstColumn = rows[i].find_element(By.XPATH, ".//td")
    #Likely Removed because it errored when searching for quantity in this step. Might look for a way to do it here in the future
    #quantity = rows[i].find_element(By.XPATH, ".//td[3]").text
    
    #Used for debuggin to see if there is actually any data.
    print(f"Element {i}:{len(rows[i].text)} characters")
    print(f"Quantity: {quantity}")
    
    if len(firstColumn.text) == 0: #rows[i].is_displayed(): I'd like to use this function but it seems to think some visible rows aren't visible. 
        print(f"Sub Element Not visible: {i}", color = 'red')
        print("Clicking previous carat to expand table")
        rows[i-1].find_element(By.XPATH, ".//td[1]/a/i").text
        rows[i-1].find_element(By.XPATH, ".//td[1]/a/i").click()
    firstColumnText = firstColumn.text
    print("First Column Text: " + firstColumnText);
    
    #Retrieves quantity sold of this specific item
    quantity = rows[i].find_element(By.XPATH, ".//td[3]").text
    
    try:
        #The text first needs to be clicked to show the options for the item
        firstColumn.find_element(By.XPATH, './/a[@class="ik-popover"]').click()
        # Needs enough time for the popover to appear on screen. Time is in seconds
        time.sleep(2)
        productOptions = firstColumn.find_element(By.XPATH, './/div')
        optionsList = productOptions.text
        #driver.execute_script("arguments[0].setAttribute('style.display', 'none')",firstColumn.find_element(By.XPATH, './/a[@class="ik-popover"]'))
        #This works but it removes the entire text field not just the pop up. Might have to find soluction that just sets the popup to none and just closes it instead of deletes the data 
        #S o you can really review the work at the end of the script. You have to log in and check the same dates.
        #This was required because the popup would remain up and be in the way and make the carat button unclickable.
        popoverWithOptions = firstColumn.find_element(By.XPATH, './/a[@class="ik-popover"]')
        #driver.execute_script("arguments[0].style.display = 'none';",popoverWithOptions)
        driver.execute_script("arguments[0].style.visibility = 'hidden';",firstColumn.find_element(By.XPATH, './/div'))
        print("popover found", color='green')
        print(optionsList)
        
        optionsListRows = optionsList.split("\n")
        #ProductID is enclosed in parenthesis
        searchID = re.search('\((\d+?)\)$', optionsListRows[0])
        if searchID:
            productID = searchID.group(1)        
        hasRegular = 0
        hasLarge = 0

        for j in optionsListRows:
            #Added x because some item names have large and regular part of their name
            if 'x Large' in j:
                large = j.split('x')[0]
                hasLarge = 1
            elif 'x Regular' in j:
                regular = j.split('x')[0]
                hasRegular = 1
        if not hasLarge and not hasRegular:
            noSize = quantity
        csvFile.loc[len(csvFile)] = [firstColumnText,productID, quantity, regular, large, noSize, optionsList]
    except:
        #Popover does not exist so we will move on to the next one
        print("popover not found", color = 'red')
#Prints out a small sample of the resulting file        
print(csvFile, color = 'yellow')
csvFile.to_csv('product_sold_' + startDate + '_to_' + endDate + '.csv', sep=',')
wait = input("Wait for input")