# InvestGo

[![PyPI version](https://badge.fury.io/py/investgo.svg)](https://badge.fury.io/py/investgo)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python library for fetching financial data from Investing.com, including historical stock prices, ETF holdings, technical indicators, and market info.

## Features

- 📈 **Historical Data**: Fetch historical stock prices with automatic date range chunking
- 🏢 **Holdings Data**: Get ETF/fund holdings, asset allocation, and sector breakdowns
- 📊 **Technical Analysis**: Access pivot points, moving averages, technical indicators, and trading signals across 8 timeframes
- 📰 **Market Info**: Get comprehensive overview data including price, volume, fundamentals, sentiment, and technical summaries
- 🔍 **Symbol Search**: Find pair IDs by ticker symbols
- ⚡ **Concurrent Processing**: Fast data retrieval using multithreading
- 🐼 **Pandas Integration**: Returns data as pandas DataFrames for easy analysis

## Installation

```bash
pip install investgo
```

## Quick Start

```python
from investgo import get_pair_id, get_historical_prices, get_holdings, get_info

# Get pair ID for a ticker
pair_id = get_pair_id(['AAPL'])[0]

# Get market info (price, fundamentals, sentiment)
info = get_info(pair_id)
print(info)

# Fetch historical data
df = get_historical_prices(pair_id, "01012021", "01012024")
print(df.head())

# Get ETF holdings
qqq_id = get_pair_id(['QQQ'])[0]
holdings = get_holdings(qqq_id, "top_holdings")
print(holdings)
```

## API Reference

### Historical Data

#### `get_historical_prices(pair_id, date_from, date_to)`

Fetch historical price data for a given stock.

**Parameters:**
- `pair_id` (str): The Investing.com pair ID
- `date_from` (str): Start date in "DDMMYYYY" format
- `date_to` (str): End date in "DDMMYYYY" format

**Returns:** pandas.DataFrame with columns: price, open, high, low, vol, perc_chg

```python
# Example
data = get_historical_prices("1075", "01012023", "31122023")
```

#### `get_multiple_historical_prices(pair_ids, date_from, date_to)`

Fetch historical data for multiple stocks concurrently.

**Parameters:**
- `pair_ids` (list): List of Investing.com pair IDs
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

### Market Info

#### `get_info(pair_id)`

Get comprehensive market overview data for any financial instrument.

**Parameters:**
- `pair_id` (str): The Investing.com pair ID

**Returns:** pandas.DataFrame with comprehensive market data including:

**Instrument Identity:**
- `symbol`, `name`, `full_name`, `exchange`, `currency`, `pair_type`, `is_crypto`

**Current Price Data:**
- `last`, `bid`, `ask`, `change`, `change_percent`, `open`, `high`, `low`, `previous_close`

**Volume:**
- `volume`, `avg_volume_3m`

**Performance:**
- `52w_high`, `52w_low`, `one_year_return`

**Technical & Sentiment:**
- `technical_summary` (Strong Buy/Sell), `bullish`, `bearish` (sentiment percentages)

**Stock-Specific (when available):**
- `eps`, `pe_ratio`, `market_cap`, `shares_outstanding`, `beta`, `revenue`, `dividend`, `dividend_yield`, `next_earnings_date`

**Index-Specific:**
- `number_of_components`

**Market Status:**
- `exchange_is_open`, `last_timestamp`

```python
# Get comprehensive info for Apple stock
apple_id = get_pair_id('AAPL')[0]
info = get_info(apple_id)

print(f"Symbol: {info['symbol'].iloc[0]}")
print(f"Price: {info['last'].iloc[0]}")
print(f"Change: {info['change_percent'].iloc[0]}%")
print(f"Market Cap: {info['market_cap'].iloc[0]}")
print(f"P/E Ratio: {info['pe_ratio'].iloc[0]}")
print(f"Technical Signal: {info['technical_summary'].iloc[0]}")
print(f"Sentiment - Bullish: {info['bullish'].iloc[0]}% / Bearish: {info['bearish'].iloc[0]}%")
```

### Technical Analysis

#### `get_technical_data(pair_id, tech_type='pivot_points', interval='daily')`

Get technical analysis data and indicators.

**Parameters:**
- `pair_id` (str): The Investing.com pair ID
- `tech_type` (str): Type of technical data:
  - `'pivot_points'`: Support and resistance levels (classic & fibonacci)
  - `'ti'`: Technical indicators
  - `'ma'`: Moving averages (simple & exponential)
  - `'summary'`: Technical summary with overall signal
- `interval` (str): Time interval:
  - `'5min'`, `'15min'`, `'30min'`: Intraday intervals
  - `'hourly'`, `'5hourly'`: Hourly intervals
  - `'daily'`, `'weekly'`, `'monthly'`: Long-term intervals

**Returns:** pandas.DataFrame with technical indicators

**Pivot Points Columns:** `level`, `classic`, `fibonacci`

**Moving Averages Columns:** `period`, `simple_ma`, `simple_signal`, `exponential_ma`, `exponential_signal`

**Technical Indicators Columns:** `indicator`, `value`, `signal`

**Summary Columns:** `type`, `signal`, `action`, `buy`, `sell`, `neutral`, `value`

```python
# Example - Daily pivot points
spy_id = get_pair_id('SPY')[0]
pivot_data = get_technical_data(spy_id, 'pivot_points', 'daily')
print(pivot_data)
#       level  classic  fibonacci
#          R3   709.80     688.57
#          R2   688.57     676.19
# Pivot Point   656.15     656.15

# Example - Weekly moving averages
weekly_ma = get_technical_data(spy_id, 'ma', 'weekly')

# Example - Technical summary
summary = get_technical_data(spy_id, 'summary', 'daily')
print(summary)
#                    type         signal     action      buy      sell     neutral   value
#                 Overall     Strong Buy strong_buy      NaN       NaN         NaN     NaN
#         Moving Averages     Strong Buy        NaN Buy (10) Sell (2)         NaN     NaN
#    Technical Indicators     Strong Buy        NaN  Buy (8)  Sell (2) Neutral (1)     NaN
#        ATR (Volatility) High Volatility        NaN      NaN       NaN         NaN  1.3011
```

## Complete Example

```python
from investgo import get_pair_id, get_historical_prices, get_holdings, get_info
import matplotlib.pyplot as plt

# Search for QQQ ETF
pair_ids = get_pair_id(['QQQ'])
qqq_id = pair_ids[0]

# Get market info
info = get_info(qqq_id)
print(f"\n{info['name'].iloc[0]} ({info['symbol'].iloc[0]})")
print(f"Price: {info['last'].iloc[0]} {info['change_percent'].iloc[0]}%")
print(f"Technical Signal: {info['technical_summary'].iloc[0]}")

# Get 1 year of historical data
historical_data = get_historical_prices(qqq_id, "01012023", "31122023")

# Get top holdings
holdings = get_holdings(qqq_id, "top_holdings")

# Plot price chart
historical_data['price'].plot(title='QQQ Price History')
plt.show()

# Display top 10 holdings
print("\nTop 10 Holdings:")
print(holdings.head(10))
```

## Error Handling

The library uses custom exceptions for better error handling:

```python
from investgo import get_pair_id, get_historical_prices
from investgo.exceptions import InvalidParameterError, NoDataFoundError, APIError

try:
    pair_id = get_pair_id('INVALID_TICKER')[0]
    data = get_historical_prices(pair_id, "01012023", "31122023")
except NoDataFoundError as e:
    print(f"No data found: {e}")
except InvalidParameterError as e:
    print(f"Invalid parameter: {e}")
except APIError as e:
    print(f"API error: {e}")
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

This library is for educational and research purposes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
