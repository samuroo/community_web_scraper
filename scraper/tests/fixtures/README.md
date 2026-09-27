# Parser fixtures

Captured 27 September 2026 using the scraper's descriptive User-Agent:

- `bebop.html`: first two `.event-summary` entries from https://shop.jazzcafebebop.nl/.
- `open_delft.html`: first, multi-day, and last `.calendar__activity` entries from https://www.opendelft.info/agenda.
- `delfts_brouwhuis.html`: first two `#vsel .vsel-content` entries from https://delftsbrouwhuis.nl/events/.

These are HTML excerpts; images, SVGs, long descriptions and unrelated content
were removed. Dates, metadata, links, and the relevant containers are unchanged.
Tests do not contact these sites. Fixture dates stay fixed even after they pass.

HAL015's homepage and the linked https://www.hal015.nl/programma/ returned HTTP
429 with a hosting-provider “Site Unavailable” page. Its robots.txt was also
unavailable. No challenge, limit, or restriction was bypassed.

- `hal015_unavailable.html` is the actual failure response.
- `hal015_text_contract.html` is **reconstructed test HTML**, not a captured live
  DOM. Dates/titles follow the public text view of https://hal015.nl/ on that date;
  links are illustrative test paths. It tests the provisional text-order parser,
  not HAL015's actual HTML compatibility. No guessed CSS classes are used.

HAL015 live verification remains outstanding. When access is restored, inspect
the actual HTML, replace the reconstructed fixture with a real excerpt, and
adjust that parser if needed. It currently covers only the homepage's limited
“Binnenkort” listing, not the entire programme.
