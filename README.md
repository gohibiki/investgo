# InvestGo

InvestGo is a Python library that allows you to fetch historical stock prices from Investing.com using a simple API. This package uses Flask for the web server and cloudscraper to handle web scraping.

## Features

- Fetch historical stock prices for a given stock ID and date range
- Convert JSON responses to pandas DataFrame for easy manipulation
- Simple API endpoint to retrieve historical data

## Installation

You can install InvestGo directly from PyPI:

```sh
pip install investgo
```
## Usage

```sh
from your_project.historical_prices import historical_prices
```
# Example parameters
```sh
stock_id = 1039381
date_from = "07072021"
date_to = "07052024"
```
# Fetch historical data
```sh
data = historical_prices(stock_id, date_from, date_to)
```
