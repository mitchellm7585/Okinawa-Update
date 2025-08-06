#!/usr/bin/python

import sys
import logging
from dotenv import load_dotenv

from get_website import get_website
from ntfy import ntfy

load_dotenv()


def get_weather(today=True):
    """
    Retrieves the weather forecast from Accuweather

    :param today: day of forecast
    :type today: bool
    :return weather
    :rtype: str
    :return link
    :rtype: str
    """

    weather_api = get_website('GUSHIKAWA') if today else get_website('GUSHIKAWA_TOMORROW')

    weather = ''
    link = ''

    if weather_api.status_code == 200:
        data = weather_api.json()['DailyForecasts']
        forecast = data[0] if today else data[1]
        min_temp = forecast['Temperature']['Minimum']['Value']
        max_temp = forecast['Temperature']['Maximum']['Value']
        day_summary = forecast['Day']['LongPhrase']
        night_summary = forecast['Night']['LongPhrase']
        weather = (f'Temperature: {min_temp}\N{DEGREE SIGN}C - {max_temp}\N{DEGREE SIGN}C\n\n'
                   f'Day: {day_summary}\n\nNight: {night_summary}')
        link = forecast['MobileLink']

    return weather, link


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    FORMAT = '%(asctime)s %(message)s'
    logging.basicConfig(filename='weather.log', format=FORMAT, level=logging.INFO)
    logger.info('Started')

    # Today = False if empty or no string
    try:
        today = bool(sys.argv[1])
    except IndexError:
        today = False

    day = "Today" if today else "Tomorrow"

    weather, link = get_weather(today)

    ntfy(url="WEATHER_POST",
         data=f"{day}\'s Weather courtesy of accuweather.com\n\n"
              f"{weather}".encode(encoding='utf-8'),
         headers={"Tags": "thermometer",
                  "Title": f"{day}\'s Forecast",
                  "Click": link}
         )

    logger.info('Finished')