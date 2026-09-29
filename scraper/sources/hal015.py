"""HAL015's complete public tickets listing (server-rendered event cards)."""

import re
from bs4 import BeautifulSoup

from scraper.fetch import fetch_page
from scraper.normalize import whitespace
from scraper.parsing import ParseError, parse_cards, required_text

URL = "https://hal015.nl/tickets/"
NAME = "HAL015"
DATE_LINE = re.compile(r"(\d{1,2}\s+[a-z]+\s+\d{4})\s*[·|•]\s*(\d{1,2}:\d{2})", re.I)


def parse_page(html):
    soup = BeautifulSoup(html, "html.parser")

    def extract(card):
        link = card.select_one("h3 a[href]")
        stamp = whitespace(required_text(card.select_one(".hal-event-date")))
        match = DATE_LINE.fullmatch(stamp)
        if not match or link is None:
            raise ParseError("Missing date/time or event link")
        return {"title": required_text(link), "date": match[1], "startTime": match[2],
                "venue": NAME, "url": link["href"]}

    return parse_cards(soup.select("article.hal-event-card"), extract, source=NAME, base_url=URL)


def scrape_events():
    return parse_page(fetch_page(URL))
