"""Common error reporting only; selectors belong in each source module."""

from scraper.normalize import normalize_event


class ParseError(ValueError):
    pass


def required_text(node):
    if node is None:
        raise ParseError("Required element is missing")
    return node.get_text(" ", strip=True)


def parse_cards(cards, extract, *, source, base_url):
    if not cards:
        raise ParseError("No recognizable event entries; the page may be empty or have changed")
    events = []
    for index, card in enumerate(cards, 1):
        try:
            events.append(normalize_event(extract(card), base_url))
        except (ValueError, KeyError, TypeError) as error:
            print(f"{source}: skipping entry {index}: {error}")
    if not events:
        raise ParseError("None of the event entries had a valid title, date, time, venue and URL")
    return events
