#!/usr/bin/python

import logging
from dotenv import load_dotenv
from os import getenv as env
from requests_html import HTMLSession

logger = logging.getLogger(__name__)
FORMAT = '%(asctime)s %(message)s'
load_dotenv()


def get_weather():
    """Retrieves tomorrow's weather forecast from Acuweather"""

    with HTMLSession() as session:
        weather_api = session.get(env('GUSHIKAWA_TOMORROW'))

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


def ntfy():
    """Send notification"""

    logging.basicConfig(filename='tomorrow_forecast.log', format=FORMAT, level=logging.INFO)
    logger.info('Started')
    weather, link = get_weather()

    with HTMLSession() as session:
        logger.info('Posting')
        session.post(f"{env('WEATHER_POST')}",
                     data=f"{weather}\n\nweather courtesy of accuweather.com".encode(encoding='utf-8'),
                     headers={"Tags": "thermometer",
                              "Title": "Tomorrow\'s Forecast",
                              "Click": link}
                     )
    logger.info('Finished')


if __name__ == "__main__":
    ntfy()
