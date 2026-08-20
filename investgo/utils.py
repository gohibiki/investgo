"""
Utility functions and shared resources for InvestGo.
"""

import cloudscraper
from typing import Dict

# Ensure CloudScraper class has default attributes if accessed on uninitialized or deserialized instances
if hasattr(cloudscraper, 'CloudScraper'):
    for attr, val in [
        ('current_concurrent_requests', 0),
        ('max_concurrent_requests', 10),
        ('last_request_time', 0),
        ('min_request_interval', 0.0),
        ('rotate_tls_ciphers', False),
        ('request_count', 0),
        ('enable_stealth', False),
        ('_solveDepthCnt', 0),
        ('solveDepth', 3),
        ('_403_retry_count', 0),
        ('max_403_retries', 3),
        ('session_start_time', 0),
        ('session_refresh_interval', 3600),
        ('auto_refresh_on_403', False),
        ('last_403_time', 0),
    ]:
        if not hasattr(cloudscraper.CloudScraper, attr):
            setattr(cloudscraper.CloudScraper, attr, val)

# Shared cloudscraper instance for better performance
_scraper_instance = None

def get_scraper():
    """
    Get or create a shared cloudscraper instance.

    Returns:
        cloudscraper instance for making API requests
    """
    global _scraper_instance
    if _scraper_instance is None:
        _scraper_instance = cloudscraper.create_scraper()
        if hasattr(_scraper_instance, 'max_concurrent_requests'):
            _scraper_instance.max_concurrent_requests = 10
        if hasattr(_scraper_instance, 'min_request_interval'):
            _scraper_instance.min_request_interval = 0.0
        if hasattr(_scraper_instance, 'rotate_tls_ciphers'):
            _scraper_instance.rotate_tls_ciphers = False

    # Defensive check on instance attributes
    if not hasattr(_scraper_instance, 'current_concurrent_requests'):
        _scraper_instance.current_concurrent_requests = 0

    return _scraper_instance


def get_default_headers() -> Dict[str, str]:
    """
    Get default headers for Investing.com API requests.

    Returns:
        Dictionary of default headers
    """
    return {"x-meta-ver": "14"}
