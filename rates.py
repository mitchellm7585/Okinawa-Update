#!/usr/bin/python

from requests_html import HTMLSession
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from re import findall
from collections import defaultdict
import logging
import sys, traceback

from get_website import get_website
from ntfy import ntfy

load_dotenv()


def extract_rates(data, **kwargs):
    """Extract yen and dollar rates from HTML data"""

    yen_rate = 0
    dollar_rate = 0

    if data.status_code == 200:
        content = data.text
        soup = BeautifulSoup(content, 'html.parser')
        rates = soup.find(**kwargs).text  # Added .text to strip html (fixes Uluma error)

        try:  # Added try statement to troubleshoot error with Uluma
            yen_rate, dollar_rate = findall(r'(\d+\.\d+)', str(rates))[:2]
        except ValueError:
            traceback.print_exc()
            logger.error(f'Error:\t{rates}')
            sys.exit(1)

    return float(yen_rate), float(dollar_rate)


def local_rates():
    """Obtain exchange rates from local exchanges"""

    with HTMLSession() as session:
        chance_data = get_website('CHANCE_EXCHANGE')
        lucky_data = get_website('LUCKY_EXCHANGE')
        uluma_data = get_website('ULUMA_EXCHANGE')

    chance_yen_rate, chance_dollar_rate = extract_rates(chance_data, name="div",
                                                        attrs={"class": "elementor-post__excerpt"})
    lucky_yen_rate, lucky_dollar_rate = extract_rates(lucky_data, id="entryBody")
    uluma_yen_rate, uluma_dollar_rate = extract_rates(uluma_data, id="entryBody")

    unique_yen_rates = {'Chance': chance_yen_rate,
                        'Lucky': lucky_yen_rate,
                        'Uluma': uluma_yen_rate
                        }

    unique_dollar_rates = {'Chance': chance_dollar_rate,
                           'Lucky': lucky_dollar_rate,
                           'Uluma': uluma_dollar_rate
                           }

    yen_rates = defaultdict(list)
    dollar_rates = defaultdict(list)

    for key, value in unique_yen_rates.items():
        yen_rates[value].append(key)

    for key, value in unique_dollar_rates.items():
        dollar_rates[value].append(key)

    yen_rate = [f"{', '.join(place[:-1])}, and {place[-1]} Exchange: {rate}" if len(place) > 1 else
                f"{place} Exchange: {rate}" for rate, place in yen_rates.items()]
    dollar_rate = [f"{', '.join(place[:-1])}, and {place[-1]} Exchange: {rate}" if len(place) > 1 else
                   f"{place} Exchange: {rate}" for rate, place in dollar_rates.items()]

    return yen_rate, dollar_rate


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    FORMAT = '%(asctime)s %(message)s'
    logging.basicConfig(filename='rates.log', format=FORMAT, level=logging.INFO)
    logger.info('Started')

    yen_rate, dollar_rate = local_rates()
    yen_rates = '\n'.join(yen_rate)
    dollar_rates = '\n'.join(dollar_rate)

    ntfy(url="EXCHANGE_POST",
         data=f"¥\n{yen_rates}\n\n¥\n{dollar_rates}".encode(encoding='utf-8'),
         # Dollar to Yen and Yen to Dollar
         headers={"Tags": "currency_exchange",
                  "Title": "Exchange Rates"}
         )
    logger.info('Finished')