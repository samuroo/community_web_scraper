"""Run from the project root: python scraper/run.py."""

import json
import os
from pathlib import Path
import sys
import tempfile
from datetime import datetime

if __name__ == "__main__":
    # Use the operating system's trusted certificates; never disable TLS checks.
    import truststore
    truststore.inject_into_ssl()

# Also support execution by absolute path from cron on a different working directory.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scraper.deduplicate import deduplicate
from scraper.normalize import AMSTERDAM, is_upcoming
from scraper.sources import hal015, bebop, open_delft, delfts_brouwhuis

SOURCES = (hal015, bebop, open_delft, delfts_brouwhuis)
OUTPUT = ROOT / "src" / "data" / "events.json"


def write_events(events, output):
    """Replace atomically, so an interrupted run cannot truncate the frontend data."""
    output = Path(output)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=output.parent,
                                         suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            json.dump(events, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temporary, output)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def run(sources=SOURCES, output=OUTPUT, now=None):
    now = now or datetime.now(AMSTERDAM)
    events, failures = [], 0
    for source in sources:
        try:
            collected = source.scrape_events()
            upcoming = [event for event in collected if is_upcoming(event, now)]
            events.extend(upcoming)
            print(f"{source.NAME}: {len(upcoming)} events ({len(collected) - len(upcoming)} past starts omitted)")
        except Exception as error:
            # Isolate even an unexpected parser failure to this one source.
            failures += 1
            print(f"{source.NAME}: ERROR [{type(error).__name__}] {error}")

    if failures == len(sources):
        print("All sources failed. Existing events.json was left unchanged.")
        return 1

    events, removed = deduplicate(events)
    events.sort(key=lambda event: (event["date"], event["startTime"], event["venue"], event["title"]))
    write_events(events, output)
    print(f"\nDuplicates removed: {removed}\nTotal events written: {len(events)}")
    print(f"Output: {Path(output).resolve()}")
    if failures:
        print(f"Partial result: {failures} source(s) failed; their events are absent from this snapshot.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
