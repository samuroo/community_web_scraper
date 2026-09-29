"""Public agenda payload used by cultuurlab.nl/js/script.js (fillagenda).

Fetch the same first-party data as the page; no JS execution is necessary.
Only explicit Aanvang/Vanaf times are used, never doors or 'timeofday'.
"""

from html import unescape
import json
import re
from bs4 import BeautifulSoup

from scraper.fetch import fetch_page
from scraper.parsing import ParseError, parse_cards

URL = "https://cultuurlab.nl/"
DATA_URL = "https://cultuurlab.nl/interactive/agenda.php?active=1"
NAME = "Cultuurlab"


def parse_page(text):
    data = json.loads(text)
    if not isinstance(data, dict) or not isinstance(data.get("rows"), list):
        raise ParseError("Missing public agenda rows")
    rows = [row for row in data["rows"] if not row.get("cancelled")]
    if not rows:
        return []

    def extract(row):
        info = BeautifulSoup(row.get("info") or "", "html.parser").get_text(" ")
        start = re.search(r"\b(?:Aanvang|Vanaf)\s*:?\s*(\d{1,2}[:.]\d{2})\b", info, re.I)
        end = re.search(r"\bEinde\s*:?\s*(\d{1,2}[:.]\d{2})\b", info, re.I)
        if not start:
            raise ParseError(f"{row.get('event')}: no advertised start time (doors alone are not a start)")
        title = BeautifulSoup(unescape(row["event"]), "html.parser").get_text(" ", strip=True)
        return {"title": title, "date": row["date"], "startTime": start[1],
                "endTime": end[1] if end else None, "venue": NAME,
                "url": row.get("ticketshop") or URL}

    return parse_cards(rows, extract, source=NAME, base_url=URL)


def scrape_events():
    return parse_page(fetch_page(DATA_URL))
