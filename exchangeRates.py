from bs4 import BeautifulSoup
from re import findall


def exchange_rates(chance_data, lucky_data):
    """ Obtain exchange rates from Chance and Lucky exchange. """

    chance_yen_rate = 0
    chance_dollar_rate = 0
    if chance_data.status_code == 200:
        chance_content = chance_data.text
        chance_soup = BeautifulSoup(chance_content, 'html.parser')
        chance_rates = chance_soup.find("div", {"class": "elementor-post__excerpt"})
        chance_yen_rate, chance_dollar_rate = findall(r'(\d+\.\d+)', str(chance_rates))

    lucky_yen_rate = 0
    lucky_dollar_rate = 0
    if lucky_data.status_code == 200:
        lucky_content = lucky_data.text
        lucky_soup = BeautifulSoup(lucky_content, 'html.parser')
        lucky_rates = lucky_soup.find(id="entryBody")
        lucky_yen_rate, lucky_dollar_rate = findall(r'(\d+\.\d+)', str(lucky_rates))

    return chance_yen_rate, chance_dollar_rate, lucky_yen_rate, lucky_dollar_rate
