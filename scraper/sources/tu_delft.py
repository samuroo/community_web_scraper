"""Studium Generale's public programme, not TU internal/staff activities.

https://www.tudelft.nl/sg/about-us explicitly welcomes all visitors.
Coverage is this programme only, not the whole university agenda.
"""

import re
from bs4 import BeautifulSoup

from scraper.fetch import fetch_page
from scraper.normalize import time_range
from scraper.parsing import ParseError, parse_cards, required_text

URL = "https://www.tudelft.nl/sg/events"
NAME = "TU Delft"


def parse_page(html):
    soup = BeautifulSoup(html, "html.parser")

    def extract(card):
        stamp = required_text(card.select_one(".label-eventData"))
        date = re.match(r"\d{1,2}\s+[a-z]+\s+\d{4}", stamp, re.I)
        if not date:
            raise ParseError("Missing full event date")
        start, end = time_range(stamp[date.end():])
        return {"title": required_text(card.select_one("h3")), "date": date[0],
                "startTime": start, "endTime": end, "venue": "TU Delft / Studium Generale",
                "url": card["href"]}

    cards = soup.select('a.card[href^="/evenementen/"]')
    return parse_cards(cards, extract, source=NAME, base_url=URL)


def scrape_events():
    return parse_page(fetch_page(URL))
