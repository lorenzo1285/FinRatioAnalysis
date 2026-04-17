"""Unit tests for efficiency_ratios tool (T028)."""

import pytest
from unittest.mock import patch

from finratioanalysis_mcp.tools.efficiency_ratios import finratio_efficiency_ratios


def test_efficiency_ratios_happy_path(mock_efficiency_ratios_df):
    """Test successful efficiency_ratios call with mocked data."""
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        mock_instance.efficiency_ratios.return_value = mock_efficiency_ratios_df
        
        response = finratio_efficiency_ratios(ticker="AAPL", freq="yearly", response_format="json")
    
    # Assert response structure
    assert "data" in response
    assert isinstance(response["data"], list)
    assert len(response["data"]) > 0
    
    # Verify date field
    assert "date" in response["data"][0]
    
    # Verify expected columns from library_schema.json
    expected_cols = ["AssetTurnover", "ReceivableTurnover", "InventoryTurnover", 
                     "FixedAssetTurnover", "FCF_Margin", "ReinvestmentRate"]
    for col in expected_cols:
        assert col in response["data"][0], f"Missing column: {col}"


def test_efficiency_ratios_markdown_format(mock_efficiency_ratios_df):
    """Test efficiency_ratios with markdown output."""
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        mock_instance.efficiency_ratios.return_value = mock_efficiency_ratios_df
        
        response = finratio_efficiency_ratios(ticker="AAPL", freq="yearly", response_format="markdown")
    
    assert "data" in response
    assert isinstance(response["data"], str)
    assert "|" in response["data"]  # Markdown table format
    
    # Verify table contains expected column headers
    assert "date" in response["data"]
    assert "AssetTurnover" in response["data"]
    assert "FCF_Margin" in response["data"]


def test_efficiency_ratios_quarterly_freq(mock_efficiency_ratios_df):
    """Test efficiency_ratios with quarterly frequency."""
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        mock_instance.efficiency_ratios.return_value = mock_efficiency_ratios_df
        
        response = finratio_efficiency_ratios(ticker="MSFT", freq="quarterly", response_format="json")
    
    assert "data" in response
    assert isinstance(response["data"], list)
