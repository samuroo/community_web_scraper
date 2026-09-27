# Delft event calendar

A minimal React + Vite site. Its only runtime data source is `src/data/events.json`.
A separate Python scraper generates that file locally from four venue websites.
No backend, database, external APIs, or accounts. See **Local Python scraper**
below for setup, source status, and limitations.

## 1. Install dependencies

Install **Node.js 22.12 or newer** (Node 22 LTS recommended) from
[nodejs.org](https://nodejs.org/) and [Git](https://git-scm.com/downloads).
Node includes npm. Restart your terminal after installation.

```sh
git clone https://github.com/samuroo/community_web_scraper.git
cd community_web_scraper
npm ci
```

If you already have this folder, open a terminal inside it and run `npm ci`.
This installs React and Vite locally; no separate or global installation is needed.
If PowerShell blocks npm.ps1, use `npm.cmd` instead of `npm`.

## 2. Run locally

```sh
npm run dev
```

Open http://localhost:5173/community_web_scraper/ (or the address printed by
Vite if that port is busy). Stop with Ctrl+C.

The calendar starts on the current month with today selected. Weeks start on
Monday. Dots mark dates with events. Clicking a date shows its events in start
time order, or “No events.” Browse the dates in `src/data/events.json` to see events.
Changing months clears selection; returning to the current month selects today.
An underline marks today; a dark background marks the selected day.

## 3. Add or edit events

Edit the array in `src/data/events.json`:

```json
{
  "id": "bebop-2026-10-03-live-jazz",
  "title": "Live Jazz",
  "date": "2026-10-03",
  "startTime": "20:00",
  "endTime": null,
  "venue": "Jazz Cafe Bebop",
  "url": "https://example.com/event"
}
```

- Use a unique `id` for each event.
- Dates must be valid `YYYY-MM-DD`; times must be zero-padded 24-hour `HH:mm`.
- Dates and times represent local Delft venue time, without timezone conversion.
- `endTime` is optional: omit it, use `null`, or a time such as `22:00`.
- Use the original event's full HTTPS URL. Links open in a new tab.
- Use valid JSON: double quotes, commas between entries, no comments or trailing commas.
- An empty array `[]` is supported. Array order does not matter.

The Python scraper overwrites this entire file, including manual edits.
Data updates require a new frontend build/deployment to appear on GitHub Pages.

## 4. Push to GitHub

This folder already uses `samuroo/community_web_scraper` and branch `main`.
Review and commit the files, including `package-lock.json`:

```sh
git add .
git commit -m "Add minimal Delft event calendar"
git push -u origin main
```

For a new repository from a downloaded folder, create an empty public repository
on GitHub, then run:

```sh
git init
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git add .
git commit -m "Add minimal Delft event calendar"
git push -u origin main
```

If `origin` already exists, use `git remote set-url origin ...` instead of
`git remote add origin ...`. If renaming the repository, change `base` in
`vite.config.js` to `/YOUR_REPOSITORY/`. Use `/` for a root repository named
`YOUR_USERNAME.github.io` or a custom domain.

## 5. Enable GitHub Pages

For free hosting on GitHub Free, use a **public** repository.
Open [Settings → Pages](https://github.com/samuroo/community_web_scraper/settings/pages).
Under **Build and deployment → Source**, select **GitHub Actions**.
The workflow is already in `.github/workflows/deploy.yml`.

## 6. Build and deploy

Check production locally:

```sh
npm run build
npm run preview
```

Open http://localhost:4173/community_web_scraper/ to preview `dist`.
This preview server is for local checking only.

Every push to `main` runs the workflow: install locked dependencies, build,
upload `dist`, and deploy to Pages. You can also open **Actions → Deploy to
GitHub Pages → Run workflow → main → Run workflow** after enabling Pages.
If the initial run failed before Pages was enabled, rerun it.
Wait for both build and deploy jobs to turn green. The deployment shows the URL.
Do not commit `dist` or `node_modules`; both are ignored.

## 7. Share the site

After the first successful deployment, share:

**https://samuroo.github.io/community_web_scraper/**

This is the expected address for the configured repository, not confirmation
that the site is already published. For another repository, the address is
`https://YOUR_USERNAME.github.io/YOUR_REPOSITORY/`.
Pages settings and the workflow deployment summary show the actual published URL.

## Project structure

```text
src/
  components/Calendar.jsx
  components/EventList.jsx
  data/events.json
  App.jsx
  dates.js
  main.jsx
  styles.css
.github/workflows/deploy.yml
vite.config.js
scraper/
  run.py
  normalize.py
  deduplicate.py
  fetch.py
  parsing.py
  requirements.txt
  sources/
    hal015.py
    bebop.py
    open_delft.py
    delfts_brouwhuis.py
  tests/
    test_scraper.py
    fixtures/
```

Deployment follows the [Vite Pages guide](https://vite.dev/guide/static-deploy#github-pages)
and [GitHub Pages workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

## Local Python scraper

Use **Python 3.10 or newer**. All commands below run from the repository root.
Python is only needed when generating data, not when viewing or hosting the site.

### 1. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS, Linux, or Raspberry Pi:

```sh
python3 -m venv .venv
source .venv/bin/activate
```

If PowerShell blocks activation, skip activation and substitute
`.\.venv\Scripts\python.exe` for `python` in the commands below.
On Raspberry Pi OS, install `python3-venv` with the OS package manager if venv
is unavailable. No browser or Playwright installation is required.

### 2. Install Python dependencies

```sh
python -m pip install -r scraper/requirements.txt
```

Dependencies are requests, BeautifulSoup, timezone data (needed on Windows), and
truststore for the operating system's trusted HTTPS certificates. Certificate
verification stays enabled. Keep the OS certificate store up to date on the Pi.

### 3. Generate events

```sh
python scraper/run.py
```

The runner fetches the four configured sources sequentially, normalizes entries,
filters past starts, removes exact duplicates, and atomically replaces
`src/data/events.json` with readable UTF-8 JSON sorted by date and start time.
It prints counts per source, errors, duplicates removed, and the output path.

The fetcher identifies itself as `DelftEventsCalendar/1.0` with this repository's
URL. It checks robots.txt, waits at least two seconds between requests to the
same host, honors longer crawl delays (Bebop specifies 15 seconds), and uses
10-second connection / 30-second read timeouts. Connections are closed after
each response because Brouwhuis drops reused connections. There are no automatic retries,
authentication, CAPTCHA workarounds, or browser automation. A blocked or
unavailable site is reported and skipped. Redirect targets are checked too.

### 4. Check the generated JSON

```sh
python -m json.tool src/data/events.json
git diff -- src/data/events.json
```

Check the terminal summary as well: valid JSON does not imply all sites worked.
The scraper never substitutes fictional events for missing data.

### 5. Run the React site

```sh
npm ci
npm run dev
```

Open http://localhost:5173/community_web_scraper/. To check production, run
`npm run build`. Publishing updated data still requires a manual commit and push
using the existing GitHub Pages workflow. Running the scraper alone changes only
your local JSON; it does not publish anything or use GitHub credentials.

### Sources and current limitations

| Source | Parsing and coverage |
| --- | --- |
| HAL015 | **Live verification blocked:** homepage and programme returned HTTP 429 / “Site Unavailable” during inspection on 27 September 2026. Includes a provisional text-order parser for the homepage's “Binnenkort” listings, with no guessed CSS classes. Its synthetic contract test is not proof of live HTML compatibility. Needs a real HTML fixture and verification once access returns. No entire-programme coverage is claimed. |
| Bebop | Parses agenda entries on the public shop homepage; dated ticket links supply the year and distinguish occurrences. Membership packs are excluded. |
| OPEN Delft | Parses all calendar entries on the agenda page. Linked event URLs provide the full date; those external pages are not fetched. `DOK in OPEN` is normalized to `OPEN Delft`. |
| Delfts Brouwhuis | Parses the event-list metadata on `/events/`. When no individual page exists, links point to the listing's `#event-…` anchor. |

The local run on 27 September 2026 wrote **60 events**: Bebop 2, OPEN Delft 53,
and Delfts Brouwhuis 5, with 0 duplicates. HAL015 was skipped because robots.txt
returned HTTP 429. These are results from that run, not guaranteed future counts.

Dates/times use **Europe/Amsterdam**, independent of the machine's timezone.
Only events whose advertised start has not passed are included; already-started
events are excluded, even if still running. Missing end times become `null`.
Missing/invalid required dates, years or start times are reported and skipped,
not invented. Each ID hashes normalized title, date, time and venue; changing a
URL or end time does not change the ID. Duplicate comparison uses those same four
fields, with whitespace normalization and case folding; the first entry wins in
the fixed source order shown above. No fuzzy matching is used.

The schema has no all-day flag or end date. Multi-day listings are represented
once on their explicit start date, without inferring additional occurrences.
OPEN's advertised `00:00` values are retained as published. Brouwhuis's structured
time fields take precedence over times mentioned in descriptions. Recurrences
mentioned only in prose are not expanded. Only the inspected listing pages are
scraped; there is no general crawler or guessed pagination.

One failed source does not stop the rest: the output is a fresh snapshot of
successful sources, so failed sources' old events are not retained. If **all**
sources fail, the existing file is preserved and the command exits with code 1.
An unrecognized/empty page layout is treated as a parsing error rather than
silently assuming it has no events. A valid run containing only past events
writes `[]`. Partial success exits with code 0 and prints a prominent warning.

### Offline tests

```sh
python -m unittest discover -s scraper/tests -v
```

Tests cover each parser, normalization, duplicate removal, time filtering,
request policy, source failures, and atomic output. They use local fixtures and
mock HTTP calls, never live requests. Fixture provenance and the HAL015 caveat
are documented in `scraper/tests/fixtures/README.md`. Source selectors are kept
inside each source module, separate from `fetch_page()` and shared normalization.

The output path is resolved relative to the repository, not the working
directory. The same virtual-environment Python can therefore run the script on
a Raspberry Pi later. No cron, automated commits, GitHub authentication, or
scheduled scraping is configured.
