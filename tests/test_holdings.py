"""
Unit tests for holdings and allocation module.
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from investgo.holdings import get_holdings, to_numeric, parse_holdings_data
from investgo.exceptions import InvalidParameterError


def test_to_numeric():
    df = pd.DataFrame({'a': ['1', '2.5', 'invalid']})
    df_clean = to_numeric(df, ['a'])
    assert pd.isna(df_clean['a'].iloc[2])
    assert df_clean['a'].iloc[0] == 1.0


def test_invalid_parameters():
    with pytest.raises(InvalidParameterError):
        get_holdings('')

    with pytest.raises(InvalidParameterError):
        get_holdings('12345', holdings_type='invalid')
