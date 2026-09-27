"""Very Simple Event List entries on the venue's events page."""

from bs4 import BeautifulSoup

from scraper.fetch import fetch_page
from scraper.normalize import time_range
from scraper.parsing import parse_cards, required_text

URL = "https://delftsbrouwhuis.nl/events/"
NAME = "Delfts Brouwhuis"


def parse_page(html):
    soup = BeautifulSoup(html, "html.parser")

    def extract(card):
        title = card.select_one(".vsel-meta-title")
        link = title.find("a", href=True) if title else None
        start, end = time_range(required_text(card.select_one(".vsel-meta-time")))
        return {"title": required_text(title),
                "date": required_text(card.select_one(".vsel-meta-date")),
                "startTime": start, "endTime": end, "venue": NAME,
                "url": link["href"] if link else f"{URL}#{card['id']}"}

    return parse_cards(soup.select("#vsel .vsel-content"), extract, source=NAME, base_url=URL)


def scrape_events():
    return parse_page(fetch_page(URL))
