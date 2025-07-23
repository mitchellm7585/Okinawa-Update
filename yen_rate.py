#!/usr/bin/python

from dotenv import load_dotenv
from bs4 import BeautifulSoup
import logging

from get_website import get_website
from ntfy import ntfy

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


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    FORMAT = '%(asctime)s %(message)s'
    logging.basicConfig(filename='yen_rate.log', format=FORMAT, level=logging.INFO)
    logger.info('Started')

    _rate = get_jpy()

    ntfy(url="EXCHANGE_POST",
         data=f"¥{_rate}".encode(encoding='utf-8'),
         headers={"Tags": "yen",
                  "Title": "Today\'s Yen Rate"}
         )

    logger.info('Finished')
