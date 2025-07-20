#!/usr/bin/python

import shutil

from selenium import webdriver
import selenium.common.exceptions


def get_driver():
    """

    Helps to grab webpages using headless Selenium.
    :return: driver

    """
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')

    # Start the Chrome Driver
    try:
        driver = webdriver.Chrome(options=options)  # sudo apt install chromium-chromedriver
    except selenium.common.exceptions.NoSuchDriverException:
        chromedriver_path = shutil.which("chromedriver")
        service = webdriver.ChromeService(executable_path=chromedriver_path)
        driver = webdriver.Chrome(options=options, service=service)

    return driver


#driver.get('https://pacific.afn.mil/Gas-Prices/')
#page_source = driver.page_source