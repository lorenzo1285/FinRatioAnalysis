"""Unit tests for error handling."""

import pytest
from finratioanalysis_mcp.errors import ErrorCode, MCPError, error_response


class TestErrorCode:
    """Tests for ErrorCode enum."""
    
    def test_all_error_codes_exist(self):
        """Test that all expected error codes are defined."""
        expected_codes = [
            'INVALID_TICKER',
            'UNSUPPORTED_FREQ',
            'DATA_UNAVAILABLE',
            'UPSTREAM_ERROR',
            'INTERNAL_ERROR',
        ]
        
        for code in expected_codes:
            assert hasattr(ErrorCode, code)
            assert ErrorCode[code].value == code


class TestMCPError:
    """Tests for MCPError exception."""
    
    def test_basic_construction(self):
        """Test basic MCPError construction."""
        error = MCPError(
            code=ErrorCode.INVALID_TICKER,
            message="Ticker not found",
        )
        
        assert error.code == ErrorCode.INVALID_TICKER
        assert error.message == "Ticker not found"
        assert error.details is None
    
    def test_with_details(self):
        """Test MCPError with details."""
        details = {"ticker": "ZZZZZ", "suggestion": "Try AAPL"}
        error = MCPError(
            code=ErrorCode.INVALID_TICKER,
            message="Ticker not found",
            details=details,
        )
        
        assert error.code == ErrorCode.INVALID_TICKER
        assert error.message == "Ticker not found"
        assert error.details == details
    
    def test_is_exception(self):
        """Test that MCPError is a proper exception."""
        error = MCPError(ErrorCode.INTERNAL_ERROR, "Test error")
        
        assert isinstance(error, Exception)
        
        # Test that it can be raised
        with pytest.raises(MCPError) as exc_info:
            raise error
        
        assert exc_info.value.code == ErrorCode.INTERNAL_ERROR


class TestErrorResponse:
    """Tests for error_response function."""
    
    def test_basic_response(self):
        """Test basic error response generation."""
        error = MCPError(
            code=ErrorCode.INVALID_TICKER,
            message="Ticker ZZZZZ not found",
        )
        
        response = error_response(error)
        
        assert response['code'] == 'INVALID_TICKER'
        assert response['message'] == "Ticker ZZZZZ not found"
        assert 'details' not in response
    
    def test_response_with_details(self):
        """Test error response with details."""
        details = {"ticker": "ZZZZZ", "suggested_tickers": ["AAPL", "MSFT"]}
        error = MCPError(
            code=ErrorCode.INVALID_TICKER,
            message="Ticker not found",
            details=details,
        )
        
        response = error_response(error)
        
        assert response['code'] == 'INVALID_TICKER'
        assert response['message'] == "Ticker not found"
        assert response['details'] == details
    
    def test_code_is_string_value(self):
        """Test that code in response is the string value, not enum."""
        error = MCPError(ErrorCode.UPSTREAM_ERROR, "API failed")
        
        response = error_response(error)
        
        assert isinstance(response['code'], str)
        assert response['code'] == 'UPSTREAM_ERROR'
    
    def test_no_stack_trace_in_response(self):
        """Test that error response doesn't leak stack traces."""
        error = MCPError(
            code=ErrorCode.INTERNAL_ERROR,
            message="Something went wrong",
            details={"error_type": "ValueError"},
        )
        
        response = error_response(error)
        
        # Check that response doesn't contain stack trace indicators
        response_str = str(response)
        assert 'Traceback' not in response_str
        assert 'File "' not in response_str
        assert 'line ' not in response_str or 'line' not in response_str.lower()
    
    def test_all_error_codes_produce_valid_response(self):
        """Test that all error codes produce valid responses."""
        for code in ErrorCode:
            error = MCPError(code, f"Test message for {code.value}")
            response = error_response(error)
            
            assert 'code' in response
            assert 'message' in response
            assert response['code'] == code.value
