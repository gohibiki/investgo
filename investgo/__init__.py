"""
InvestGo - A Python library for fetching financial data from Investing.com

This library provides easy access to historical stock prices, ETF holdings,
technical indicators, market info, and search functionality for financial instruments.
"""

from .search import get_pair_id
from .historical import get_historical_prices, get_multiple_historical_prices
from .holdings import get_holdings
from .technical import get_technical_data
from .info import get_info
from .exceptions import (
    InvestGoError,
    APIError,
    InvalidParameterError,
    NoDataFoundError
)

__version__ = "1.0.8"
__author__ = "gohibiki"
__email__ = "gohibiki@protonmail.com"
__description__ = "A Python library for fetching financial data from Investing.com"

__all__ = [
    "get_pair_id",
    "get_historical_prices",
    "get_multiple_historical_prices",
    "get_holdings",
    "get_technical_data",
    "get_info",
    "InvestGoError",
    "APIError",
    "InvalidParameterError",
    "NoDataFoundError"
]

