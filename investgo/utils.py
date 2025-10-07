"""
Utility functions and shared resources for InvestGo.
"""

import cloudscraper
from typing import Dict

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
    return _scraper_instance


def get_default_headers() -> Dict[str, str]:
    """
    Get default headers for Investing.com API requests.

    Returns:
        Dictionary of default headers
    """
    return {"x-meta-ver": "14"}
