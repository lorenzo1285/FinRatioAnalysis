"""T039: Test invalid ticker error handling.

Verifies that invalid/nonsense tickers produce structured ErrorResponse
with code=INVALID_TICKER per US2 scenario 1.
"""

from unittest.mock import patch

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
    
    # TODO(T043): tighten to `== ErrorCode.INVALID_TICKER.value` once the
    # yfinance pre-flight liveness probe lands. Today INVALID_TICKER is only
    # emittable via regex rejection (caught upstream by Pydantic), so a
    # format-valid-but-nonexistent ticker surfaces as INTERNAL_ERROR or
    # UPSTREAM_ERROR depending on how yfinance fails.
    assert response["code"] in [
        ErrorCode.INVALID_TICKER.value,
        ErrorCode.UPSTREAM_ERROR.value,
        ErrorCode.INTERNAL_ERROR.value,
    ]
    
    # Message should be human-readable
    assert len(response["message"]) > 0
    assert isinstance(response["message"], str)


def test_invalid_ticker_no_stack_trace():
    """Test that invalid ticker errors don't leak stack traces."""
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        mock_instance.return_ratios.side_effect = Exception("Invalid ticker")
        
        response = finratio_return_ratios(ticker="INVALID", freq="yearly", response_format="json")
    
    # Ensure no traceback strings in the response. The detailed
    # forbidden-substring list lives in tests_mcp/test_no_stack_traces.py
    # (T042); this test is a smoke check on the strongest indicators.
    response_str = str(response)
    assert "Traceback" not in response_str
    assert 'File "' not in response_str


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
