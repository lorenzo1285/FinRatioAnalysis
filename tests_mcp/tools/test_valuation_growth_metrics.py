"""Unit tests for valuation_growth_metrics tool (T033).

NOTE: This tool has a Symbol injection shim (Option B) because the library's
valuation_growth_metrics() does not return a Symbol column. The tool manually
injects it as the first field in the response.
"""

import pytest
from unittest.mock import patch

from finratioanalysis_mcp.tools.valuation_growth_metrics import finratio_valuation_growth_metrics


def test_valuation_growth_metrics_happy_path(mock_valuation_growth_metrics_df):
    """Test successful valuation_growth_metrics call with mocked data."""
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        mock_instance.valuation_growth_metrics.return_value = mock_valuation_growth_metrics_df
        
        response = finratio_valuation_growth_metrics(ticker="AAPL", freq="yearly", response_format="json")
    
    # Assert response structure
    assert "data" in response
    assert isinstance(response["data"], dict)
    
    # Verify Symbol field is present (injected by the tool, not in the mock)
    assert "Symbol" in response["data"]
    assert response["data"]["Symbol"] == "AAPL"
    
    # Verify expected columns from library_schema.json
    expected_cols = ["dividend_yield", "payout_ratio", "pe_ratio", "forward_pe", 
                     "ps_ratio", "beta", "ev_ebitda", "fcf_yield", 
                     "revenue_cagr_3y", "net_income_cagr_3y"]
    for col in expected_cols:
        assert col in response["data"], f"Missing column: {col}"


def test_valuation_growth_metrics_markdown_format(mock_valuation_growth_metrics_df):
    """Test valuation_growth_metrics with markdown output."""
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        mock_instance.valuation_growth_metrics.return_value = mock_valuation_growth_metrics_df
        
        response = finratio_valuation_growth_metrics(ticker="AAPL", freq="yearly", response_format="markdown")
    
    assert "data" in response
    assert isinstance(response["data"], str)
    # Markdown key-value format (not table)
    assert "Symbol" in response["data"]
    assert "pe_ratio" in response["data"]
    assert "beta" in response["data"]


def test_valuation_growth_metrics_symbol_injection(mock_valuation_growth_metrics_df):
    """Test that Symbol is injected correctly even when not in library response."""
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        mock_instance.valuation_growth_metrics.return_value = mock_valuation_growth_metrics_df
        
        response = finratio_valuation_growth_metrics(ticker="MSFT", freq="yearly", response_format="json")
    
    # Symbol should match the ticker passed to the tool, not from the DataFrame
    assert response["data"]["Symbol"] == "MSFT"
