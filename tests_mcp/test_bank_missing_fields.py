"""T041: Test NaN handling for bank stocks with missing fields.

Verifies that when a bank ticker yields NaN in GrossProfit-derived columns
(GrossMargin, etc.), the response contains null values (not errors) per
constitution Principle IV and FR-004.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch

from finratioanalysis_mcp.tools.return_ratios import finratio_return_ratios


def test_bank_missing_gross_profit_fields():
    """Test that NaN values for bank stocks are returned as null, not errors."""
    # Create a DataFrame with some NaN values (simulating bank with no GrossMargin)
    dates = pd.to_datetime(['2023-01-01', '2024-01-01'])
    mock_df = pd.DataFrame({
        'ROE': [0.12, 0.15],
        'ROA': [0.08, 0.09],
        'ROCE': [0.10, 0.11],
        'ROIC': [0.09, 0.10],
        'GrossMargin': [np.nan, np.nan],  # Banks don't have gross profit
        'OperatingMargin': [0.25, 0.28],
        'NetProfit': [0.15, 0.18],
    }, index=dates)
    
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        mock_instance.return_ratios.return_value = mock_df
        
        response = finratio_return_ratios(ticker="JPM", freq="yearly", response_format="json")
    
    # Should return data, not an error
    assert "data" in response, "Should return data despite NaN values"
    assert "code" not in response, "Should not be an error response"
    
    data = response["data"]
    assert isinstance(data, list)
    assert len(data) == 2
    
    # GrossMargin should be null (None in Python, null in JSON)
    assert data[0]["GrossMargin"] is None, "NaN should be converted to null"
    assert data[1]["GrossMargin"] is None, "NaN should be converted to null"
    
    # Other fields should have valid values
    assert data[0]["ROE"] == pytest.approx(0.12)
    assert data[0]["OperatingMargin"] == pytest.approx(0.25)
    assert data[1]["NetProfit"] == pytest.approx(0.18)


def test_partial_nan_fields_snapshot():
    """Test that snapshot tools also handle partial NaN values correctly."""
    from finratioanalysis_mcp.tools.z_score import finratio_z_score
    
    # Create a snapshot DataFrame with one NaN field
    mock_df = pd.DataFrame({
        'Symbol': ['JPM'],
        'Z Score': [np.nan],  # Might not be computable for some banks
        'Zone': ['Unknown'],
    })
    
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        mock_instance.z_score.return_value = mock_df
        
        response = finratio_z_score(ticker="JPM", freq="yearly", response_format="json")
    
    # Should return data with null for the NaN field
    assert "data" in response
    assert response["data"]["Symbol"] == "JPM"
    assert response["data"]["Z Score"] is None
    assert response["data"]["Zone"] == "Unknown"


def test_all_nan_row_still_included():
    """Test that rows with all NaN metrics (except date) are still included."""
    dates = pd.to_datetime(['2023-01-01'])
    mock_df = pd.DataFrame({
        'ROE': [np.nan],
        'ROA': [np.nan],
        'ROCE': [np.nan],
        'ROIC': [np.nan],
        'GrossMargin': [np.nan],
        'OperatingMargin': [np.nan],
        'NetProfit': [np.nan],
    }, index=dates)
    
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        mock_instance.return_ratios.return_value = mock_df
        
        response = finratio_return_ratios(ticker="TEST", freq="yearly", response_format="json")
    
    # Row should be included with all null values
    assert "data" in response
    assert len(response["data"]) == 1
    assert response["data"][0]["date"] == "2023-01-01"
    assert all(v is None for k, v in response["data"][0].items() if k != "date")


def test_nan_in_markdown_format():
    """Test that NaN values are rendered as 'null' in markdown format."""
    dates = pd.to_datetime(['2023-01-01'])
    mock_df = pd.DataFrame({
        'ROE': [0.15],
        'ROA': [np.nan],
        'ROCE': [0.10],
        'ROIC': [np.nan],
        'GrossMargin': [np.nan],
        'OperatingMargin': [0.25],
        'NetProfit': [0.18],
    }, index=dates)
    
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        mock_instance.return_ratios.return_value = mock_df
        
        response = finratio_return_ratios(ticker="JPM", freq="yearly", response_format="markdown")
    
    assert "data" in response
    markdown = response["data"]
    
    # Should contain the literal string 'null' for NaN values
    assert "null" in markdown, "NaN should be rendered as 'null' in markdown"
    assert "0.15" in markdown or "0.1500" in markdown, "Valid values should be present"
