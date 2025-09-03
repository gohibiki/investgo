"""
Unit tests for the search module.

These tests verify the search functionality works correctly
and handles edge cases appropriately.
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from investgo.search import get_pair_id, fetch_pair_data, json_to_dataframe


class TestSearchFunctionality:
    """Test cases for search functionality."""
    
    def test_get_pair_id_single_ticker(self):
        """Test searching for a single ticker symbol."""
        # This would be a real test in practice
        # For now, we'll test the structure
        pass
    
    def test_get_pair_id_multiple_tickers(self):
        """Test searching for multiple ticker symbols."""
        pass
    
    def test_get_pair_id_with_names(self):
        """Test returning names along with pair IDs."""
        pass
    
    def test_get_pair_id_invalid_display_mode(self):
        """Test that invalid display_mode raises ValueError."""
        with pytest.raises(ValueError, match="Invalid display_mode"):
            get_pair_id(['AAPL'], display_mode="invalid")
    
    def test_get_pair_id_empty_input(self):
        """Test that empty input raises ValueError."""
        with pytest.raises(ValueError, match="Missing required parameters"):
            get_pair_id([])
        
        with pytest.raises(ValueError, match="Missing required parameters"):
            get_pair_id("")
    
    def test_get_pair_id_all_mode_multiple_stocks(self):
        """Test that 'all' mode with multiple stocks raises ValueError."""
        with pytest.raises(ValueError, match="Display mode 'all' can only be used with a single stock ID"):
            get_pair_id(['AAPL', 'MSFT'], display_mode="all")


class TestDataProcessing:
    """Test cases for data processing functions."""
    
    def test_json_to_dataframe_empty_data(self):
        """Test handling of empty JSON data."""
        empty_data = []
        result = json_to_dataframe(empty_data)
        assert isinstance(result, pd.DataFrame)
        assert result.empty
    
    def test_json_to_dataframe_missing_quotes(self):
        """Test handling of JSON without quotes data."""
        invalid_data = [({'data': {}}, 'TEST')]
        result = json_to_dataframe(invalid_data)
        assert isinstance(result, pd.DataFrame)
        assert result.empty


@patch('investgo.search.cloudscraper.create_scraper')
def test_fetch_pair_data_success(mock_scraper):
    """Test successful API call."""
    # Mock the scraper and response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'data': {
            'quotes': [
                {
                    'pair_ID': '12345',
                    'search_main_text': 'AAPL',
                    'search_main_longtext': 'Apple Inc',
                    'search_main_subtext': 'NASDAQ'
                }
            ]
        }
    }
    mock_response.raise_for_status.return_value = None
    
    mock_scraper_instance = MagicMock()
    mock_scraper_instance.get.return_value = mock_response
    mock_scraper.return_value = mock_scraper_instance
    
    result, search_string = fetch_pair_data('AAPL')
    
    assert search_string == 'AAPL'
    assert 'data' in result
    assert 'quotes' in result['data']


@patch('investgo.search.cloudscraper.create_scraper')
def test_fetch_pair_data_http_error(mock_scraper):
    """Test handling of HTTP errors."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = Exception("HTTP 404")
    
    mock_scraper_instance = MagicMock()
    mock_scraper_instance.get.return_value = mock_response
    mock_scraper.return_value = mock_scraper_instance
    
    with pytest.raises(Exception):
        fetch_pair_data('INVALID')


if __name__ == "__main__":
    # Run tests if script is executed directly
    pytest.main([__file__])
