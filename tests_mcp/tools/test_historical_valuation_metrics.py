"""Unit tests for historical_valuation_metrics tool (T032)."""

import pytest
from unittest.mock import patch

from finratioanalysis_mcp.tools.historical_valuation_metrics import finratio_historical_valuation_metrics


def test_historical_valuation_metrics_happy_path(mock_historical_valuation_metrics_df):
    """Test successful historical_valuation_metrics call with mocked data."""
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        mock_instance.historical_valuation_metrics.return_value = mock_historical_valuation_metrics_df
        
        response = finratio_historical_valuation_metrics(ticker="AAPL", freq="yearly", response_format="json")
    
    # Assert response structure
    assert "data" in response
    assert isinstance(response["data"], list)
    assert len(response["data"]) > 0
    
    # Verify date field
    assert "date" in response["data"][0]
    
    # Verify expected columns from library_schema.json
    expected_cols = ["Market_Cap", "PE_Ratio", "EV_EBITDA", "FCF_Yield"]
    for col in expected_cols:
        assert col in response["data"][0], f"Missing column: {col}"


def test_historical_valuation_metrics_markdown_format(mock_historical_valuation_metrics_df):
    """Test historical_valuation_metrics with markdown output."""
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        mock_instance.historical_valuation_metrics.return_value = mock_historical_valuation_metrics_df
        
        response = finratio_historical_valuation_metrics(ticker="AAPL", freq="yearly", response_format="markdown")
    
    assert "data" in response
    assert isinstance(response["data"], str)
    assert "|" in response["data"]  # Markdown table format
    
    # Verify table contains expected column headers
    assert "date" in response["data"]
    assert "Market_Cap" in response["data"]
    assert "PE_Ratio" in response["data"]


def test_historical_valuation_metrics_quarterly_freq(mock_historical_valuation_metrics_df):
    """Test historical_valuation_metrics with quarterly frequency."""
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        mock_instance.historical_valuation_metrics.return_value = mock_historical_valuation_metrics_df
        
        response = finratio_historical_valuation_metrics(ticker="MSFT", freq="quarterly", response_format="json")
    
    assert "data" in response
    assert isinstance(response["data"], list)
