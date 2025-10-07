"""
Technical analysis data functionality for InvestGo.
"""

import pandas as pd
from typing import Dict, Any, List, Optional
import logging

from .exceptions import InvalidParameterError, APIError
from .utils import get_scraper, get_default_headers

logger = logging.getLogger(__name__)

# Valid technical data types
VALID_TECH_TYPES = {'ti', 'ma', 'pivot_points', 'summary'}

# Valid intervals
VALID_INTERVALS = {'5min', '15min', '30min', 'hourly', '5hourly', 'daily', 'weekly', 'monthly'}

# Timeframe to seconds mapping
TIMEFRAME_SECONDS = {
    '5min': '300',
    '15min': '900',
    '30min': '1800',
    'hourly': '3600',
    '5hourly': '18000',
    'daily': '86400',
    'weekly': '604800',
    'monthly': '2592000'
}


def fetch_technical_data(pair_id: str) -> Dict[str, Any]:
    """
    Fetch technical analysis data from Investing.com API.

    Args:
        pair_id: The Investing.com pair ID

    Returns:
        JSON response containing technical data

    Raises:
        APIError: If the API request fails
    """
    scraper = get_scraper()

    url = "https://aappapi.investing.com/get_screen.php"
    params = {
        "screen_ID": 25,
        "pair_ID": pair_id,
        "lang_ID": 1,
        "additionalTimeframes": "Yes"
    }
    headers = get_default_headers()

    try:
        response = scraper.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch technical data for pair_id {pair_id}: {e}")
        raise APIError(f"Failed to fetch technical data for pair_id {pair_id}") from e


def get_technical_data(
    pair_id: str,
    tech_type: str = 'pivot_points',
    interval: str = 'daily'
) -> pd.DataFrame:
    """
    Get technical analysis data for a financial instrument.

    Args:
        pair_id: The Investing.com pair ID
        tech_type: Type of technical data to retrieve:
            - 'pivot_points': Support and resistance levels
            - 'ti': Technical indicators
            - 'ma': Moving averages
            - 'summary': Technical summary (main, MA, and TI summaries)
        interval: Time interval for the data:
            - '5min': 5-minute intervals
            - '15min': 15-minute intervals
            - '30min': 30-minute intervals
            - 'hourly': Hourly intervals
            - '5hourly': 5-hour intervals
            - 'daily': Daily intervals
            - 'weekly': Weekly intervals
            - 'monthly': Monthly intervals

    Returns:
        pandas.DataFrame with technical analysis data

    Raises:
        InvalidParameterError: If tech_type or interval is invalid
        APIError: If API request fails

    Examples:
        >>> # Get daily pivot points
        >>> pivot_data = get_technical_data('29049', 'pivot_points', 'daily')

        >>> # Get technical summary
        >>> summary = get_technical_data('29049', 'summary', 'daily')
    """
    # Validate parameters
    if tech_type not in VALID_TECH_TYPES:
        raise InvalidParameterError(
            f"Invalid tech_type '{tech_type}'. "
            f"Choose from: {', '.join(sorted(VALID_TECH_TYPES))}"
        )

    if interval not in VALID_INTERVALS:
        raise InvalidParameterError(
            f"Invalid interval '{interval}'. "
            f"Choose from: {', '.join(sorted(VALID_INTERVALS))}"
        )

    logger.info(f"Fetching {tech_type} data for interval {interval}")

    try:
        data = fetch_technical_data(pair_id)

        # Find the matching timeframe in the response
        target_timeframe = TIMEFRAME_SECONDS[interval]

        for item in data.get('data', []):
            screen_data = item.get('screen_data', {})
            for tech_data in screen_data.get('technical_data', []):
                # Handle both string and int timeframes
                current_timeframe = str(tech_data.get('timeframe', ''))

                if current_timeframe == target_timeframe:

                    # Handle summary type
                    if tech_type == 'summary':
                        summary_data = []

                        # Main summary
                        main = tech_data.get('main_summary', {})
                        if main:
                            summary_data.append({
                                'type': 'Overall',
                                'signal': main.get('text'),
                                'action': main.get('action')
                            })

                        # MA summary
                        ma_sum = tech_data.get('ma_summary', {})
                        if ma_sum:
                            summary_data.append({
                                'type': 'Moving Averages',
                                'signal': ma_sum.get('ma_text'),
                                'buy': ma_sum.get('ma_buy'),
                                'sell': ma_sum.get('ma_sell')
                            })

                        # TI summary
                        ti_sum = tech_data.get('ti_summary', {})
                        if ti_sum:
                            summary_data.append({
                                'type': 'Technical Indicators',
                                'signal': ti_sum.get('ti_text'),
                                'buy': ti_sum.get('ti_buy'),
                                'sell': ti_sum.get('ti_sell'),
                                'neutral': ti_sum.get('ti_neutral')
                            })

                        # ATR (Volatility)
                        ti_items = tech_data.get('ti', [])
                        atr_item = next((item for item in ti_items if 'ATR' in item.get('text', '')), None)
                        if atr_item:
                            summary_data.append({
                                'type': 'ATR (Volatility)',
                                'signal': atr_item.get('action'),
                                'value': atr_item.get('value')
                            })

                        df = pd.DataFrame(summary_data)
                        logger.info(f"Successfully retrieved summary data")
                        return df

                    # Handle other types
                    tech_items = tech_data.get(tech_type, [])

                    if not tech_items:
                        logger.warning(f"No {tech_type} data available for interval {interval}")
                        return pd.DataFrame()

                    # Parse based on tech_type
                    if tech_type == 'ti':
                        df = pd.DataFrame(tech_items)
                        if not df.empty:
                            df = df[['text', 'value', 'action']]
                            df.columns = ['indicator', 'value', 'signal']

                    elif tech_type == 'ma':
                        df = pd.DataFrame(tech_items)
                        if not df.empty:
                            df = df[['text', 'simple', 'simple_action', 'exponential', 'exponential_action']]
                            df.columns = ['period', 'simple_ma', 'simple_signal', 'exponential_ma', 'exponential_signal']

                    elif tech_type == 'pivot_points':
                        df = pd.DataFrame(tech_items)
                        if not df.empty:
                            df = df[['text', 'value_class', 'value_fib']]
                            df.columns = ['level', 'classic', 'fibonacci']
                    else:
                        df = pd.DataFrame(tech_items)

                    logger.info(f"Successfully retrieved {len(df)} {tech_type} data points")
                    return df

        logger.warning(f"No {tech_type} data available for interval {interval}")
        return pd.DataFrame()

    except Exception as e:
        logger.error(f"Error retrieving technical data: {e}")
        raise


def get_available_intervals() -> List[str]:
    """Get list of available time intervals."""
    return list(VALID_INTERVALS)


def get_available_tech_types() -> List[str]:
    """Get list of available technical data types."""
    return list(VALID_TECH_TYPES)
