"""
Utility functions and shared resources for InvestGo.
"""

import requests
from typing import Dict

# Investing.com's Cloudflare setup rejects the default python-requests
# User-Agent but accepts any real browser UA over plain TLS, so a regular
# requests.Session with a browser User-Agent is all that's needed.
# cloudscraper is no longer used: its 1.x releases are 403-blocked by the
# site (their custom TLS fingerprint is flagged) and 3.x is GitHub-only.
_BROWSER_USER_AGENT = (
    "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36"
)

# Shared session instance for better performance
_scraper_instance = None

def get_scraper():
    """
    Get or create a shared requests session.

    Returns:
        requests.Session for making API requests
    """
    global _scraper_instance
    if _scraper_instance is None:
        _scraper_instance = requests.Session()
        _scraper_instance.headers.update({"User-Agent": _BROWSER_USER_AGENT})
    return _scraper_instance


def get_default_headers() -> Dict[str, str]:
    """
    Get default headers for Investing.com API requests.

    Returns:
        Dictionary of default headers
    """
    return {"x-meta-ver": "14"}
