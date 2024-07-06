from flask import Flask, jsonify, request
import cloudscraper
import pandas as pd
import datetime
import json

app = Flask(__name__)

def get_historical_prices(stock_id, date_from, date_to):
    scraper = cloudscraper.create_scraper()
    
    url = "https://aappapi.investing.com/get_screen.php"
    params = {
        "screen_ID": 63,
        "include_pair_attr": "true",
        "v2": 1,
        "pair_ID": stock_id,
        "lang_ID": 1,
        "time_utc_offset": 28800,
        "skinID": 2,
        "onlineCacheSeconds": 5,
        "sessionsCounter": 1,
        "date_from": date_from,
        "date_to": date_to
    }

    headers = {
        "x-app-ver": "1534",
        "x-client-version": "6.28",
        "ccode": "MY",
        "ccode_time": "1720114009",
        "x-meta-ver": "14",
        "x-app-instance-id": "c164d98779d8d53154fe00697115a8d6",
        "x-session-id": "1720114002",
        "x-udid": "5a570d8dac84c8fa",
        "x-accept-language": "en-US",
        "user-agent": "Android Version/1534",
        "content-type": "application/json",
        "x-os": "Android",
        "apf_id": "1720114004259-4823729932348912896",
        "apf_src": "org",
        "rc-data": "eyJydHFfZW5hYmxlZCI6ZmFsc2V9",
        "accept-encoding": "gzip"
    }

    response = scraper.get(url, params=params, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def json_to_dataframe(json_data):
    if 'data' in json_data:
        screen_data = json_data['data'][0]['screen_data']['data']
        # Convert the Unix timestamps to datetime
        for item in screen_data:
            item["date"] = datetime.datetime.utcfromtimestamp(item["date"]).strftime('%Y-%m-%d')
        # Create the DataFrame
        df = pd.DataFrame(screen_data)
        # Reorder the columns as specified
        df = df[["date", "price", "open", "high", "low", "perc_chg"]]
        return df
    return None

@app.route('/api/historical_prices', methods=['GET'])
def historical_prices():
    stock_id = request.args.get('stock_id')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    if not stock_id or not date_from or not date_to:
        return jsonify({"error": "Missing required parameters"}), 400
    
    json_data = get_historical_prices(stock_id, date_from, date_to)
    if json_data:
        df = json_to_dataframe(json_data)
        if df is not None:
            return df.to_json(orient='records')
        else:
            return jsonify({"error": "Failed to convert data to DataFrame"}), 500
    else:
        return jsonify({"error": "Failed to fetch data"}), 500

if __name__ == '__main__':
    app.run(debug=True)
