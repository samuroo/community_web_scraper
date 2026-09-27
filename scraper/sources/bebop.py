"""The public shop agenda contains each occurrence and its dated ticket URL."""

import re
from bs4 import BeautifulSoup

from scraper.fetch import fetch_page
from scraper.normalize import time_range
from scraper.parsing import ParseError, parse_cards, required_text

URL = "https://shop.jazzcafebebop.nl/"
NAME = "Bebop"


def parse_page(html):
    soup = BeautifulSoup(html, "html.parser")

    def extract(card):
        link = card.select_one(".event-summary__action a[href]")
        if link is None:
            raise ParseError("Missing occurrence link")
        match = re.search(r"/date/\d+/(\d{4}-\d{2}-\d{2})(?:[/?#]|$)", link["href"])
        if not match:
            raise ParseError("Ticket URL has no explicit occurrence date")
        start, end = time_range(required_text(card.select_one(".event-summary__date")))
        return {"title": required_text(card.select_one(".event-summary__title")),
                "date": match[1], "startTime": start, "endTime": end,
                "venue": "Jazz Cafe Bebop", "url": link["href"]}

    return parse_cards(soup.select(".event-list .event-summary"), extract, source=NAME, base_url=URL)


def scrape_events():
    return parse_page(fetch_page(URL))
