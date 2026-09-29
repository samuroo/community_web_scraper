"""Investigation-only adapter: official programme is behind a bot challenge.

29 September 2026: robots.txt redirects to /csq/ with x-redirect-reason:
no-token. Do not run a browser to bypass that challenge or invent selectors.
"""

from scraper.fetch import fetch_page
from scraper.parsing import ParseError

URL = "https://www.theaterdeveste.nl/programma"
NAME = "Theater de Veste"


def parse_page(html):
    raise ParseError("Parser not implemented: official HTML inspection blocked by /csq/ bot protection")


def scrape_events():
    return parse_page(fetch_page(URL))
