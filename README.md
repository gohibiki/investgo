# InvestGo

[![PyPI version](https://badge.fury.io/py/investgo.svg)](https://badge.fury.io/py/investgo)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python library for fetching financial data from Investing.com, including historical stock prices, ETF holdings, and technical indicators.

## Features

- 📈 **Historical Data**: Fetch historical stock prices with automatic date range chunking
- 🏢 **Holdings Data**: Get ETF/fund holdings, asset allocation, and sector breakdowns
- 📊 **Technical Analysis**: Access technical indicators and pivot points
- 🔍 **Symbol Search**: Find stock IDs by ticker symbols
- ⚡ **Concurrent Processing**: Fast data retrieval using multithreading
- 🐼 **Pandas Integration**: Returns data as pandas DataFrames for easy analysis

## Installation

```bash
pip install investgo
```

## Quick Start

```python
from investgo import get_pair_id, get_historical_prices, get_holdings

# Get stock ID for a ticker
stock_id = get_pair_id(['QQQ'])[0]

# Fetch historical data
df = get_historical_prices(stock_id, "01012021", "01012024")
print(df.head())

# Get ETF holdings
holdings = get_holdings(stock_id, "top_holdings")
print(holdings)
```

## API Reference

### Historical Data

#### `get_historical_prices(stock_id, date_from, date_to)`

Fetch historical price data for a given stock.

**Parameters:**
- `stock_id` (str): The Investing.com pair ID
- `date_from` (str): Start date in "DDMMYYYY" format
- `date_to` (str): End date in "DDMMYYYY" format

**Returns:** pandas.DataFrame with columns: price, open, high, low, vol, perc_chg

```python
# Example
data = get_historical_prices("1075", "01012023", "31122023")
```

#### `get_multiple_historical_prices(stock_ids, date_from, date_to)`

Fetch historical data for multiple stocks concurrently.

**Parameters:**
- `stock_ids` (list): List of Investing.com pair IDs
- `date_from` (str): Start date in "DDMMYYYY" format  
- `date_to` (str): End date in "DDMMYYYY" format

**Returns:** pandas.DataFrame with concatenated data

### Search Functions

#### `get_pair_id(stock_ids, display_mode="first", name="no")`

Search for stock pair IDs by ticker symbols.

**Parameters:**
- `stock_ids` (str or list): Ticker symbol(s) to search
- `display_mode` (str): "first" for first match, "all" for all matches
- `name` (str): "yes" to return names along with IDs

**Returns:** List of pair IDs or DataFrame (depending on parameters)

```python
# Get pair ID for Apple
apple_id = get_pair_id('AAPL')[0]

# Get IDs and names for multiple tickers
ids, names = get_pair_id(['AAPL', 'MSFT'], name='yes')

# Get all search results
all_results = get_pair_id('AAPL', display_mode='all')
```

### Holdings Data

#### `get_holdings(pair_id, holdings_type="all")`

Get holdings and allocation data for ETFs and funds.

**Parameters:**
- `pair_id` (str): The Investing.com pair ID
- `holdings_type` (str): Type of data to retrieve:
  - `"top_holdings"`: Top holdings by weight
  - `"assets_allocation"`: Asset class breakdown (stocks, bonds, cash)
  - `"stock_sector"`: Sector allocation
  - `"stock_region"`: Geographic allocation
  - `"all"`: All holdings data types

**Returns:** pandas.DataFrame or list of DataFrames

```python
# Get top holdings for QQQ ETF
qqq_id = get_pair_id('QQQ')[0]
top_holdings = get_holdings(qqq_id, "top_holdings")

# Get asset allocation
allocation = get_holdings(qqq_id, "assets_allocation")

# Get all holdings data
all_data = get_holdings(qqq_id, "all")
```

### Technical Analysis

#### `get_technical_data(tech_type='pivot_points', interval='5min')`

Get technical analysis data and indicators.

**Parameters:**
- `tech_type` (str): Type of technical data ('pivot_points', 'ti', 'ma')
- `interval` (str): Time interval ('5min', '15min', 'hourly', 'daily')

**Returns:** pandas.DataFrame with technical indicators

## Complete Example

```python
from investgo import get_pair_id, get_historical_prices, get_holdings
import matplotlib.pyplot as plt

# Search for QQQ ETF
stock_ids = get_pair_id(['QQQ'])
qqq_id = stock_ids[0]

# Get 1 year of historical data
historical_data = get_historical_prices(qqq_id, "01012023", "31122023")

# Get top holdings
holdings = get_holdings(qqq_id, "top_holdings")

# Plot price chart
historical_data['price'].plot(title='QQQ Price History')
plt.show()

# Display top 10 holdings
print("Top 10 Holdings:")
print(holdings.head(10))
```

## Error Handling

The library includes basic error handling, but you should wrap calls in try-except blocks for production use:

```python
try:
    stock_id = get_pair_id('INVALID_TICKER')[0]
    data = get_historical_prices(stock_id, "01012023", "31122023")
except ValueError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Requirements

- Python 3.6+
- cloudscraper >= 1.2.68
- pandas >= 2.2.1

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Disclaimer

This library is for educational and research purposes. Please respect Investing.com's terms of service and rate limits when using this library.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENCE.txt) file for details.
