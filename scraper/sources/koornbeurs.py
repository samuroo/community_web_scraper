"""Public agenda at O.J.V. De Koornbeurs, Voldersgracht 1, Delft.

The page omits years. Anchor to its published dateModified, NOT today's year,
and validate the printed weekday. Ambiguous/inconsistent entries are skipped.
"""

from datetime import date, timedelta
import json
import re
from bs4 import BeautifulSoup

from scraper.fetch import fetch_page
from scraper.normalize import time_range
from scraper.parsing import ParseError, parse_cards, required_text

URL = "https://koornbeurs.nl/agenda/"
NAME = "OJV De Koornbeurs"
MONTHS = {name: index for index, name in enumerate(
    "january february march april may june july august september october november december".split(), 1)}
WEEKDAYS = "monday tuesday wednesday thursday friday saturday sunday".split()
DATE = re.compile(r"(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+(?:the\s+)?"
                  r"(\d{1,2})(?:st|nd|rd|th)?\s+(?:of\s+)?([A-Za-z]+)(?:\s+(\d{4}))?", re.I)


def event_date(match, updated):
    month = MONTHS[match[3].lower()]
    weekday = WEEKDAYS.index(match[1].lower())
    years = [int(match[4])] if match[4] else range(updated.year - 1, updated.year + 2)
    candidates = []
    for year in years:
        try:
            candidate = date(year, month, int(match[2]))
        except ValueError:
            continue
        if candidate.weekday() == weekday and (match[4] or updated - timedelta(days=31) <= candidate <= updated + timedelta(days=183)):
            candidates.append(candidate)
    if len(candidates) != 1:
        raise ParseError(f"Unclear year or inconsistent weekday: {match[0]}")
    return candidates[0].isoformat()


def parse_page(html):
    soup = BeautifulSoup(html, "html.parser")
    updated = None
    for script in soup.select('script[type="application/ld+json"]'):
        data = json.loads(script.string or script.get_text())
        for node in data.get("@graph", []):
            if node.get("@type") == "WebPage" and node.get("url") == URL:
                updated = date.fromisoformat(node["dateModified"][:10])
    if updated is None:
        raise ParseError("No agenda update date to resolve missing years")

    def extract(card):
        paragraphs = [required_text(p) for p in card.find_all("p")]
        stamp = next((DATE.fullmatch(p) for p in paragraphs if DATE.fullmatch(p)), None)
        if stamp is None:
            raise ParseError("Missing event date")
        # The first time-only paragraph is the advertised schedule, not a band timetable.
        schedule = next((p for p in paragraphs if re.fullmatch(r"\d{1,2}:\d{2}\s*[-–]\s*\d{1,2}:\d{2}", p)), None)
        start, end = time_range(schedule)
        return {"title": required_text(card.select_one("h4")), "date": event_date(stamp, updated),
                "startTime": start, "endTime": end, "venue": NAME, "url": URL}

    cards = [card for card in soup.select(".brz-column__items")
             if card.select_one("h4") and any(DATE.fullmatch(required_text(p)) for p in card.find_all("p"))]
    return parse_cards(cards, extract, source=NAME, base_url=URL)


def scrape_events():
    return parse_page(fetch_page(URL))
