"""Unit tests for wacc tool (T036)."""

import pytest
from unittest.mock import patch

from finratioanalysis_mcp.tools.wacc import finratio_wacc


def test_wacc_happy_path(mock_wacc_df):
    """Test successful wacc call with mocked data."""
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        mock_instance.wacc.return_value = mock_wacc_df
        
        response = finratio_wacc(ticker="AAPL", freq="yearly", response_format="json")
    
    # Assert response structure
    assert "data" in response
    assert isinstance(response["data"], dict)
    
    # Verify Symbol field
    assert "Symbol" in response["data"]
    
    # Verify expected columns from library_schema.json
    expected_cols = ["Symbol", "WACC"]
    for col in expected_cols:
        assert col in response["data"], f"Missing column: {col}"


def test_wacc_markdown_format(mock_wacc_df):
    """Test wacc with markdown output."""
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        mock_instance.wacc.return_value = mock_wacc_df
        
        response = finratio_wacc(ticker="AAPL", freq="yearly", response_format="markdown")
    
    assert "data" in response
    assert isinstance(response["data"], str)
    # Markdown key-value format
    assert "Symbol" in response["data"]
    assert "WACC" in response["data"]


def test_wacc_quarterly_freq(mock_wacc_df):
    """Test wacc with quarterly frequency."""
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        mock_instance.wacc.return_value = mock_wacc_df
        
        response = finratio_wacc(ticker="MSFT", freq="quarterly", response_format="json")
    
    assert "data" in response
    assert isinstance(response["data"], dict)
