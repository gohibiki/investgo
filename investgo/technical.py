"""
Technical analysis data functionality for InvestGo.

This module provides functions to fetch technical indicators, moving averages,
and pivot points from Investing.com.
"""

import cloudscraper
import pandas as pd
from typing import Dict, Any, List, Optional
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Valid technical data types
VALID_TECH_TYPES = {'ti', 'ma', 'pivot_points'}

# Valid intervals  
VALID_INTERVALS = {'5min', '15min', 'hourly', 'daily'}

# Interval mapping
INTERVAL_MAP = {
    '5min': 0,
    '15min': 1, 
    'hourly': 2,
    'daily': 3
}


def fetch_technical_data(pair_id: str = '651') -> Dict[str, Any]:
    """
    Fetch technical analysis data from Investing.com API.
    
    Args:
        pair_id: The Investing.com pair ID (defaults to '651' for S&P 500)
        
    Returns:
        JSON response containing technical data
        
    Raises:
        requests.exceptions.HTTPError: If the API request fails
    """
    scraper = cloudscraper.create_scraper()
    
    url = "https://aappapi.investing.com/get_screen.php"
    params = {
        "screen_ID": 25,
        "pair_ID": pair_id,
        "lang_ID": 1,
    }
    headers = {"x-meta-ver": "14"}
    
    try:
        response = scraper.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch technical data for pair_id {pair_id}: {e}")
        raise


def parse_technical_data(data: Dict[str, Any], tech_type: str) -> List[pd.DataFrame]:
    """
    Parse technical data from JSON response.
    
    Args:
        data: JSON response from the API
        tech_type: Type of technical data ('ti', 'ma', 'pivot_points')
        
    Returns:
        List of DataFrames containing technical data for different intervals
        
    Note:
        Different tech_types return different column structures:
        - 'ti': Technical indicators (columns 0, 1)
        - 'ma': Moving averages (columns 0, 1, 2, 6, 7)  
        - 'pivot_points': Pivot points (columns 0, 1, 5)
    """
    dfs = []
    
    try:
        for item in data.get('data', []):
            screen_data = item.get('screen_data', {})
            for tech_data in screen_data.get('technical_data', []):
                pivot_points = tech_data.get(tech_type, [])
                
                if not pivot_points:
                    continue
                
                # Select appropriate columns based on tech_type
                if tech_type == 'ti':
                    df = pd.DataFrame(pivot_points).iloc[:, [0, 1]]
                    if len(df.columns) >= 2:
                        df.columns = ['indicator', 'value']
                elif tech_type == 'ma':
                    df = pd.DataFrame(pivot_points).iloc[:, [0, 1, 2, 6, 7]]
                    if len(df.columns) >= 5:
                        df.columns = ['period', 'simple_ma', 'exponential_ma', 'buy_sell', 'signal']
                elif tech_type == 'pivot_points':
                    df = pd.DataFrame(pivot_points).iloc[:, [0, 1, 5]]
                    if len(df.columns) >= 3:
                        df.columns = ['level', 'value', 'signal']
                else:
                    df = pd.DataFrame(pivot_points)
                
                dfs.append(df)
                
    except Exception as e:
        logger.error(f"Error parsing technical data: {e}")
    
    return dfs


def get_technical_data(
    tech_type: str = 'pivot_points', 
    interval: str = '5min',
    pair_id: str = '651'
) -> pd.DataFrame:
    """
    Get technical analysis data for a financial instrument.
    
    Args:
        tech_type: Type of technical data to retrieve:
            - 'pivot_points': Support and resistance levels
            - 'ti': Technical indicators 
            - 'ma': Moving averages
        interval: Time interval for the data:
            - '5min': 5-minute intervals
            - '15min': 15-minute intervals  
            - 'hourly': Hourly intervals
            - 'daily': Daily intervals
        pair_id: The Investing.com pair ID (defaults to S&P 500)
        
    Returns:
        pandas.DataFrame with technical analysis data
        
    Raises:
        ValueError: If tech_type or interval is invalid
        requests.exceptions.HTTPError: If API request fails
        
    Examples:
        >>> # Get daily pivot points for S&P 500
        >>> pivot_data = get_technical_data('pivot_points', 'daily')
        >>> print(pivot_data)
        
        >>> # Get moving averages for a specific stock
        >>> stock_id = get_pair_id(['AAPL'])[0]
        >>> ma_data = get_technical_data('ma', 'daily', stock_id)
    """
    # Validate parameters
    if tech_type not in VALID_TECH_TYPES:
        raise ValueError(
            f"Invalid tech_type '{tech_type}'. "
            f"Choose from: {', '.join(sorted(VALID_TECH_TYPES))}"
        )
    
    if interval not in VALID_INTERVALS:
        raise ValueError(
            f"Invalid interval '{interval}'. "
            f"Choose from: {', '.join(sorted(VALID_INTERVALS))}"
        )
    
    logger.info(f"Fetching {tech_type} data for interval {interval}")
    
    try:
        data = fetch_technical_data(pair_id)
        dfs = parse_technical_data(data, tech_type)
        
        # Get data for the specified interval
        interval_index = INTERVAL_MAP.get(interval, 0)
        
        if dfs and len(dfs) > interval_index:
            result_df = dfs[interval_index]
            logger.info(f"Successfully retrieved {len(result_df)} {tech_type} data points")
            return result_df
        else:
            logger.warning(f"No {tech_type} data available for interval {interval}")
            return pd.DataFrame()
            
    except Exception as e:
        logger.error(f"Error retrieving technical data: {e}")
        raise


def get_available_intervals() -> List[str]:
    """
    Get list of available time intervals.
    
    Returns:
        List of valid interval strings
    """
    return list(VALID_INTERVALS)


def get_available_tech_types() -> List[str]:
    """
    Get list of available technical data types.
    
    Returns:
        List of valid technical data type strings
    """
    return list(VALID_TECH_TYPES)
