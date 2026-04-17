"""Unit tests for capm tool (T035)."""

import pytest
from unittest.mock import patch

from finratioanalysis_mcp.tools.capm import finratio_capm


def test_capm_happy_path(mock_capm_df):
    """Test successful capm call with mocked data."""
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        mock_instance.capm.return_value = mock_capm_df

        response = finratio_capm(ticker="AAPL", freq="yearly", response_format="json")

    # Assert response structure
    assert "data" in response
    assert isinstance(response["data"], dict)

    # Verify Symbol field
    assert "Symbol" in response["data"]

    # Verify expected columns from library_schema.json
    expected_cols = ["Symbol", "CAPM", "Sharpe"]
    for col in expected_cols:
        assert col in response["data"], f"Missing column: {col}"


def test_capm_markdown_format(mock_capm_df):
    """Test capm with markdown output."""
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        mock_instance.capm.return_value = mock_capm_df

        response = finratio_capm(ticker="AAPL", freq="yearly", response_format="markdown")

    assert "data" in response
    assert isinstance(response["data"], str)
    # Markdown key-value format
    assert "Symbol" in response["data"]
    assert "CAPM" in response["data"]
    assert "Sharpe" in response["data"]


def test_capm_quarterly_freq(mock_capm_df):
    """Test capm with quarterly frequency."""
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        mock_instance.capm.return_value = mock_capm_df

        response = finratio_capm(ticker="MSFT", freq="quarterly", response_format="json")

    assert "data" in response
    assert isinstance(response["data"], dict)
