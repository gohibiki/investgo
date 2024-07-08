import cloudscraper
import pandas as pd
import datetime
import json

def get_pair_id(pair_id):
  scraper = cloudscraper.create_scraper()

  url = "https://aappapi.investing.com/search_by_type.php"
  params = {
    "section": "quotes",
    "string": pair_id,
    "lang_ID": 1,
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
    quotes = json_data['data']['quotes']
    df_quotes = pd.DataFrame(quotes)
    df_quotes = df_quotes.iloc[:, [0, 1, 2, 4]]
    df_quotes.rename(columns={
        'search_main_text': 'Ticker',
        'search_main_longtext': 'Description',
        'search_main_subtext': 'Exchange'
    })
    pair_ID = df_quotes.iloc[0]['pair_ID']
    return pair_ID
  return None

def pair_id(stock_id):
  if not pair_id:
    return jsonify({"error": "Missing required parameters"}), 400
  
  json_data = get_pair_id(stock_id)
  if json_data:
    df = json_to_dataframe(json_data)
    if df is not None:
      return df
    else:
      return jsonify({"error": "Failed to convert data to DataFrame"}), 400
  else:
    return jsonify({"error": "Failed to fetch data"}), 404