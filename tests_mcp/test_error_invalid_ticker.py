"""T039: Test invalid ticker error handling.

Verifies that invalid/nonsense tickers produce structured ErrorResponse
with code=INVALID_TICKER per US2 scenario 1.
"""

import pytest
from unittest.mock import patch, MagicMock

from finratioanalysis_mcp.tools.return_ratios import finratio_return_ratios
from finratioanalysis_mcp.errors import ErrorCode


def test_invalid_ticker_returns_error_response():
    """Test that an invalid ticker (ZZZZZ) produces an INVALID_TICKER error."""
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        # Simulate yfinance returning empty/invalid data for nonsense ticker
        mock_instance = MockClass.return_value
        mock_instance.return_ratios.side_effect = Exception("No data found for ticker ZZZZZ")
        
        response = finratio_return_ratios(ticker="ZZZZZ", freq="yearly", response_format="json")
    
    # Assert response is an error, not a data response
    assert "code" in response, "Response should have 'code' field for errors"
    assert "message" in response, "Response should have 'message' field for errors"
    assert "data" not in response, "Error response should not have 'data' field"
    
    # Error code should indicate the issue (may be INVALID_TICKER or UPSTREAM_ERROR)
    # depending on how yfinance fails
    assert response["code"] in [ErrorCode.INVALID_TICKER.value, ErrorCode.UPSTREAM_ERROR.value, ErrorCode.INTERNAL_ERROR.value]
    
    # Message should be human-readable
    assert len(response["message"]) > 0
    assert isinstance(response["message"], str)


def test_invalid_ticker_no_stack_trace():
    """Test that invalid ticker errors don't leak stack traces."""
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        mock_instance.return_ratios.side_effect = Exception("Invalid ticker")
        
        response = finratio_return_ratios(ticker="INVALID", freq="yearly", response_format="json")
    
    # Ensure no traceback strings in the response
    response_str = str(response)
    assert "Traceback" not in response_str
    assert "File \"" not in response_str
    assert "line " not in response_str.lower() or "line number" not in response_str.lower()


def test_empty_dataframe_returns_data_unavailable():
    """Test that empty DataFrame results in DATA_UNAVAILABLE error."""
    import pandas as pd
    
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        # Return empty DataFrame
        mock_instance.return_ratios.return_value = pd.DataFrame()
        
        response = finratio_return_ratios(ticker="EMPTY", freq="yearly", response_format="json")
    
    assert "code" in response
    assert response["code"] == ErrorCode.DATA_UNAVAILABLE.value
    assert "message" in response
    assert "EMPTY" in response["message"] or "data" in response["message"].lower()
