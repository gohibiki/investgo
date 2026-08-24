"""
Unit tests for the info module.
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from investgo.info import get_info, fetch_info_data, _extract_from_overview_table
from investgo.exceptions import APIError


def test_extract_from_overview_table():
    overview_table = [
        {'key': 'Market Cap', 'val': '2.5T'},
        {'key': 'Shares Outstanding', 'val': '15.5B'}
    ]
    assert _extract_from_overview_table(overview_table, 'Shares Outstanding') == '15.5B'
    assert _extract_from_overview_table(overview_table, 'NonExistent') is None
    assert _extract_from_overview_table([], 'Shares Outstanding') is None


@patch('investgo.info.get_scraper')
def test_fetch_info_data_success(mock_get_scraper):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'data': [
            {
                'screen_data': {
                    'pairs_data': [{
                        'last': 150.0,
                        'change_val': 1.5,
                        'change_percent_val': '1.01%'
                    }],
                    'pairs_attr': [{
                        'pair_symbol': 'AAPL',
                        'pair_name': 'Apple Inc'
                    }]
                }
            }
        ]
    }
    mock_response.raise_for_status.return_value = None

    mock_scraper = MagicMock()
    mock_scraper.get.return_value = mock_response
    mock_get_scraper.return_value = mock_scraper

    data = fetch_info_data('985439')
    assert 'data' in data
    assert len(data['data']) > 0


@patch('investgo.info.get_scraper')
def test_fetch_info_data_failure(mock_get_scraper):
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = Exception("HTTP 500")

    mock_scraper = MagicMock()
    mock_scraper.get.return_value = mock_response
    mock_get_scraper.return_value = mock_scraper

    with pytest.raises(APIError, match="Failed to fetch info data for pair_id"):
        fetch_info_data('985439')


@patch('investgo.info.fetch_info_data')
def test_get_info_success(mock_fetch):
    mock_fetch.return_value = {
        'data': [
            {
                'screen_data': {
                    'pairs_data': [{
                        'pair_type_section': 'Equities',
                        'isCrypto': False,
                        'last': 150.0,
                        'bid': 149.9,
                        'ask': 150.1,
                        'change_val': 1.5,
                        'change_percent_val': '1.01%',
                        'open': 149.0,
                        'high': 151.0,
                        'low': 148.5,
                        'last_close_value': 148.5,
                        'volume': 50000000,
                        'avg_volume': 45000000,
                        'a52_week_high': 180.0,
                        'a52_week_low': 120.0,
                        'one_year_return': '25%',
                        'technical_summary_text': 'Strong Buy',
                        'sentiments': {'bullish': 75, 'bearish': 25},
                        'exchange_is_open': True,
                        'last_timestamp': 1600000000,
                        'eq_eps': 6.0,
                        'eq_pe_ratio': 25.0,
                        'eq_market_cap': '2.5T',
                        'overview_table': [{'key': 'Shares Outstanding', 'val': '15.5B'}],
                        'eq_beta': 1.2,
                        'eq_revenue': '380B',
                        'eq_dividend': '0.96',
                        'eq_dividend_yield': '0.64%',
                        'next_earnings_date': '2026-10-30',
                        'number_of_components': None,
                    }],
                    'pairs_attr': [{
                        'pair_symbol': 'AAPL',
                        'pair_name': 'Apple Inc',
                        'pair_name_base': 'Apple Inc.',
                        'exchange_name': 'NASDAQ',
                        'currency_in': 'USD'
                    }]
                }
            }
        ]
    }

    df = get_info('985439')
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert df['symbol'].iloc[0] == 'AAPL'
    assert df['last'].iloc[0] == 150.0
    assert df['shares_outstanding'].iloc[0] == '15.5B'


@patch('investgo.info.fetch_info_data')
def test_get_info_empty_pairs_data(mock_fetch):
    mock_fetch.return_value = {
        'data': [
            {
                'screen_data': {
                    'pairs_data': [],
                    'pairs_attr': []
                }
            }
        ]
    }

    df = get_info('985439')
    assert isinstance(df, pd.DataFrame)
    assert df.empty
