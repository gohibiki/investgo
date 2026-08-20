"""
Unit tests for the utils module and scraper instance behavior.
"""

import pytest
import cloudscraper
from investgo.utils import get_scraper, get_default_headers


def test_get_default_headers():
    headers = get_default_headers()
    assert isinstance(headers, dict)
    assert headers.get("x-meta-ver") == "14"


def test_get_scraper():
    scraper = get_scraper()
    assert scraper is not None
    assert hasattr(scraper, 'current_concurrent_requests')
    assert scraper.current_concurrent_requests >= 0


def test_cloudscraper_compatibility_attributes():
    # Test that CloudScraper class has default attributes so unpickled/mocked objects won't fail
    assert hasattr(cloudscraper.CloudScraper, 'current_concurrent_requests')
    assert hasattr(cloudscraper.CloudScraper, 'max_concurrent_requests')
    assert hasattr(cloudscraper.CloudScraper, 'last_request_time')
    assert hasattr(cloudscraper.CloudScraper, 'min_request_interval')
    assert hasattr(cloudscraper.CloudScraper, 'rotate_tls_ciphers')
    assert hasattr(cloudscraper.CloudScraper, 'request_count')
    assert hasattr(cloudscraper.CloudScraper, 'enable_stealth')
