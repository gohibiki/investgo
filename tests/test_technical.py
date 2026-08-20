"""
Unit tests for technical analysis module.
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from investgo.technical import get_technical_data, get_available_intervals, get_available_tech_types
from investgo.exceptions import InvalidParameterError


def test_get_available_intervals():
    intervals = get_available_intervals()
    assert 'daily' in intervals
    assert 'hourly' in intervals


def test_get_available_tech_types():
    types = get_available_tech_types()
    assert 'pivot_points' in types
    assert 'ti' in types
    assert 'ma' in types
    assert 'summary' in types


def test_invalid_parameters():
    with pytest.raises(InvalidParameterError):
        get_technical_data('12345', tech_type='invalid')

    with pytest.raises(InvalidParameterError):
        get_technical_data('12345', interval='invalid')
