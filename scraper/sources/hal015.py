"""Provisional text-order parser for HAL015's 'Binnenkort' homepage listing.

The public text view shows date/time followed by a linked title. Raw live HTML
was unavailable (HTTP 429), so this deliberately does not guess CSS classes.
Verify against real HTML when the site is available; see fixtures/README.md.
"""

import re
from bs4 import BeautifulSoup

from scraper.fetch import fetch_page
from scraper.normalize import whitespace
from scraper.parsing import ParseError, parse_cards

URL = "https://hal015.nl/"
NAME = "HAL015"
DATE_LINE = re.compile(r"(\d{1,2}\s+[a-z]+\s+\d{4})\s*[·|•]\s*(\d{1,2}:\d{2})", re.I)


def parse_page(html):
    soup = BeautifulSoup(html, "html.parser")
    for node in soup(["script", "style", "nav", "footer"]):
        node.decompose()
    links = {}
    for link in soup.find_all("a", href=True):
        links.setdefault(whitespace(link.get_text(" ", strip=True)), link["href"])
    lines = [whitespace(text) for text in soup.stripped_strings]
    try:
        start = lines.index("Binnenkort") + 1
    except ValueError as error:
        raise ParseError("HAL015 'Binnenkort' listing not found; live HTML verification needed") from error
    raw = []
    for index in range(start, len(lines) - 1):
        match = DATE_LINE.fullmatch(lines[index])
        if match:
            title = lines[index + 1]
            raw.append({"title": title, "date": match[1], "startTime": match[2],
                        "venue": NAME, "url": links.get(title)})
    return parse_cards(raw, lambda event: event, source=NAME, base_url=URL)


def scrape_events():
    return parse_page(fetch_page(URL))
