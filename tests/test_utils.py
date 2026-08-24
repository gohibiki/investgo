"""
Unit tests for the utils module and scraper instance behavior.
"""

import requests
from investgo.utils import get_scraper, get_default_headers


def test_get_default_headers():
    headers = get_default_headers()
    assert isinstance(headers, dict)
    assert headers.get("x-meta-ver") == "14"


def test_get_scraper():
    scraper = get_scraper()
    assert isinstance(scraper, requests.Session)
    # The site 403s the default python-requests UA; a browser UA must be set
    assert "Mozilla" in scraper.headers.get("User-Agent", "")


def test_get_scraper_is_shared():
    assert get_scraper() is get_scraper()
