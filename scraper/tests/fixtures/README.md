# Source fixtures

Tests never fetch live websites. HTML excerpts retain parsing fields and their
containers; images, descriptions, and irrelevant styling were removed where practical.

Captured 27 September 2026:

- `bebop.html`: two `.event-summary` entries from https://shop.jazzcafebebop.nl/.
- `open_delft.html`: first, multi-day, and last entries from https://www.opendelft.info/agenda.
- `delfts_brouwhuis.html`: two entries from https://delftsbrouwhuis.nl/events/.
- `hal015_unavailable.html`: actual unavailable response, retained for failure tests.

Captured 29 September 2026 using the descriptive scraper User-Agent:

- `hal015.html`: real `article.hal-event-card` entries from https://hal015.nl/tickets/.
  Both homepage and tickets page now work without rendering. This replaces the
  old reconstructed contract fixture. Programme cards include the full year,
  time and original product URL; no ticket-system workaround is needed.
- `tu_delft.html`: two cards from https://www.tudelft.nl/sg/events. The official
  https://www.tudelft.nl/sg/about-us confirms activities are open to all visitors.
  The broader https://www.tudelft.nl/over-tu-delft/agenda was inspected but is not
  collected because it also contains internal/staff/student activities.
- `steck.html`: two dated listings from https://shop.steck.nl/, linked by the
  official https://www.steck.nl/ at Kromstraat 25, Delft.
- `koornbeurs.html`: real agenda metadata and three entries from
  https://koornbeurs.nl/agenda/. The canonical site redirects away from `www`.
  Its introduction explicitly welcomes non-members. Dates omit years: resolve
  within 31 days before / 183 days after the page's dateModified and validate
  the weekday. Never anchor stale pages to today's year. The first captured
  entry says Tuesday 26 September, inconsistent with 2026; it is skipped.
- `cultuurlab.json`: four rows with just the fields needed by the parser from
  https://cultuurlab.nl/interactive/agenda.php?active=1, the exact public URL used
  by `fillagenda(1)` in https://cultuurlab.nl/js/script.js. The script confirms
  Brabantse Turfmarkt 9, Delft. This is the page's own data, not an external API.
  `timeofday` is a day-part hint, NOT an event start. Only Aanvang/Vanaf gives a
  usable start; ticketshop links are kept when present, otherwise the agenda URL.

Theater de Veste: https://www.theaterdeveste.nl/robots.txt returns HTTP 307 to
`https://www.theaterdeveste.nl/csq/`, with `x-redirect-reason: no-token` and a
challenge-target cookie. No browser challenge was attempted. Its module is an
explicit failure adapter, not an implemented parser. There is no fabricated
success fixture or claim of working coverage.
