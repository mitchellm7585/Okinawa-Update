#!/usr/bin/python

import logging
from os import getenv as env

from requests_html import HTMLSession
from dotenv import load_dotenv

from get_driver import get_driver

logger = logging.getLogger(__name__)
FORMAT = '%(asctime)s %(message)s'
load_dotenv()


def get_website(website: str):
    """
    Grabs webpage data using requests with headless Selenium used as a backup via the get_driver script.
    :return: website_data

    """
    with HTMLSession() as session:
        website_data = session.get(env(website))

    if website_data.status_code != 200:
        logger.info(f'Status Code: {website_data.status_code}; Could not obtain the website using the requests module.')
        driver = get_driver()
        driver.get(env(website))
        website_data = driver.page_source
    else:
        pass

    return website_data

