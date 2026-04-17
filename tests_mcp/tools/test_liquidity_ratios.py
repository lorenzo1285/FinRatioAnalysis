"""Unit tests for liquidity_ratios tool (T030)."""

import pytest
from unittest.mock import patch

from finratioanalysis_mcp.tools.liquidity_ratios import finratio_liquidity_ratios


def test_liquidity_ratios_happy_path(mock_liquidity_ratios_df):
    """Test successful liquidity_ratios call with mocked data."""
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        mock_instance.liquidity_ratios.return_value = mock_liquidity_ratios_df
        
        response = finratio_liquidity_ratios(ticker="AAPL", freq="yearly", response_format="json")
    
    # Assert response structure
    assert "data" in response
    assert isinstance(response["data"], list)
    assert len(response["data"]) > 0
    
    # Verify date field
    assert "date" in response["data"][0]
    
    # Verify expected columns from library_schema.json
    expected_cols = ["CurrentRatios", "QuickRatio", "CashRatio", "DIR", 
                     "TIE", "TIE_CB", "CAPEX_OpCash", "OpCashFlow"]
    for col in expected_cols:
        assert col in response["data"][0], f"Missing column: {col}"


def test_liquidity_ratios_markdown_format(mock_liquidity_ratios_df):
    """Test liquidity_ratios with markdown output."""
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        mock_instance.liquidity_ratios.return_value = mock_liquidity_ratios_df
        
        response = finratio_liquidity_ratios(ticker="AAPL", freq="yearly", response_format="markdown")
    
    assert "data" in response
    assert isinstance(response["data"], str)
    assert "|" in response["data"]  # Markdown table format
    
    # Verify table contains expected column headers
    assert "date" in response["data"]
    assert "CurrentRatios" in response["data"]
    assert "QuickRatio" in response["data"]


def test_liquidity_ratios_quarterly_freq(mock_liquidity_ratios_df):
    """Test liquidity_ratios with quarterly frequency."""
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        mock_instance.liquidity_ratios.return_value = mock_liquidity_ratios_df
        
        response = finratio_liquidity_ratios(ticker="MSFT", freq="quarterly", response_format="json")
    
    assert "data" in response
    assert isinstance(response["data"], list)
