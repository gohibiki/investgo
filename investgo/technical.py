import cloudscraper
import pandas as pd

def fetch_technical_data():
    scraper = cloudscraper.create_scraper()
    
    url = "https://aappapi.investing.com/get_screen.php"
    params = {
        "screen_ID": 25,
        "pair_ID": '651',
        "lang_ID": 1,
    }
    
    headers = {
        "x-meta-ver": "14",
    }
    
    response = scraper.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response.json()

def parse_technical_data(data, tech_type):
    dfs = []
    for item in data.get('data', []):
        screen_data = item.get('screen_data', {})
        for tech_data in screen_data.get('technical_data', []):
            pivot_points = tech_data.get(tech_type, [])
            
            if tech_type == 'ti':
                df = pd.DataFrame(pivot_points).iloc[:, [0, 1]]
            elif tech_type == 'ma':
                df = pd.DataFrame(pivot_points).iloc[:, [0, 1, 2, 6, 7]]
            elif tech_type == 'pivot_points':
                df = pd.DataFrame(pivot_points).iloc[:, [0, 1, 5]]
            else:
                df = pd.DataFrame(pivot_points)
            
            dfs.append(df)
    return dfs

def get_technical_data(tech_type='pivot_points', interval='5min'):
    data = fetch_technical_data()
    dfs = parse_technical_data(data, tech_type)
    
    interval_map = {
        '5min': 0,
        '15min': 1,
        'hourly': 2,
        'daily': 3
    }
    
    return dfs[interval_map.get(interval, 0)]