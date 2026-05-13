import sys
import http.client as httplib

import requests


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip",
    "DNT": "1",
    "Connection": "keep-alive",
    "Sec-GPC": "1",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}


class InternetChecker:
    def __init__(self, check_internet=True):
        self.check_internet = check_internet
        self._already_checked = False

    def internet_present(self):
        conn = httplib.HTTPSConnection("8.8.8.8", timeout=5)
        try:
            conn.request("HEAD", "/")
            return True
        except Exception:
            return False
        finally:
            self._already_checked = True
            conn.close()

    def is_online(self):
        if self.check_internet and not self._already_checked:
            if not self.internet_present():
                return False
        return True


class Fetcher:
    def __init__(self, headers=None, timeout=30):
        self.headers = headers or HEADERS
        self.internet_checker = InternetChecker()
        self.timeout = timeout

    def check_internet(self):
        return self.internet_checker.is_online()

    def fetch(self, url, timeout=None):
        if url is None:
            return None
        try:
            r = requests.get(
                url, headers=self.headers,
                timeout=timeout or self.timeout,
            )
            r.raise_for_status()
            return r
        except requests.RequestException:
            return None

    def fetch_html(self, url, timeout=None):
        response = self.fetch(url, timeout=timeout)
        if response is not None:
            return response.content
        return None

    def fetch_text(self, url, timeout=None):
        response = self.fetch(url, timeout=timeout)
        if response is not None:
            return response.text
        return None
