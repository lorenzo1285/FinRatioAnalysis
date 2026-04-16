"""T042: Test that no stack traces leak in error responses.

Verifies that unexpected exceptions are caught and wrapped as structured
ErrorResponse objects with code=INTERNAL_ERROR, and that no Python
traceback strings appear in the response per FR-006.
"""

import pytest
from unittest.mock import patch

from finratioanalysis_mcp.tools.return_ratios import finratio_return_ratios
from finratioanalysis_mcp.tools.z_score import finratio_z_score
from finratioanalysis_mcp.errors import ErrorCode


def test_unexpected_exception_wrapped_as_internal_error():
    """Test that arbitrary exceptions become INTERNAL_ERROR responses."""
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        # Force an unexpected exception
        mock_instance.return_ratios.side_effect = RuntimeError("Simulated crash")
        
        response = finratio_return_ratios(ticker="AAPL", freq="yearly", response_format="json")
    
    # Should be an error response
    assert "code" in response
    assert "message" in response
    assert "data" not in response
    
    # Should be INTERNAL_ERROR
    assert response["code"] == ErrorCode.INTERNAL_ERROR.value
    assert len(response["message"]) > 0


def test_no_traceback_in_error_message():
    """Test that exception tracebacks don't leak into error messages."""
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        mock_instance.return_ratios.side_effect = ValueError("Test error with traceback")
        
        response = finratio_return_ratios(ticker="AAPL", freq="yearly", response_format="json")
    
    # Check all fields in the response for traceback indicators
    response_str = str(response)
    
    # These strings are typical traceback indicators that should NOT appear
    forbidden_strings = [
        "Traceback (most recent call last)",
        'File "',
        "line ",
        ".py\", line",
        "raise ",
        "in <module>",
        "in main",
        "in _call_library",
    ]
    
    for forbidden in forbidden_strings:
        assert forbidden not in response_str, \
            f"Traceback indicator '{forbidden}' found in error response"


def test_no_traceback_in_details_field():
    """Test that even the optional 'details' field doesn't contain tracebacks."""
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        mock_instance.z_score.side_effect = KeyError("missing_field")
        
        response = finratio_z_score(ticker="AAPL", freq="yearly", response_format="json")
    
    # If details field exists, inspect it
    if "details" in response and response["details"]:
        details_str = str(response["details"])
        assert "Traceback" not in details_str
        assert 'File "' not in details_str


def test_error_has_reference_id():
    """Test that errors include a reference ID for correlation (req_id)."""
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        mock_instance.return_ratios.side_effect = Exception("Test error")
        
        response = finratio_return_ratios(ticker="AAPL", freq="yearly", response_format="json")
    
    # Check for reference ID in message or details
    response_str = str(response)
    assert "ref=" in response_str or "req_id" in response_str, \
        "Error should include a correlation reference ID"


def test_multiple_exception_types_all_wrapped():
    """Test that various exception types all get wrapped properly."""
    exception_types = [
        ValueError("Test value error"),
        KeyError("missing_key"),
        AttributeError("no such attribute"),
        TypeError("wrong type"),
        RuntimeError("runtime issue"),
    ]
    
    for exc in exception_types:
        with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
            mock_instance = MockClass.return_value
            mock_instance.return_ratios.side_effect = exc
            
            response = finratio_return_ratios(ticker="AAPL", freq="yearly", response_format="json")
        
        # All should produce structured error responses
        assert "code" in response, f"Exception {type(exc).__name__} should produce error response"
        assert "message" in response
        assert "data" not in response
        
        # Should not leak the exception type name in a way that reveals internals
        # (though error_type in details is acceptable for debugging)
        assert response["code"] in [
            ErrorCode.INTERNAL_ERROR.value,
            ErrorCode.UPSTREAM_ERROR.value,
        ]


def test_connection_error_mapped_to_upstream_error():
    """Test that network errors are mapped to UPSTREAM_ERROR not INTERNAL_ERROR."""
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        mock_instance.return_ratios.side_effect = ConnectionError("Network unreachable")
        
        response = finratio_return_ratios(ticker="AAPL", freq="yearly", response_format="json")
    
    assert "code" in response
    # Should be UPSTREAM_ERROR for connection issues
    assert response["code"] == ErrorCode.UPSTREAM_ERROR.value
    assert "message" in response
    
    # Message should hint at Yahoo Finance issue
    assert "yahoo" in response["message"].lower() or "upstream" in response["message"].lower()


def test_timeout_error_mapped_to_upstream_error():
    """Test that timeout errors are mapped to UPSTREAM_ERROR."""
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        mock_instance.return_ratios.side_effect = TimeoutError("Request timed out")
        
        response = finratio_return_ratios(ticker="AAPL", freq="yearly", response_format="json")
    
    assert "code" in response
    assert response["code"] == ErrorCode.UPSTREAM_ERROR.value
