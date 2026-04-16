"""Unit tests for ccc tool (T031)."""

import pytest
from unittest.mock import patch

from finratioanalysis_mcp.tools.ccc import finratio_ccc


def test_ccc_happy_path(mock_ccc_df):
    """Test successful ccc call with mocked data."""
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        mock_instance.ccc.return_value = mock_ccc_df
        
        response = finratio_ccc(ticker="AAPL", freq="yearly", response_format="json")
    
    # Assert response structure
    assert "data" in response
    assert isinstance(response["data"], list)
    assert len(response["data"]) > 0
    
    # Verify date field
    assert "date" in response["data"][0]
    
    # Verify expected columns from library_schema.json
    expected_cols = ["DIO", "DSO", "DPO", "CCC"]
    for col in expected_cols:
        assert col in response["data"][0], f"Missing column: {col}"


def test_ccc_markdown_format(mock_ccc_df):
    """Test ccc with markdown output."""
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        mock_instance.ccc.return_value = mock_ccc_df
        
        response = finratio_ccc(ticker="AAPL", freq="yearly", response_format="markdown")
    
    assert "data" in response
    assert isinstance(response["data"], str)
    assert "|" in response["data"]  # Markdown table format
    
    # Verify table contains expected column headers
    assert "date" in response["data"]
    assert "DIO" in response["data"]
    assert "CCC" in response["data"]


def test_ccc_quarterly_freq(mock_ccc_df):
    """Test ccc with quarterly frequency."""
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        mock_instance.ccc.return_value = mock_ccc_df
        
        response = finratio_ccc(ticker="MSFT", freq="quarterly", response_format="json")
    
    assert "data" in response
    assert isinstance(response["data"], list)
