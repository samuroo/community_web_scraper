from scraper.normalize import event_key


def deduplicate(events):
    """Keep the first match, following the fixed source and page order."""
    unique = {}
    for event in events:
        unique.setdefault(event_key(event), event)
    return list(unique.values()), len(events) - len(unique)
