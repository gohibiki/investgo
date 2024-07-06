import requests
import pandas as pd

BASE_URL = "https://your-render-app-url/api/historical_prices"

def get_historical_prices(stock_id, date_from, date_to):
    params = {
        'stock_id': stock_id,
        'date_from': date_from,
        'date_to': date_to
    }
    response = requests.get(BASE_URL, params=params)
    
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        response.raise_for_status()