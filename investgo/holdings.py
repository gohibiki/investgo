import cloudscraper
import pandas as pd

TOP_HOLDINGS = "top_holdings"
ASSETS_ALLOCATION = "assets_allocation"
STOCK_SECTOR = "stock_sector"
STOCK_REGION = "stock_region"
ALL_TYPES = "all"

def fetch_holdings_data(pair_id):
    scraper = cloudscraper.create_scraper()

    url = "https://aappapi.investing.com/get_screen.php"
    params = {
        "screen_ID": 125,
        "pair_ID": pair_id,
        "lang_ID": 1,
    }

    headers = {
        "x-meta-ver": "14",
    }

    response = scraper.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response.json()

def to_numeric(df, columns):
    df[columns] = df[columns].apply(pd.to_numeric, errors='coerce')
    return df

def parse_holdings_data(json_data):
    holdings_info = json_data['data'][0]['screen_data'].get('holdings_info', {})

    # Handle Top Holdings
    if 'topHoldings' in holdings_info:
        top_holdings_df = pd.DataFrame(holdings_info['topHoldings'])
        if top_holdings_df.shape[1] > 2:
            top_holdings_df = top_holdings_df.iloc[:, [0, 2]]
            top_holdings_df = to_numeric(top_holdings_df, ['weight'])
            top_holdings_df = top_holdings_df.sort_values(by='weight', ascending=False)
        else:
            top_holdings_df = pd.DataFrame([{'name': 'No information', 'weight': 0.0}])
    else:
        top_holdings_df = pd.DataFrame([{'name': 'No information', 'weight': 0.0}])

    # Handle Assets Allocation
    if 'assetsAllocation' in holdings_info and holdings_info['assetsAllocation']:
        assets_allocation_df = pd.DataFrame(holdings_info['assetsAllocation']).iloc[:, 1:3]
        assets_allocation_df = assets_allocation_df[assets_allocation_df['fldname'] != 'other_pie_chart']
        assets_allocation_df = to_numeric(assets_allocation_df, ['val'])
        assets_allocation_df = assets_allocation_df.sort_values(by='val', ascending=False)
    else:
        assets_allocation_df = pd.DataFrame([{'fldname': 'Other', 'val': 100.0}])

    # Safely extract stock, bond, and cash proportions
    stock_proportion = assets_allocation_df.loc[assets_allocation_df['fldname'] == 'Stock', 'val']
    stock_proportion = stock_proportion.values[0] / 100 if not stock_proportion.empty else 0

    bond_proportion = assets_allocation_df.loc[assets_allocation_df['fldname'] == 'Bond', 'val']
    bond_proportion = bond_proportion.values[0] / 100 if not bond_proportion.empty else 0

    cash_proportion = assets_allocation_df.loc[assets_allocation_df['fldname'] == 'Cash', 'val']
    cash_proportion = cash_proportion.values[0] / 100 if not cash_proportion.empty else 0

    # Combine bond and cash proportions
    bond_proportion += cash_proportion

    # Handle Stock Sector Data (if any)
    stock_sector_df = pd.DataFrame(holdings_info.get('stockSectorData', []))
    bond_sector_df = pd.DataFrame(holdings_info.get('bondSectorData', []))
    
    sector_df = pd.concat([stock_sector_df, bond_sector_df], ignore_index=True)
    if not sector_df.empty:
        sector_df = sector_df.iloc[:, 1:3]  # Adjust columns as necessary
        if 'val' in sector_df.columns:
            sector_df = to_numeric(sector_df, ['val'])
            sector_df = sector_df.groupby(sector_df.columns[0], as_index=False).sum()  # Group by sector and sum the values
            sector_df = sector_df.sort_values(by='val', ascending=False)
    else:
        sector_df = pd.DataFrame([{'fieldname': 'No information', 'val': 0.0}])

    # Adjust Stock and Bond Region Data by their proportions
    stock_region_df = pd.DataFrame(holdings_info.get('stockRegionData', []))
    bond_region_df = pd.DataFrame(holdings_info.get('bondRegionData', []))

    # Convert 'val' columns to numeric before applying proportions
    if not stock_region_df.empty:
        stock_region_df['val'] = pd.to_numeric(stock_region_df['val'], errors='coerce')
        stock_region_df['val'] *= stock_proportion
    if not bond_region_df.empty:
        bond_region_df['val'] = pd.to_numeric(bond_region_df['val'], errors='coerce')
        bond_region_df['val'] *= bond_proportion

    region_df = pd.concat([stock_region_df, bond_region_df], ignore_index=True)
    if not region_df.empty:
        if 'val' in region_df.columns:
            region_df = to_numeric(region_df, ['val'])
            region_df = region_df.groupby(region_df.columns[0], as_index=False).sum()  # Group by region and sum the values
            region_df = region_df.sort_values(by='val', ascending=False)
    else:
        region_df = pd.DataFrame([{'key': 'North America', 'val': 100.0}])

    return {
        TOP_HOLDINGS: top_holdings_df,
        ASSETS_ALLOCATION: assets_allocation_df,
        STOCK_SECTOR: sector_df,  # Combined sector data
        STOCK_REGION: region_df,  # Combined region data
    }


def get_holdings(pair_id, holdings_type="all"):
    if not pair_id:
        raise ValueError("Missing required parameter: pair_id")

    json_data = fetch_holdings_data(pair_id)
    holdings_data = parse_holdings_data(json_data)

    if holdings_type in holdings_data:
        return holdings_data[holdings_type]
    elif holdings_type == ALL_TYPES:
        return list(holdings_data.values())
    else:
        raise ValueError(f"Invalid holdings_type. Choose from 'top_holdings', 'assets_allocation', 'stock_sector', 'stock_region', 'all'")
