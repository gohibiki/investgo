import cloudscraper
import pandas as pd
import datetime
import json

def get_historical_prices(stock_id, date_from, date_to):
  scraper = cloudscraper.create_scraper()

  url = "https://aappapi.investing.com/get_screen.php"
  params = {
    "screen_ID": 63,
    "pair_ID": stock_id,
    "lang_ID": 1,
    "date_from": date_from,
    "date_to": date_to
  }

  headers = {
    "x-meta-ver": "14",
  }

  response = scraper.get(url, params=params, headers=headers)
  if response.status_code == 200:
    return response.json()
  else:
    return None

def json_to_dataframe(json_data):
  if 'data' in json_data:
    screen_data = json_data['data'][0]['screen_data']['data']
    for item in screen_data:
      item["date"] = datetime.datetime.utcfromtimestamp(item["date"]).strftime('%Y-%m-%d')
    df = pd.DataFrame(screen_data)
    df['date'] = pd.to_datetime(df['date'])
    df['date'] = df['date'].dt.strftime('%d%m%Y')
    df=df.set_index('date').drop('color',axis=1)
    df.index.name = None
    return df
  return None

def historical_prices(stock_id, date_from, date_to):
  if not stock_id or not date_from or not date_to:
    return jsonify({"error": "Missing required parameters"}), 400
  
  json_data = get_historical_prices(stock_id, date_from, date_to)
  if json_data:
    df = json_to_dataframe(json_data)
    if df is not None:
      return df
    else:
      return jsonify({"error": "Failed to convert data to DataFrame"}), 400
  else:
    return jsonify({"error": "Failed to fetch data"}), 404