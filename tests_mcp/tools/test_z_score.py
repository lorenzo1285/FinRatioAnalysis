"""Unit tests for z_score tool (T034)."""

import pytest
from unittest.mock import patch

from finratioanalysis_mcp.tools.z_score import finratio_z_score


def test_z_score_happy_path(mock_z_score_df):
    """Test successful z_score call with mocked data."""
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        mock_instance.z_score.return_value = mock_z_score_df
        
        response = finratio_z_score(ticker="AAPL", freq="yearly", response_format="json")
    
    # Assert response structure
    assert "data" in response
    assert isinstance(response["data"], dict)
    
    # Verify Symbol field
    assert "Symbol" in response["data"]
    
    # Verify expected columns from library_schema.json
    expected_cols = ["Symbol", "Z Score", "Zone"]
    for col in expected_cols:
        assert col in response["data"], f"Missing column: {col}"


def test_z_score_markdown_format(mock_z_score_df):
    """Test z_score with markdown output."""
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        mock_instance.z_score.return_value = mock_z_score_df
        
        response = finratio_z_score(ticker="AAPL", freq="yearly", response_format="markdown")
    
    assert "data" in response
    assert isinstance(response["data"], str)
    # Markdown key-value format
    assert "Symbol" in response["data"]
    assert "Z Score" in response["data"]
    assert "Zone" in response["data"]


def test_z_score_quarterly_freq(mock_z_score_df):
    """Test z_score with quarterly frequency."""
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        mock_instance.z_score.return_value = mock_z_score_df
        
        response = finratio_z_score(ticker="MSFT", freq="quarterly", response_format="json")
    
    assert "data" in response
    assert isinstance(response["data"], dict)
