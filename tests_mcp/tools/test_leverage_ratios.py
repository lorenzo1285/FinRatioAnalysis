"""Unit tests for leverage_ratios tool (T029)."""

import pytest
from unittest.mock import patch

from finratioanalysis_mcp.tools.leverage_ratios import finratio_leverage_ratios


def test_leverage_ratios_happy_path(mock_leverage_ratios_df):
    """Test successful leverage_ratios call with mocked data."""
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        mock_instance.leverage_ratios.return_value = mock_leverage_ratios_df
        
        response = finratio_leverage_ratios(ticker="AAPL", freq="yearly", response_format="json")
    
    # Assert response structure
    assert "data" in response
    assert isinstance(response["data"], list)
    assert len(response["data"]) > 0
    
    # Verify date field
    assert "date" in response["data"][0]
    
    # Verify expected columns from library_schema.json
    expected_cols = ["DebtEquityRatio", "EquityRatio", "DebtRatio"]
    for col in expected_cols:
        assert col in response["data"][0], f"Missing column: {col}"


def test_leverage_ratios_markdown_format(mock_leverage_ratios_df):
    """Test leverage_ratios with markdown output."""
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        mock_instance.leverage_ratios.return_value = mock_leverage_ratios_df
        
        response = finratio_leverage_ratios(ticker="AAPL", freq="yearly", response_format="markdown")
    
    assert "data" in response
    assert isinstance(response["data"], str)
    assert "|" in response["data"]  # Markdown table format
    
    # Verify table contains expected column headers
    assert "date" in response["data"]
    assert "DebtEquityRatio" in response["data"]
    assert "EquityRatio" in response["data"]


def test_leverage_ratios_quarterly_freq(mock_leverage_ratios_df):
    """Test leverage_ratios with quarterly frequency."""
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        mock_instance.leverage_ratios.return_value = mock_leverage_ratios_df
        
        response = finratio_leverage_ratios(ticker="MSFT", freq="quarterly", response_format="json")
    
    assert "data" in response
    assert isinstance(response["data"], list)
