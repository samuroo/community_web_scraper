# Event Scraper

**Live website: [samuroo.github.io/event-scraper](https://samuroo.github.io/event-scraper/)**

A community event web scraper for Delft, collecting local events into a simple
calendar. The project may later expand to Den Haag and possibly Rotterdam.

Use the Sources checkboxes to filter both the event list and calendar dots.
All sources start selected; on mobile the checklist appears above the calendar.

## Project structure

```text
src/
  components/           React calendar and event list
  data/events.json      Generated event data
scraper/
  run.py                Collect, filter, sort and write events
  normalize.py          Shared dates, times, venues and stable IDs
  deduplicate.py        Remove matching title/date/time/venue entries
  fetch.py              Respectful HTTP requests and robots checks
  sources/              One scraper per source
  tests/fixtures/       Offline parser tests and saved source samples
.github/workflows/      GitHub Pages build and deployment
vite.config.js          Vite settings, including /event-scraper/ base
```

The Python scraper updates the JSON; React reads it at build time. No backend
or database is needed. Tests live in `scraper/tests/`.

## Event format

`src/data/events.json` contains an array of events:

```json
{
  "id": "example-live-jazz",
  "title": "Live Jazz",
  "date": "2026-10-03",
  "startTime": "20:00",
  "endTime": null,
  "venue": "Jazz Cafe Bebop",
  "url": "https://example.com/event"
}
```

Dates use `YYYY-MM-DD`; times use `HH:MM` in Europe/Amsterdam. `endTime` can be
`null`. The URL links to the original event or source page. The scraper creates
stable IDs automatically; the example above is illustrative.

## Run the scraper

Requires Python 3.10+. From the project root, create and activate a virtual environment.

Windows (Command Prompt):

```bat
python -m venv .venv
.venv\Scripts\activate
```

In PowerShell, activate with `.\.venv\Scripts\Activate.ps1`, or use
`.\.venv\Scripts\python.exe` directly if activation is blocked.

macOS/Linux:

```sh
python3 -m venv .venv
source .venv/bin/activate
```

Then install dependencies and generate events:

```sh
python -m pip install -r scraper/requirements.txt
python scraper/run.py
```

This overwrites `src/data/events.json` locally with upcoming events. Check the
printed source counts and `git diff -- src/data/events.json`. Failed sources
are skipped; if all sources fail, the existing file is preserved. Running the
scraper does **not** publish the site.

## Event sources

Checked 29 September 2026. “Partial” means some listings are intentionally skipped.

| Source | Parsing method | Coverage | Works? |
| --- | --- | --- | --- |
| [HAL015](https://hal015.nl/tickets/) | HTML event cards | Full tickets listing; accessible again | Yes |
| [Jazz Cafe Bebop](https://shop.jazzcafebebop.nl/) | Dated ticket listings | Published shop events, excluding membership packs | Yes |
| [OPEN Delft](https://www.opendelft.info/agenda) | HTML calendar listings | Published activities; multi-day events appear once at their start | Yes |
| [Delfts Brouwhuis](https://delftsbrouwhuis.nl/events/) | HTML event metadata | Listed events; prose-only recurrences are not expanded | Yes |
| [TU Delft](https://www.tudelft.nl/sg/events) | HTML event cards | Public Studium Generale programme only; not the whole university | Yes |
| [Theater de Veste](https://www.theaterdeveste.nl/programma) | Not implemented: robots request redirects to `/csq/` bot protection | Programme inspection blocked; no bypass attempted | No |
| [OJV De Koornbeurs](https://koornbeurs.nl/agenda/) | HTML agenda + page update date | Public activities; missing years anchored to page update, inconsistent weekdays skipped | Partial |
| [STECK](https://shop.steck.nl/) | Dated ticket listings | Public events at STECK, Kromstraat 25, Delft | Yes |
| [Cultuurlab](https://cultuurlab.nl/) | First-party agenda data loaded by its page script | Entries with explicit start times; doors-only, untimed and cancelled entries skipped | Partial |

No browser automation is needed. Fetching uses a clear User-Agent, robots rules,
timeouts and request spacing. Past starts are excluded, including earlier today.

## Preview, test and publish

With Node.js 22.12+ installed:

```sh
npm ci
npm run dev
```

Open http://localhost:5173/event-scraper/.

```sh
python -m unittest discover -s scraper/tests -v
npm run build
```

Tests use saved fixtures, not live websites. To publish, commit and push changes
to `main` in `samuroo/event-scraper`. The existing GitHub Actions workflow builds
and deploys `dist`. In repository **Settings → Pages**, select **GitHub Actions**.
Wait for the deployment to succeed, then open the live link above.
