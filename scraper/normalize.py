"""Small, strict conversions shared by the source parsers."""

import hashlib
import re
import unicodedata
from datetime import date, datetime
from urllib.parse import urljoin, urlsplit
from zoneinfo import ZoneInfo

AMSTERDAM = ZoneInfo("Europe/Amsterdam")
MONTHS = {
    "jan": 1, "januari": 1, "feb": 2, "februari": 2,
    "mrt": 3, "maart": 3, "apr": 4, "april": 4, "mei": 5,
    "jun": 6, "juni": 6, "jul": 7, "juli": 7, "aug": 8,
    "augustus": 8, "sep": 9, "sept": 9, "september": 9,
    "okt": 10, "oktober": 10, "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}
VENUES = {
    "hal015": "HAL015", "hal 015": "HAL015",
    "bebop": "Jazz Cafe Bebop", "jazz cafe bebop": "Jazz Cafe Bebop",
    "jazz café bebop": "Jazz Cafe Bebop",
    "open delft": "OPEN Delft", "dok in open": "OPEN Delft",
    "delfts brouwhuis": "Delfts Brouwhuis",
}
TIME_PATTERN = re.compile(r"(?<![\d:.])(\d{1,2})[:.](\d{2})(?![\d:.])")


def whitespace(value):
    return " ".join(unicodedata.normalize("NFC", str(value or "")).split())


def parse_date(value, *, year=None):
    text = whitespace(value).lower()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        return date.fromisoformat(text).isoformat()
    if "t" in text and re.match(r"\d{4}-\d{2}-\d{2}t", text):
        moment = datetime.fromisoformat(text.replace("z", "+00:00"))
        if moment.tzinfo:
            moment = moment.astimezone(AMSTERDAM)
        return moment.date().isoformat()
    numeric = re.fullmatch(r"(\d{1,2})[-/](\d{1,2})[-/](\d{4})", text)
    if numeric:
        day, month, event_year = map(int, numeric.groups())
        return date(event_year, month, day).isoformat()
    text = re.sub(r"^(?:maandag|dinsdag|woensdag|donderdag|vrijdag|zaterdag|zondag|ma|di|wo|do|vr|za|zo)[.,]?\s+", "", text)
    match = re.fullmatch(r"(\d{1,2})\s+([a-z]+)\.?(?:\s+(\d{4}))?", text)
    if not match or match[2] not in MONTHS:
        raise ValueError(f"Unrecognized date: {value!r}")
    event_year = int(match[3]) if match[3] else year
    if event_year is None:
        raise ValueError(f"Date has no explicit year: {value!r}")
    return date(event_year, MONTHS[match[2]], int(match[1])).isoformat()


def normalize_time(value):
    text = whitespace(value).lower()
    match = re.fullmatch(r"(\d{1,2})(?:[:.](\d{2}))?\s*(?:uur|u)?", text)
    if not match:
        raise ValueError(f"Unrecognized time: {value!r}")
    hour, minute = int(match[1]), int(match[2] or 0)
    if hour > 23 or minute > 59:
        raise ValueError(f"Invalid time: {value!r}")
    return f"{hour:02d}:{minute:02d}"


def time_range(text):
    matches = list(TIME_PATTERN.finditer(whitespace(text)))
    if not 1 <= len(matches) <= 2:
        raise ValueError(f"Expected a start time and optional end time: {text!r}")
    times = [normalize_time(match[0]) for match in matches]
    return times[0], times[1] if len(times) == 2 else None


def absolute_url(value, base_url):
    value = whitespace(value)
    if not value:
        raise ValueError("Missing event URL")
    url = urljoin(base_url, value)
    if urlsplit(url).scheme not in {"http", "https"} or not urlsplit(url).netloc:
        raise ValueError(f"Not an HTTP event URL: {value!r}")
    return url


def event_key(event):
    return tuple(whitespace(event[field]).casefold()
                 for field in ("title", "date", "startTime", "venue"))


def normalize_event(raw, base_url):
    title = whitespace(raw.get("title"))
    venue = whitespace(raw.get("venue"))
    if not title or not venue:
        raise ValueError("Missing title or venue")
    event = {
        "title": title,
        "date": parse_date(raw.get("date")),
        "startTime": normalize_time(raw.get("startTime")),
        "endTime": normalize_time(raw["endTime"]) if raw.get("endTime") else None,
        "venue": VENUES.get(venue.casefold(), venue),
        "url": absolute_url(raw.get("url"), base_url),
    }
    digest = hashlib.sha256("\x1f".join(event_key(event)).encode("utf-8")).hexdigest()[:20]
    return {"id": f"event-{digest}", **event}


def is_upcoming(event, now):
    """Upcoming means the advertised start has not passed in Amsterdam."""
    if now.tzinfo is None:
        raise ValueError("now must include a timezone")
    start = datetime.fromisoformat(f"{event['date']}T{event['startTime']}").replace(tzinfo=AMSTERDAM)
    return start >= now.astimezone(AMSTERDAM)
