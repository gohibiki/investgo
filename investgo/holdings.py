"""
Holdings and allocation data functionality for InvestGo.

This module provides functions to fetch ETF/fund holdings, asset allocation,
sector breakdown, and geographic allocation data.
"""

import cloudscraper
import pandas as pd
from typing import Dict, Any, Union, List
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Constants for holdings types
TOP_HOLDINGS = "top_holdings"
ASSETS_ALLOCATION = "assets_allocation"
STOCK_SECTOR = "stock_sector"
STOCK_REGION = "stock_region"
ALL_TYPES = "all"

# Valid holdings types for validation
VALID_HOLDINGS_TYPES = {TOP_HOLDINGS, ASSETS_ALLOCATION, STOCK_SECTOR, STOCK_REGION, ALL_TYPES}


def fetch_holdings_data(pair_id: str) -> Dict[str, Any]:
    """
    Fetch holdings data from Investing.com API.
    
    Args:
        pair_id: The Investing.com pair ID
        
    Returns:
        JSON response containing holdings information
        
    Raises:
        requests.exceptions.HTTPError: If the API request fails
    """
    scraper = cloudscraper.create_scraper()

    url = "https://aappapi.investing.com/get_screen.php"
    params = {
        "screen_ID": 125,
        "pair_ID": pair_id,
        "lang_ID": 1,
    }
    headers = {"x-meta-ver": "14"}

    try:
        response = scraper.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch holdings data for pair_id {pair_id}: {e}")
        raise


def to_numeric(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """
    Convert specified columns to numeric, handling errors gracefully.
    
    Args:
        df: DataFrame to process
        columns: List of column names to convert
        
    Returns:
        DataFrame with converted numeric columns
    """
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df


def _process_top_holdings(holdings_info: Dict[str, Any]) -> pd.DataFrame:
    """Process top holdings data."""
    if 'topHoldings' not in holdings_info or not holdings_info['topHoldings']:
        return pd.DataFrame([{'name': 'No information', 'weight': 0.0}])
    
    try:
        top_holdings_df = pd.DataFrame(holdings_info['topHoldings'])
        if top_holdings_df.shape[1] > 2:
            # Select name and weight columns (typically columns 0 and 2)
            top_holdings_df = top_holdings_df.iloc[:, [0, 2]]
            top_holdings_df.columns = ['name', 'weight']
            top_holdings_df = to_numeric(top_holdings_df, ['weight'])
            return top_holdings_df.sort_values(by='weight', ascending=False)
        else:
            return pd.DataFrame([{'name': 'No information', 'weight': 0.0}])
    except Exception as e:
        logger.warning(f"Error processing top holdings: {e}")
        return pd.DataFrame([{'name': 'No information', 'weight': 0.0}])


def _process_assets_allocation(holdings_info: Dict[str, Any]) -> pd.DataFrame:
    """Process assets allocation data."""
    if 'assetsAllocation' not in holdings_info or not holdings_info['assetsAllocation']:
        return pd.DataFrame([{'fldname': 'Other', 'val': 100.0}])
    
    try:
        assets_allocation_df = pd.DataFrame(holdings_info['assetsAllocation']).iloc[:, 1:3]
        # Filter out pie chart elements
        assets_allocation_df = assets_allocation_df[
            assets_allocation_df['fldname'] != 'other_pie_chart'
        ]
        assets_allocation_df = to_numeric(assets_allocation_df, ['val'])
        return assets_allocation_df.sort_values(by='val', ascending=False)
    except Exception as e:
        logger.warning(f"Error processing assets allocation: {e}")
        return pd.DataFrame([{'fldname': 'Other', 'val': 100.0}])


def _process_sector_data(holdings_info: Dict[str, Any]) -> pd.DataFrame:
    """Process sector allocation data."""
    try:
        stock_sector_df = pd.DataFrame(holdings_info.get('stockSectorData', []))
        bond_sector_df = pd.DataFrame(holdings_info.get('bondSectorData', []))
        
        sector_df = pd.concat([stock_sector_df, bond_sector_df], ignore_index=True)
        
        if not sector_df.empty and sector_df.shape[1] >= 3:
            # Select relevant columns (typically columns 1 and 2)
            sector_df = sector_df.iloc[:, 1:3]
            sector_df.columns = ['fieldname', 'val']
            
            if 'val' in sector_df.columns:
                sector_df = to_numeric(sector_df, ['val'])
                # Group by sector and sum values
                sector_df = sector_df.groupby('fieldname', as_index=False).sum()
                return sector_df.sort_values(by='val', ascending=False)
        
        return pd.DataFrame([{'fieldname': 'No information', 'val': 0.0}])
    except Exception as e:
        logger.warning(f"Error processing sector data: {e}")
        return pd.DataFrame([{'fieldname': 'No information', 'val': 0.0}])


def _process_region_data(holdings_info: Dict[str, Any], assets_allocation_df: pd.DataFrame) -> pd.DataFrame:
    """Process geographic region allocation data."""
    try:
        # Calculate asset proportions for weighting
        stock_proportion = 0
        bond_proportion = 0
        
        stock_row = assets_allocation_df[assets_allocation_df['fldname'] == 'Stock']
        if not stock_row.empty:
            stock_proportion = stock_row['val'].iloc[0] / 100
        
        bond_row = assets_allocation_df[assets_allocation_df['fldname'] == 'Bond']
        if not bond_row.empty:
            bond_proportion = bond_row['val'].iloc[0] / 100
            
        cash_row = assets_allocation_df[assets_allocation_df['fldname'] == 'Cash']
        if not cash_row.empty:
            bond_proportion += cash_row['val'].iloc[0] / 100
        
        # Process region data
        stock_region_df = pd.DataFrame(holdings_info.get('stockRegionData', []))
        bond_region_df = pd.DataFrame(holdings_info.get('bondRegionData', []))

        # Apply proportional weighting
        if not stock_region_df.empty:
            stock_region_df['val'] = pd.to_numeric(stock_region_df['val'], errors='coerce')
            stock_region_df['val'] *= stock_proportion
            
        if not bond_region_df.empty:
            bond_region_df['val'] = pd.to_numeric(bond_region_df['val'], errors='coerce')
            bond_region_df['val'] *= bond_proportion

        region_df = pd.concat([stock_region_df, bond_region_df], ignore_index=True)
        
        if not region_df.empty and 'val' in region_df.columns:
            region_df = to_numeric(region_df, ['val'])
            # Group by region and sum values
            first_col = region_df.columns[0]  # Dynamic column name handling
            region_df = region_df.groupby(first_col, as_index=False).sum()
            return region_df.sort_values(by='val', ascending=False)
        
        return pd.DataFrame([{'key': 'North America', 'val': 100.0}])
    except Exception as e:
        logger.warning(f"Error processing region data: {e}")
        return pd.DataFrame([{'key': 'North America', 'val': 100.0}])


def parse_holdings_data(json_data: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
    """
    Parse holdings data from JSON response into structured DataFrames.
    
    Args:
        json_data: Raw JSON response from the API
        
    Returns:
        Dictionary containing DataFrames for different holdings types:
        - top_holdings: Top holdings by weight
        - assets_allocation: Asset class breakdown
        - stock_sector: Sector allocation
        - stock_region: Geographic allocation
    """
    try:
        holdings_info = json_data['data'][0]['screen_data'].get('holdings_info', {})
    except (KeyError, IndexError):
        logger.warning("No holdings info found in response")
        holdings_info = {}

    if not holdings_info:
        # Return default empty data structure
        return {
            TOP_HOLDINGS: pd.DataFrame([{'name': 'No information', 'weight': 0.0}]),
            ASSETS_ALLOCATION: pd.DataFrame([{'fldname': 'Other', 'val': 100.0}]),
            STOCK_SECTOR: pd.DataFrame([{'fieldname': 'No information', 'val': 0.0}]),
            STOCK_REGION: pd.DataFrame([{'key': 'North America', 'val': 100.0}]),
        }

    # Process each type of holdings data
    top_holdings_df = _process_top_holdings(holdings_info)
    assets_allocation_df = _process_assets_allocation(holdings_info)
    sector_df = _process_sector_data(holdings_info)
    region_df = _process_region_data(holdings_info, assets_allocation_df)

    return {
        TOP_HOLDINGS: top_holdings_df,
        ASSETS_ALLOCATION: assets_allocation_df,
        STOCK_SECTOR: sector_df,
        STOCK_REGION: region_df,
    }


def get_holdings(
    pair_id: str, 
    holdings_type: str = "all"
) -> Union[pd.DataFrame, List[pd.DataFrame]]:
    """
    Get holdings and allocation data for ETFs and funds.
    
    Args:
        pair_id: The Investing.com pair ID
        holdings_type: Type of holdings data to retrieve:
            - "top_holdings": Top holdings by weight percentage
            - "assets_allocation": Breakdown by asset class (stocks, bonds, cash)
            - "stock_sector": Sector allocation 
            - "stock_region": Geographic allocation
            - "all": All holdings data types as a list
            
    Returns:
        pandas.DataFrame for specific holdings type, or list of DataFrames for "all"
        
    Raises:
        ValueError: If pair_id is missing or holdings_type is invalid
        
    Examples:
        >>> pair_id = get_pair_id(['QQQ'])[0]
        >>> top_holdings = get_holdings(pair_id, "top_holdings")
        >>> print(top_holdings.head())
        
        >>> all_data = get_holdings(pair_id, "all")
        >>> top_holdings, allocation, sectors, regions = all_data
    """
    if not pair_id:
        raise ValueError("Missing required parameter: pair_id")
    
    if holdings_type not in VALID_HOLDINGS_TYPES:
        raise ValueError(
            f"Invalid holdings_type '{holdings_type}'. "
            f"Choose from: {', '.join(sorted(VALID_HOLDINGS_TYPES))}"
        )

    logger.info(f"Fetching holdings data for pair_id {pair_id}, type: {holdings_type}")
    
    try:
        json_data = fetch_holdings_data(pair_id)
        holdings_data = parse_holdings_data(json_data)

        if holdings_type == ALL_TYPES:
            return [
                holdings_data[TOP_HOLDINGS],
                holdings_data[ASSETS_ALLOCATION], 
                holdings_data[STOCK_SECTOR],
                holdings_data[STOCK_REGION]
            ]
        else:
            return holdings_data[holdings_type]
            
    except Exception as e:
        logger.error(f"Error retrieving holdings data: {e}")
        raise
