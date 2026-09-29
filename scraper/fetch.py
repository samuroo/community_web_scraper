"""Polite HTTP fetching: robots checks, per-host spacing, no retries."""

import time
from urllib.parse import urljoin, urlsplit
from urllib.robotparser import RobotFileParser

import requests

USER_AGENT = "DelftEventsCalendar/1.0 (+https://github.com/samuroo/event-scraper)"
TIMEOUT = (10, 30)


class FetchError(RuntimeError):
    pass


class PageFetcher:
    def __init__(self):
        self.session = requests.Session()
        # These few daily requests do not need persistent connections. Brouwhuis
        # drops reused connections, so explicitly close each one after reading.
        self.session.headers.update({"User-Agent": USER_AGENT, "Connection": "close"})
        self.robots = {}
        self.last_request = {}
        self.delays = {}
        self.cache = {}

    def _request(self, url):
        host = urlsplit(url).netloc
        wait = self.delays.get(host, 2) - (time.monotonic() - self.last_request.get(host, 0))
        if wait > 0:
            time.sleep(wait)
        # Redirects are checked separately, including the destination's robots rules.
        try:
            return self.session.get(url, timeout=TIMEOUT, allow_redirects=False)
        except requests.RequestException as error:
            raise FetchError(f"Request failed for {url}: {error}") from error
        finally:
            self.last_request[host] = time.monotonic()

    def _check_robots(self, url):
        parts = urlsplit(url)
        origin = f"{parts.scheme}://{parts.netloc}"
        if origin not in self.robots:
            response = self._request(origin + "/robots.txt")
            parser = RobotFileParser()
            if response.status_code == 404:
                parser.parse([])
            elif response.status_code in (401, 403):
                raise FetchError(f"robots.txt access denied for {origin}")
            else:
                response.raise_for_status()
                if response.is_redirect:
                    raise FetchError(f"robots.txt redirected for {origin}; inspect before scraping")
                if "<html" in response.text.lower():
                    raise FetchError(f"robots.txt returned HTML for {origin}; inspect before scraping")
                parser.parse(response.text.splitlines())
            self.robots[origin] = parser
            delay = parser.crawl_delay(USER_AGENT) or 2
            rate = parser.request_rate(USER_AGENT)
            if rate:
                delay = max(delay, rate.seconds / rate.requests)
            self.delays[parts.netloc] = max(2, delay)
        if not self.robots[origin].can_fetch(USER_AGENT, url):
            raise FetchError(f"robots.txt disallows {url}")

    def fetch_page(self, url):
        if url in self.cache:
            return self.cache[url]
        original_url = url
        for _ in range(6):
            if urlsplit(url).scheme not in {"http", "https"}:
                raise FetchError(f"Not an HTTP URL: {url}")
            self._check_robots(url)
            response = self._request(url)
            response.raise_for_status()
            if response.is_redirect:
                url = urljoin(url, response.headers["Location"])
                continue
            # Accessible listing pages declare UTF-8. Avoid the ISO-8859-1 fallback.
            response.encoding = "utf-8"
            text = response.text
            markers = ("please wait while your request is being verified", "cf-chl-",
                       "verify you are human", "this site is currently unavailable")
            if any(marker in text.lower() for marker in markers):
                raise FetchError(f"Access challenge or unavailable page at {url}; not bypassing")
            self.cache[original_url] = text
            return text
        raise FetchError(f"Too many redirects: {original_url}")


_fetcher = PageFetcher()


def fetch_page(url):
    return _fetcher.fetch_page(url)
