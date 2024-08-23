import cloudscraper
import pandas as pd
from datetime import datetime, timedelta
import concurrent.futures

def fetch_historical_prices(stock_id, date_from, date_to):
    scraper = cloudscraper.create_scraper()
    url = "https://aappapi.investing.com/get_screen.php"
    params = {
        "screen_ID": 63,
        "pair_ID": stock_id,
        "lang_ID": 1,
        "date_from": date_from,
        "date_to": date_to
    }
    headers = {"x-meta-ver": "14"}
    response = scraper.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response.json()

def json_to_dataframe(json_data):
    if 'data' in json_data and json_data['data']:
        screen_data = json_data['data'][0]['screen_data']['data']
        for item in screen_data:
            item["date"] = datetime.utcfromtimestamp(item["date"]).strftime('%d%m%Y')
            for key in ['price', 'open', 'high', 'low', 'vol', 'perc_chg']:
                if key in item and isinstance(item[key], str):
                    item[key] = item[key].replace(',', '').replace('K', '000').replace('%', '')
        df = pd.DataFrame(screen_data)
        if 'date' in df.columns:
            df.set_index('date', inplace=True)
            df.index = pd.to_datetime(df.index, format='%d%m%Y')
            df = df.sort_index(ascending=True)
            df.drop('color', axis=1, inplace=True, errors='ignore')
            return df.apply(pd.to_numeric, errors='coerce')
    return pd.DataFrame()

def generate_date_ranges(date_from, date_to, delta_days=365):
    start_date = datetime.strptime(date_from, "%d%m%Y")
    end_date = datetime.strptime(date_to, "%d%m%Y")
    delta = timedelta(days=delta_days)
    
    date_ranges = []
    while start_date < end_date:
        current_end_date = min(start_date + delta, end_date)
        date_ranges.append((start_date.strftime('%d%m%Y'), current_end_date.strftime('%d%m%Y')))
        start_date = current_end_date + timedelta(days=1)
    
    return date_ranges

def fetch_data_for_range(stock_id, date_range):
    date_from, date_to = date_range
    json_data = fetch_historical_prices(stock_id, date_from, date_to)
    return json_to_dataframe(json_data)

def get_historical_prices(stock_id, date_from, date_to):
    date_ranges = generate_date_ranges(date_from, date_to)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(fetch_data_for_range, stock_id, date_range) for date_range in date_ranges]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    valid_results = [df for df in results if not df.empty]
    if valid_results:
        valid_results.sort(key=lambda df: df.index.min())
        combined_df = pd.concat(valid_results)
        return combined_df
    else:
        return pd.DataFrame()

def get_multiple_historical_prices(stock_ids, date_from, date_to):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_historical_prices, stock_id, date_from, date_to) for stock_id in stock_ids]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    valid_results = [df for df in results if not df.empty]
    if valid_results:
        return pd.concat(valid_results, axis=1)
    else:
        return pd.DataFrame()
