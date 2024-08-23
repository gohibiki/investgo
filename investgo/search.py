import cloudscraper
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_pair_data(search_string):
    scraper = cloudscraper.create_scraper()
    url = "https://aappapi.investing.com/search_by_type.php"
    params = {"section": "quotes", "string": search_string, "lang_ID": 1,"include_pair_attr": "true"}
    headers = {"x-meta-ver": "14"}

    response = scraper.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response.json(), search_string

def json_to_dataframe(json_data_list):
    df_list = []
    for json_data, search_string in json_data_list:
        if "data" in json_data and "quotes" in json_data["data"]:
            quotes = json_data["data"]["quotes"]
            df_quotes = pd.DataFrame(quotes)
            try:
                df_quotes = df_quotes.loc[:, ["pair_ID", "search_main_text", "search_main_longtext", "search_main_subtext"]]
                df_quotes.rename(
                    columns={
                        "pair_ID": "pair_id",
                        "search_main_text": "Ticker",
                        "search_main_longtext": "Description",
                        "search_main_subtext": "Exchange",
                    },
                    inplace=True,
                )
                df_quotes['search_string'] = search_string
                df_list.append(df_quotes)
            except KeyError as e:
                print(f"KeyError: {e} in search string: {search_string}")
        else:
            print(f"Missing 'quotes' in 'data' for search string: {search_string}")
    if df_list:
        return pd.concat(df_list, ignore_index=True)
    return pd.DataFrame()

def get_pair_id(stock_ids, display_mode="first", name="no"):
    if not stock_ids:
        raise ValueError("Missing required parameters")

    if isinstance(stock_ids, str):
        stock_ids = [stock_ids]

    with ThreadPoolExecutor() as executor:
        future_to_search = {executor.submit(fetch_pair_data, stock_id): stock_id for stock_id in stock_ids}
        results = []
        for future in as_completed(future_to_search):
            try:
                result = future.result()
                results.append(result)
            except Exception as exc:
                print(f'Error fetching data for {future_to_search[future]}: {exc}')
    
    df = json_to_dataframe(results)

    if df.empty:
        raise ValueError("Failed to convert data to DataFrame")

    if display_mode == "all":
        if len(stock_ids) > 1:
            raise ValueError("Display mode 'all' can only be used with a single stock ID.")
        return df
    elif display_mode == "first" and name == 'yes':
        return df.groupby('search_string')['pair_id'].first().tolist(), df.groupby('search_string')['Description'].first().tolist()
    elif display_mode == "first" :
        return df.groupby('search_string')['pair_id'].first().tolist()
    else:
        raise ValueError("Invalid display_mode. Choose 'first' or 'all'.")