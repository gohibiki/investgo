"""
Search functionality for InvestGo library.

This module provides functions to search for financial instruments
and retrieve their pair IDs from Investing.com.
"""

import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Union, Tuple, Dict, Any
import logging

from .exceptions import InvalidParameterError, NoDataFoundError, APIError
from .utils import get_scraper, get_default_headers

# Set up logging
logger = logging.getLogger(__name__)


def fetch_pair_data(search_string: str) -> Tuple[Dict[str, Any], str]:
    """
    Fetch pair data for a given search string from Investing.com API.

    Args:
        search_string: The ticker symbol or name to search for

    Returns:
        Tuple containing the JSON response and the original search string

    Raises:
        APIError: If the API request fails
    """
    scraper = get_scraper()
    url = "https://aappapi.investing.com/search_by_type.php"
    params = {
        "section": "quotes",
        "string": search_string,
        "lang_ID": 1,
        "include_pair_attr": "true"
    }
    headers = get_default_headers()

    try:
        response = scraper.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json(), search_string
    except Exception as e:
        raise APIError(f"Failed to fetch pair data for '{search_string}'") from e


def json_to_dataframe(json_data_list: List[Tuple[Dict[str, Any], str]]) -> pd.DataFrame:
    """
    Convert JSON response data to a pandas DataFrame.
    
    Args:
        json_data_list: List of tuples containing JSON data and search strings
        
    Returns:
        pandas.DataFrame with columns: pair_id, Ticker, Description, Exchange, search_string
    """
    df_list = []
    for json_data, search_string in json_data_list:
        if "data" in json_data and "quotes" in json_data["data"]:
            quotes = json_data["data"]["quotes"]
            df_quotes = pd.DataFrame(quotes)
            try:
                df_quotes = df_quotes.loc[:, [
                    "pair_ID", 
                    "search_main_text", 
                    "search_main_longtext", 
                    "search_main_subtext"
                ]]
                df_quotes.rename(
                    columns={
                        "pair_ID": "pair_id",
                        "search_main_text": "Ticker",
                        "search_main_longtext": "Description",
                        "search_main_subtext": "Exchange",
                    },
                    inplace=True,
                )
                # FIXED: Convert pair_id to string to ensure consistency
                df_quotes['pair_id'] = df_quotes['pair_id'].astype(str)
                df_quotes['search_string'] = search_string
                df_list.append(df_quotes)
            except KeyError as e:
                logger.warning(f"KeyError: {e} in search string: {search_string}")
        else:
            logger.warning(f"Missing 'quotes' in 'data' for search string: {search_string}")
    
    if df_list:
        return pd.concat(df_list, ignore_index=True)
    return pd.DataFrame()


def get_pair_id(
    stock_ids: Union[str, List[str]], 
    display_mode: str = "first", 
    name: str = "no"
) -> Union[List[str], Tuple[List[str], List[str]], pd.DataFrame]:
    """
    Get pair IDs for given stock ticker symbols.
    
    Args:
        stock_ids: Single ticker symbol (str) or list of ticker symbols
        display_mode: "first" to return first match, "all" to return all matches
        name: "yes" to return names along with IDs, "no" for IDs only
        
    Returns:
        - If display_mode="first" and name="no": List of pair IDs
        - If display_mode="first" and name="yes": Tuple of (pair_ids, names)
        - If display_mode="all": pandas.DataFrame with all search results
        
    Raises:
        InvalidParameterError: If parameters are invalid
        NoDataFoundError: If no data is found
        
    Examples:
        >>> get_pair_id('AAPL')
        ['14958']
        
        >>> get_pair_id(['AAPL', 'MSFT'], name='yes')
        (['14958', '20936'], ['Apple Inc', 'Microsoft Corporation'])
    """
    if not stock_ids:
        raise InvalidParameterError("Missing required parameters: stock_ids cannot be empty")

    if isinstance(stock_ids, str):
        stock_ids = [stock_ids]

    with ThreadPoolExecutor() as executor:
        future_to_search = {
            executor.submit(fetch_pair_data, stock_id): stock_id 
            for stock_id in stock_ids
        }
        results = []
        for future in as_completed(future_to_search):
            try:
                result = future.result()
                results.append(result)
            except Exception as exc:
                logger.error(f'Error fetching data for {future_to_search[future]}: {exc}')
    
    df = json_to_dataframe(results)

    if df.empty:
        raise NoDataFoundError("No data found for the provided stock IDs")

    if display_mode == "all":
        if len(stock_ids) > 1:
            raise InvalidParameterError("Display mode 'all' can only be used with a single stock ID")
        return df
    elif display_mode == "first" and name == 'yes':
        return df.groupby('search_string')['pair_id'].first().tolist(), df.groupby('search_string')['Description'].first().tolist()
    elif display_mode == "first":
        return df.groupby('search_string')['pair_id'].first().tolist()
    else:
        raise InvalidParameterError("Invalid display_mode. Choose 'first' or 'all'")
