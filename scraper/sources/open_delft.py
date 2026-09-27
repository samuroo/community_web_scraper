"""OPEN's full agenda embeds dates in outgoing event URLs; no extra fetches."""

import re
from bs4 import BeautifulSoup

from scraper.fetch import fetch_page
from scraper.normalize import time_range
from scraper.parsing import ParseError, parse_cards, required_text

URL = "https://www.opendelft.info/agenda"
NAME = "OPEN Delft"


def parse_page(html):
    soup = BeautifulSoup(html, "html.parser")

    def extract(card):
        link = card.select_one(".activity__description a[href]")
        if link is None:
            raise ParseError("Missing event link")
        match = re.search(r"/(\d{2}-\d{2}-\d{4})(?:[/?#]|$)", link["href"])
        if not match:
            raise ParseError("Event URL has no explicit date/year; not guessing")
        start, end = time_range(required_text(card.select_one(".activity__datetime .activity__time")))
        return {"title": required_text(card.select_one(".activity__description h3")),
                "date": match[1], "startTime": start, "endTime": end,
                "venue": required_text(card.select_one(".meta__location")), "url": link["href"]}

    return parse_cards(soup.select(".calendar .calendar__activity"), extract, source=NAME, base_url=URL)


def scrape_events():
    return parse_page(fetch_page(URL))
