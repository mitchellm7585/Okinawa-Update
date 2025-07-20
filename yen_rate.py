#!/usr/bin/python

from requests_html import HTMLSession
from dotenv import load_dotenv
from os import getenv as env
from bs4 import BeautifulSoup
from re import findall
from collections import defaultdict
import logging

from get_website import get_website

logger = logging.getLogger(__name__)
FORMAT = '%(asctime)s %(message)s'
load_dotenv()


def get_jpy():
    """ Get JPY exchange rate from Yahoo finance"""

    yf = get_website('JPY_RATE')

    if type(yf) is str:
        soup = BeautifulSoup(yf, 'html.parser')
        rate = soup.find_all('fin-streamer', class_="livePrice")[0].text
    else:
        pass

    with open('latest_rate.txt', 'w') as file:
        file.write(rate)

    return rate


def ntfy():
    """Post notification"""

    logging.basicConfig(filename='yen_rate.log', format=FORMAT, level=logging.INFO)
    logger.info('Started')
    rate = get_jpy()

    with HTMLSession() as session:
        logger.info('Posting')
        session.post(f"{env('EXCHANGE_POST')}",
                     data=f"¥{rate}".encode(encoding='utf-8'),
                     headers={"Tags": "yen",
                              "Title": "Today\'s Yen Rate"}
                     )
    logger.info('Finished')


if __name__ == "__main__":
    ntfy()
