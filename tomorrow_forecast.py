#!/usr/bin/python

import logging
from dotenv import load_dotenv

from get_website import get_website
from ntfy import ntfy

load_dotenv()


def get_weather():
    """Retrieves tomorrow's weather forecast from Acuweather"""

    weather_api = get_website('GUSHIKAWA_TOMORROW')

    weather = ''
    link = ''

    if weather_api.status_code == 200:
        forecast = weather_api.json()['DailyForecasts'][1]
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
    logging.basicConfig(filename='tomorrow_forecast.log', format=FORMAT, level=logging.INFO)
    logger.info('Started')

    weather, link = get_weather()
    ntfy(url="WEATHER_POST",
         data=f"{weather}\n\nweather courtesy of accuweather.com".encode(encoding='utf-8'),
         headers={"Tags": "thermometer",
                  "Title": "Tomorrow\'s Forecast",
                  "Click": link}
         )

    logger.info('Finished')
