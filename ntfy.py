#!/usr/bin/python

"""Pushes information to ntfy"""
from requests_html import HTMLSession

from dotenv import load_dotenv
from os import getenv as env

load_dotenv()


def ntfy(url, data, headers):
    """Post notification

    :param url: url for post location
    :type url: str
    :param data: data to be posted
    :type data: bytes
    :param headers: values for notification Tags, Title, and Click actions
    :type headers: dict
    :returns 1 when complete
    """

    with HTMLSession() as session:
        session.post(f"{env(url)}",
                     data=data,
                     headers=headers
                     )

    return 1