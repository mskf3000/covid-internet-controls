#!/usr/bin/env python3

import logging

import coloredlogs
import requests
from bs4 import BeautifulSoup

logging.getLogger("scapy").setLevel(logging.ERROR)
logging.getLogger("requests").setLevel(logging.WARNING)

log = logging.getLogger(__name__)
coloredlogs.install(level="INFO", fmt="%(message)s")


BASE_URL = "https://www.alexa.com/topsites/countries"
COUNTRIES = ["CN"]


def get_top_sites(country_code: str) -> list:
    """ Get the Alexa top sites for a given country code. """

    sites = []
    url = BASE_URL + "/" + country_code
    response = requests.get(url)

    soup = BeautifulSoup(response.text, features="lxml")
    bullets = soup.find_all("div", {"class": "site-listing"})

    for bullet in bullets:
        site_url = bullet.find("div", {"class": "DescriptionCell"})
        sites.append(site_url.text.strip())

    return sites


if __name__ == "__main__":
    top_sites_by_country = {}
    for country_code in COUNTRIES:
        top_sites_by_country[country_code] = get_top_sites(country_code)

    print(top_sites_by_country)
