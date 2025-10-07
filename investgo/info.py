"""
Info and overview data functionality for InvestGo.
"""

import pandas as pd
from typing import Dict, Any, Optional
import logging

from .exceptions import APIError
from .utils import get_scraper, get_default_headers

logger = logging.getLogger(__name__)


def _extract_from_overview_table(overview_table: list, key: str) -> Optional[str]:
    """Extract value from overview_table by key."""
    for item in overview_table:
        if item.get('key') == key:
            return item.get('val')
    return None


def fetch_info_data(pair_id: str) -> Dict[str, Any]:
    """
    Fetch info and overview data from Investing.com API (screen_ID 22).

    Args:
        pair_id: The Investing.com pair ID

    Returns:
        JSON response containing overview and market data

    Raises:
        APIError: If the API request fails
    """
    scraper = get_scraper()

    url = "https://aappapi.investing.com/get_screen.php"
    params = {
        "screen_ID": 22,
        "pair_ID": pair_id,
        "lang_ID": 1,
        "additionalTimeframes": "Yes",
        "include_pair_attr": "true"
    }
    headers = get_default_headers()

    try:
        response = scraper.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch info data for pair_id {pair_id}: {e}")
        raise APIError(f"Failed to fetch info data for pair_id {pair_id}") from e


def get_info(pair_id: str) -> pd.DataFrame:
    """
    Get comprehensive info and overview data for a financial instrument.

    Returns a single DataFrame with all relevant information including:
    - Current price data (last, change, change_percent, open, high, low)
    - Volume data (volume, avg_volume_3m)
    - 52-week range (52w_high, 52w_low)
    - Technical summary and sentiment
    - Additional metrics (P/E ratio, market cap, dividend, etc. when available)

    Args:
        pair_id: The Investing.com pair ID

    Returns:
        pandas.DataFrame with one row containing all info fields

    Raises:
        APIError: If API request fails

    Examples:
        >>> # Get info data for S&P 500
        >>> info = get_info('29049')
        >>> print(info)
    """
    logger.info(f"Fetching info data for pair_id {pair_id}")

    try:
        data = fetch_info_data(pair_id)

        # Navigate to pairs_data
        pairs_data = (data.get('data', [{}])[0]
                      .get('screen_data', {})
                      .get('pairs_data', [{}])[0])

        if not pairs_data:
            logger.warning("No pairs data found in response")
            return pd.DataFrame()

        # Get pairs_attr for additional metadata
        pairs_attr = (data.get('data', [{}])[0]
                      .get('screen_data', {})
                      .get('pairs_attr', [{}]))
        pair_attr = pairs_attr[0] if pairs_attr else {}

        if not pair_attr:
            logger.warning("No pairs_attr found in response - some fields may be missing")

        # Build comprehensive info dictionary
        info_data = {
            # Instrument Identity
            'symbol': pair_attr.get('pair_symbol'),
            'name': pair_attr.get('pair_name'),
            'full_name': pair_attr.get('pair_name_base'),
            'exchange': pair_attr.get('exchange_name'),
            'currency': pair_attr.get('currency_in'),
            'pair_type': pairs_data.get('pair_type_section'),
            'is_crypto': pairs_data.get('isCrypto'),

            # Current Price Data
            'last': pairs_data.get('last'),
            'bid': pairs_data.get('bid'),
            'ask': pairs_data.get('ask'),
            'change': pairs_data.get('change_val'),
            'change_percent': pairs_data.get('change_percent_val'),
            'open': pairs_data.get('open'),
            'high': pairs_data.get('high'),
            'low': pairs_data.get('low'),
            'previous_close': pairs_data.get('last_close_value'),

            # Volume
            'volume': pairs_data.get('volume'),
            'avg_volume_3m': pairs_data.get('avg_volume'),

            # 52-Week Range
            '52w_high': pairs_data.get('a52_week_high'),
            '52w_low': pairs_data.get('a52_week_low'),

            # Performance
            'one_year_return': pairs_data.get('one_year_return'),

            # Technical Summary
            'technical_summary': pairs_data.get('technical_summary_text'),

            # Sentiment
            'bullish': pairs_data.get('sentiments', {}).get('bullish'),
            'bearish': pairs_data.get('sentiments', {}).get('bearish'),

            # Market Status
            'exchange_is_open': pairs_data.get('exchange_is_open'),
            'last_timestamp': pairs_data.get('last_timestamp'),

            # Stock-specific (when available)
            'eps': pairs_data.get('eq_eps'),
            'pe_ratio': pairs_data.get('eq_pe_ratio'),
            'market_cap': pairs_data.get('eq_market_cap'),
            'shares_outstanding': _extract_from_overview_table(pairs_data.get('overview_table', []), 'Shares Outstanding'),
            'beta': pairs_data.get('eq_beta'),
            'revenue': pairs_data.get('eq_revenue'),
            'dividend': pairs_data.get('eq_dividend'),
            'dividend_yield': pairs_data.get('eq_dividend_yield'),
            'next_earnings_date': pairs_data.get('next_earnings_date'),

            # Index-specific
            'number_of_components': pairs_data.get('number_of_components'),
        }

        df = pd.DataFrame([info_data])
        logger.info(f"Successfully retrieved info data")
        return df

    except Exception as e:
        logger.error(f"Error retrieving info data: {e}")
        raise
