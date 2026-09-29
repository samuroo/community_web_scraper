import contextlib
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import requests

from scraper.deduplicate import deduplicate
from scraper.fetch import FetchError, PageFetcher
from scraper.normalize import AMSTERDAM, is_upcoming, normalize_event, parse_date, time_range
from scraper.parsing import ParseError
from scraper.run import run, write_events
from scraper.sources import bebop, delfts_brouwhuis, hal015, open_delft

FIXTURES = Path(__file__).parent / 'fixtures'


def fixture(name):
    return (FIXTURES / f'{name}.html').read_text(encoding='utf-8')


class ParserTests(unittest.TestCase):
    def assert_event(self, event, title, date, start, end, venue, url):
        self.assertEqual(set(event), {'id', 'title', 'date', 'startTime', 'endTime', 'venue', 'url'})
        self.assertEqual([event[key] for key in ('title', 'date', 'startTime', 'endTime', 'venue', 'url')],
                         [title, date, start, end, venue, url])
        self.assertTrue(event['id'].startswith('event-'))

    def test_bebop(self):
        events = bebop.parse_page(fixture('bebop'))
        self.assertEqual(len(events), 2)
        self.assert_event(events[0], 'Biertocht Delft | Herfst editie | 2026', '2026-10-17',
                          '12:00', '23:00', 'Jazz Cafe Bebop',
                          'https://shop.jazzcafebebop.nl/home/biertocht-delft-herfst-2026/date/196/2026-10-17')
        self.assertEqual(events[1]['date'], '2026-10-18')
        self.assertNotEqual(events[0]['id'], events[1]['id'])

    def test_open_delft(self):
        events = open_delft.parse_page(fixture('open_delft'))
        self.assertEqual(len(events), 3)
        self.assert_event(events[0], 'Informatiepunt Digitale Overheid (IDO)', '2026-09-29',
                          '10:00', '12:00', 'OPEN Delft',
                          'https://dok.op-shop.nl/6767/informatiepunt-digitale-overheid-ido/29-09-2026')
        self.assertEqual(events[1]['date'], '2026-09-30')  # Range kept as one listed start.
        self.assertEqual(events[2]['venue'], 'OPEN Delft')  # DOK in OPEN alias.

    def test_brouwhuis(self):
        events = delfts_brouwhuis.parse_page(fixture('delfts_brouwhuis'))
        self.assertEqual(len(events), 2)
        self.assert_event(events[0], 'groover jazz sunday', '2026-10-04', '15:00', None,
                          'Delfts Brouwhuis', 'https://delftsbrouwhuis.nl/events/#event-5112')

    def test_hal015_live_html_fixture(self):
        events = hal015.parse_page(fixture('hal015'))
        self.assertEqual(len(events), 2)
        self.assert_event(events[0], 'Het danspaleis', '2026-09-30', '14:00', None,
                          'HAL015', 'https://hal015.nl/product/het-danspaleis/')

    def test_unavailable_or_changed_page_is_not_silent_success(self):
        for module in (hal015, bebop, open_delft, delfts_brouwhuis):
            with self.subTest(module=module.NAME), self.assertRaises(ParseError):
                module.parse_page(fixture('hal015_unavailable'))

    def test_bad_entry_does_not_drop_valid_entries(self):
        html = fixture('bebop').replace('2026-10-17', 'missing-year')
        with contextlib.redirect_stdout(io.StringIO()) as log:
            events = bebop.parse_page(html)
        self.assertEqual(len(events), 1)
        self.assertIn('skipping entry', log.getvalue())

    def test_fetch_separate_from_parse(self):
        with patch.object(bebop, 'fetch_page', return_value=fixture('bebop')) as fetch:
            self.assertEqual(len(bebop.scrape_events()), 2)
        fetch.assert_called_once_with(bebop.URL)


class NormalizationTests(unittest.TestCase):
    def event(self, **updates):
        raw = {'title': ' Live\n Jazz ', 'date': '3 oktober 2026', 'startTime': '9.05 uur',
               'venue': 'Jazz Café Bebop', 'url': '/event'}
        return normalize_event({**raw, **updates}, 'https://example.com/')

    def test_dates_and_explicit_years(self):
        for text in ('zaterdag 3 oktober 2026', '3 okt. 2026', '03-10-2026', '2026-10-03'):
            self.assertEqual(parse_date(text), '2026-10-03')
        self.assertEqual(parse_date('1 jan', year=2027), '2027-01-01')
        self.assertEqual(parse_date('2026-09-30T23:30:00Z'), '2026-10-01')
        for text in ('3 oktober', '31 februari 2026', '2026-13-01'):
            with self.assertRaises(ValueError):
                parse_date(text)

    def test_times(self):
        self.assertEqual(time_range('van 9.05 tot 10:30'), ('09:05', '10:30'))
        self.assertEqual(time_range('20:00 – 00:30'), ('20:00', '00:30'))
        for text in ('tijd onbekend', '25:00', '20:80'):
            with self.assertRaises(ValueError):
                time_range(text)

    def test_optional_fields_whitespace_urls_and_stable_ids(self):
        event = self.event()
        self.assertEqual(event['title'], 'Live Jazz')
        self.assertEqual(event['venue'], 'Jazz Cafe Bebop')
        self.assertEqual(event['startTime'], '09:05')
        self.assertIsNone(event['endTime'])
        self.assertEqual(event['url'], 'https://example.com/event')
        self.assertEqual(event['id'], self.event(title='LIVE  JAZZ', venue='Bebop', url='/new')['id'])
        with self.assertRaises(ValueError):
            self.event(url='javascript:alert(1)')

    def test_deduplication_keeps_first_and_different_occurrences(self):
        first = self.event()
        different_time = self.event(startTime='10:00')
        unique, count = deduplicate([first, self.event(title='live jazz', url='/other'), different_time])
        self.assertEqual(unique, [first, different_time])
        self.assertEqual(count, 1)

    def test_filter_uses_amsterdam_including_today_and_dst(self):
        now = datetime(2026, 10, 3, 7, 0, tzinfo=timezone.utc)  # 09:00 Amsterdam
        self.assertTrue(is_upcoming(self.event(), now))
        self.assertFalse(is_upcoming(self.event(startTime='08:59'), now))
        self.assertFalse(is_upcoming(self.event(date='2026-10-02'), now))
        winter = datetime(2026, 12, 1, 8, 0, tzinfo=timezone.utc)  # 09:00 Amsterdam
        self.assertTrue(is_upcoming(self.event(date='2026-12-01'), winter))


class RunnerTests(unittest.TestCase):
    def test_failure_isolation_dedup_sort_filter_and_json(self):
        events = bebop.parse_page(fixture('bebop'))
        past = {**events[0], 'date': '2020-01-01'}
        sources = [SimpleNamespace(NAME='broken', scrape_events=Mock(side_effect=requests.Timeout('timeout'))),
                   SimpleNamespace(NAME='working', scrape_events=lambda: [events[1], past, events[0], events[0]])]
        with tempfile.TemporaryDirectory() as folder, contextlib.redirect_stdout(io.StringIO()) as log:
            path = Path(folder) / 'events.json'
            self.assertEqual(run(sources, path, datetime(2026, 9, 27, tzinfo=AMSTERDAM)), 0)
            self.assertEqual(json.loads(path.read_text(encoding='utf-8')), events)
        self.assertIn('Partial result', log.getvalue())
        self.assertIn('Duplicates removed: 1', log.getvalue())

    def test_all_failed_preserves_file(self):
        source = SimpleNamespace(NAME='broken', scrape_events=Mock(side_effect=ParseError('changed')))
        with tempfile.TemporaryDirectory() as folder, contextlib.redirect_stdout(io.StringIO()):
            path = Path(folder) / 'events.json'
            path.write_text('["keep"]', encoding='utf-8')
            self.assertEqual(run([source], path), 1)
            self.assertEqual(path.read_text(), '["keep"]')

    def test_successful_empty_run_writes_empty_array(self):
        source = SimpleNamespace(NAME='empty', scrape_events=lambda: [])
        with tempfile.TemporaryDirectory() as folder, contextlib.redirect_stdout(io.StringIO()):
            path = Path(folder) / 'events.json'
            self.assertEqual(run([source], path), 0)
            self.assertEqual(json.loads(path.read_text()), [])

    def test_failed_replace_preserves_file_and_cleans_temporary(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'events.json'
            path.write_text('[]', encoding='utf-8')
            with patch('scraper.run.os.replace', side_effect=OSError('disk failure')):
                with self.assertRaises(OSError):
                    write_events([{}], path)
            self.assertEqual(path.read_text(), '[]')
            self.assertEqual(len(list(Path(folder).iterdir())), 1)


class FetchTests(unittest.TestCase):
    def response(self, text, status=200):
        response = requests.Response()
        response.status_code = status
        response._content = text.encode('utf-8')
        response.url = 'https://example.com/'
        return response

    def test_robots_and_caching(self):
        fetcher = PageFetcher()
        self.assertEqual(fetcher.session.headers['Connection'], 'close')
        with patch.object(fetcher.session, 'get', side_effect=[
            self.response('User-agent: *\nCrawl-delay: 15\nDisallow: /private'),
            self.response('<html>café</html>'),
        ]) as get, patch('scraper.fetch.time.sleep') as sleep:
            self.assertEqual(fetcher.fetch_page('https://example.com/'), '<html>café</html>')
            fetcher.fetch_page('https://example.com/')
            self.assertEqual(get.call_count, 2)
            self.assertGreater(sleep.call_args[0][0], 14)
            with self.assertRaises(FetchError):
                fetcher.fetch_page('https://example.com/private')
            self.assertEqual(get.call_count, 2)

    def test_429_is_not_retried(self):
        fetcher = PageFetcher()
        with patch.object(fetcher.session, 'get', return_value=self.response('unavailable', 429)) as get:
            with self.assertRaises(requests.HTTPError):
                fetcher.fetch_page('https://example.com/')
            self.assertEqual(get.call_count, 1)

    def test_bot_challenge_is_not_parsed(self):
        fetcher = PageFetcher()
        with patch.object(fetcher, '_check_robots'), patch.object(fetcher, '_request', return_value=
                self.response('<html>Please wait while your request is being verified</html>')):
            with self.assertRaises(FetchError):
                fetcher.fetch_page('https://example.com/')

    def test_redirect_checks_destination_robots(self):
        fetcher = PageFetcher()
        redirect = self.response('', 302)
        redirect.headers['Location'] = 'https://other.example/private'
        with patch.object(fetcher, '_request', side_effect=[
            self.response('User-agent: *\nDisallow:'), redirect,
            self.response('User-agent: *\nDisallow: /private'),
        ]) as request:
            with self.assertRaises(FetchError):
                fetcher.fetch_page('https://example.com/')
        self.assertEqual(request.call_count, 3)


if __name__ == '__main__':
    unittest.main()
