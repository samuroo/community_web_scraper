import contextlib
from datetime import date, datetime
import io
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from scraper.normalize import AMSTERDAM, is_upcoming
from scraper.parsing import ParseError
from scraper.run import run
from scraper.sources import cultuurlab, hal015, koornbeurs, steck, theater_de_veste, tu_delft

FIXTURES = Path(__file__).parent / 'fixtures'


def fixture(name):
    return (FIXTURES / name).read_text(encoding='utf-8')


class NewSourceTests(unittest.TestCase):
    def assert_fields(self, event, **expected):
        for field, value in expected.items():
            self.assertEqual(event[field], value, field)

    def test_tu_delft_public_programme(self):
        events = tu_delft.parse_page(fixture('tu_delft.html'))
        self.assertEqual(len(events), 2)
        self.assert_fields(events[0], title='Twilight Safari', date='2026-10-01',
                           startTime='18:30', endTime='20:30', venue='TU Delft / Studium Generale',
                           url='https://www.tudelft.nl/evenementen/2026/sg/10-oct/twilight-safari')
        self.assertEqual(events[1]['date'], '2026-10-06')

    def test_steck_dated_occurrences(self):
        events = steck.parse_page(fixture('steck.html'))
        self.assertEqual(len(events), 2)
        self.assert_fields(events[0], title='VROEG PIEKEN | 30 oktober', date='2026-10-30',
                           startTime='20:00', endTime='00:00', venue='STECK',
                           url='https://shop.steck.nl/home/vroeg-pieken-3/date/208/2026-10-30')
        self.assertIn("Let's Mingle", events[1]['title'])

    def test_koornbeurs_agenda_and_inconsistent_weekday(self):
        with contextlib.redirect_stdout(io.StringIO()) as log:
            events = koornbeurs.parse_page(fixture('koornbeurs.html'))
        self.assertEqual(len(events), 2)
        self.assert_fields(events[0], title='Board Game Basement', date='2026-10-05',
                           startTime='20:00', endTime='00:00', venue='OJV De Koornbeurs',
                           url='https://koornbeurs.nl/agenda/')
        self.assertEqual(events[1]['date'], '2026-10-09')
        self.assertIn('inconsistent weekday', log.getvalue())

    def test_koornbeurs_year_rollover_uses_page_date_not_today(self):
        stamp = koornbeurs.DATE.fullmatch('Friday the 1st of January')
        self.assertEqual(koornbeurs.event_date(stamp, date(2026, 12, 20)), '2027-01-01')
        with self.assertRaises(ParseError):
            koornbeurs.event_date(stamp, date(2025, 12, 20))

    def test_cultuurlab_start_not_doors(self):
        with contextlib.redirect_stdout(io.StringIO()) as log:
            events = cultuurlab.parse_page(fixture('cultuurlab.json'))
        self.assertEqual(len(events), 3)  # Doors-only entry is not assigned a made-up start.
        self.assert_fields(events[0], title='Roel C. Verburg - Try out', date='2026-10-08',
                           startTime='20:30', endTime=None, venue='Cultuurlab',
                           url='https://www.ticketkantoor.nl/shop/IQaNrvofDQ')
        self.assert_fields(events[2], title='Latin in the City', date='2026-10-16',
                           startTime='20:00', endTime='00:00')
        self.assertIn('doors alone', log.getvalue())

    def test_cultuurlab_cancellations_and_empty_agenda(self):
        data = json.loads(fixture('cultuurlab.json'))
        data['rows'] = [dict(data['rows'][0], cancelled=1)]
        self.assertEqual(cultuurlab.parse_page(json.dumps(data)), [])
        self.assertEqual(cultuurlab.parse_page('{"rows": []}'), [])
        with self.assertRaises(ParseError):
            cultuurlab.parse_page('{"error": "unavailable"}')

    def test_theater_is_explicitly_unimplemented_not_false_empty_success(self):
        with self.assertRaisesRegex(ParseError, 'bot protection'):
            theater_de_veste.parse_page('<html>challenge</html>')

    def test_new_sources_use_separate_fetch_and_same_schema(self):
        cases = [(hal015, 'hal015.html'), (tu_delft, 'tu_delft.html'),
                 (steck, 'steck.html'), (koornbeurs, 'koornbeurs.html'),
                 (cultuurlab, 'cultuurlab.json')]
        for source, filename in cases:
            with self.subTest(source=source.NAME), contextlib.redirect_stdout(io.StringIO()), \
                    patch.object(source, 'fetch_page', return_value=fixture(filename)):
                events = source.scrape_events()
                self.assertTrue(events)
                for event in events:
                    self.assertEqual(set(event), {'id', 'title', 'date', 'startTime', 'endTime', 'venue', 'url'})
                    self.assertFalse(is_upcoming(event, datetime(2030, 1, 1, tzinfo=AMSTERDAM)))

    def test_blocked_source_does_not_stop_new_sources(self):
        good = SimpleNamespace(NAME='STECK', scrape_events=lambda: steck.parse_page(fixture('steck.html')))
        with tempfile.TemporaryDirectory() as folder, contextlib.redirect_stdout(io.StringIO()), \
                patch.object(theater_de_veste, 'fetch_page', return_value='challenge'):
            path = Path(folder) / 'events.json'
            code = run([theater_de_veste, good], path, datetime(2026, 10, 31, tzinfo=AMSTERDAM))
            self.assertEqual(code, 0)
            written = json.loads(path.read_text())
            self.assertEqual(len(written), 1)
            self.assertEqual(written[0]['date'], '2026-11-07')


if __name__ == '__main__':
    unittest.main()
