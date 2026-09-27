# Delft event calendar

A minimal React + Vite site. Its only data source is `src/data/events.json`.
No backend, database, external APIs, accounts, or scraper.
The ten included events are **fictional examples** across September–November
2026. Their example.com URLs are placeholders, not real event listings.

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
time order, or “No events.” Browse September–November 2026 to test the examples.
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

When replacing the fake events, update the example notice in `src/App.jsx` and
description in `index.html`. A future script can generate the same JSON file.
This version does not scrape anything. Data updates require a build/deployment.

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
```

Deployment follows the [Vite Pages guide](https://vite.dev/guide/static-deploy#github-pages)
and [GitHub Pages workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).
