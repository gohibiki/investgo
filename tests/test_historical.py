"""
Unit tests for historical data module.
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from investgo.historical import generate_date_ranges, json_to_dataframe, get_historical_prices
from investgo.exceptions import InvalidParameterError


def test_generate_date_ranges():
    ranges = generate_date_ranges('01012023', '01032023', delta_days=30)
    assert len(ranges) >= 2
    assert ranges[0][0] == '01012023'


def test_generate_date_ranges_invalid_dates():
    with pytest.raises(InvalidParameterError):
        generate_date_ranges('invalid', '01012023')

    with pytest.raises(InvalidParameterError):
        generate_date_ranges('01012024', '01012023')


def test_get_historical_prices_invalid():
    with pytest.raises(InvalidParameterError):
        get_historical_prices('', '01012023', '02012023')

    with pytest.raises(InvalidParameterError):
        get_historical_prices('12345', 'invalid', '02012023')


def test_json_to_dataframe_empty():
    assert json_to_dataframe({}).empty
    assert json_to_dataframe({'data': []}).empty
