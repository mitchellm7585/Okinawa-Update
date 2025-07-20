#!/usr/bin/python

import logging

import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO
from re import match
from datetime import datetime, date

from dotenv import load_dotenv
from os import getenv as env

from get_website import get_website
from ntfy import ntfy

load_dotenv()

def get_jpy():
    """ Get JPY exchange rate from Yahoo finance"""

    with open('latest_rate.txt', 'r') as file:
        rate = file.read()

    return float(rate)


def get_gas_prices():
    """ Parse the Gas Prices website and find values for Okinawa. """

    gas_data = get_website('BASE_GAS_PRICES')
    tables = None
    pattern = r"<h4>[\w]+\s([\d]+)\s([\w]{3})[\w]*,\s([\d]+)</h4>"  # Limited month to first 3 characters to match locale Sep

    today = date.today()

    if type(gas_data) == str:
        soup = BeautifulSoup(gas_data, 'html.parser')
    else:
        content = gas_data.text
        soup = BeautifulSoup(content, 'html.parser')

    eff_date = str(soup.find_all('h4')[0])
    day, month, year = match(pattern, eff_date).groups()
    data_date = datetime.date(datetime.strptime(f"{day} {month} {year}", "%d %b %Y"))

    if data_date != today:
        logger.info(f'The listed gas prices are dated {data_date}')
        return 0
    else:
        table = soup.find_all('table')[-1]
        tables = pd.read_html(StringIO(str(table)))
        _gas_prices = tables[0].get('Okinawa') if tables is not None else None

        # Get central bank exchange rate
        jpy = get_jpy()

        # Add JPY equivalent
        prices = [round(float(price[1:]) * jpy, 3) for price in _gas_prices.get('Per Liter')]
        _gas_prices.insert(3, 'JPY Per Liter', prices)

        # Test items
        _gas_prices.set_index("Fuel Type")
        lines = ""
        for row in _gas_prices.to_dict('split').get('data'):
            _type, _price, _per_liter, _yen_liter, _change = row[0:5]
            lines += f"{_type} @ {_price} per gallon.\nPer Liter: {_per_liter}\nYen Per Liter: ¥{_yen_liter}\n\n"

        return lines


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    FORMAT = '%(asctime)s %(message)s'
    logging.basicConfig(filename='base_gas.log', format=FORMAT, level=logging.INFO)
    logger.info('Started')
    gas_prices = get_gas_prices()
    if gas_prices:
        logger.info('Posting')
        ntfy(url="GAS_PRICES_POST",
             data=f"Okinawa Gas Prices\n\n{gas_prices}".encode(encoding='utf-8'),
             headers={"Tags": "car",
                     "Title": "Base Gas Prices",
                     "Click": f"{env('BASE_GAS_PRICES')}"}
        )
    logger.info('Finished')
