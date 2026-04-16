"""T040: Test unsupported frequency validation.

Verifies that invalid freq values are rejected at the Pydantic boundary
with clear validation error messages per US2 scenario 3.
"""

import pytest
from pydantic import ValidationError

from finratioanalysis_mcp.models import TickerRequest


def test_unsupported_freq_rejected():
    """Test that freq='monthly' is rejected with validation error."""
    with pytest.raises(ValidationError) as exc_info:
        TickerRequest(ticker="AAPL", freq="monthly", response_format="json")
    
    # Extract validation error details
    error = exc_info.value
    errors = error.errors()
    
    # Should have at least one error about freq field
    freq_errors = [e for e in errors if 'freq' in str(e.get('loc', []))]
    assert len(freq_errors) > 0, "Should have validation error for 'freq' field"
    
    # Error message should reference allowed values
    error_msg = str(error).lower()
    assert 'yearly' in error_msg or 'quarterly' in error_msg, \
        "Error message should mention allowed frequency values"


def test_valid_freq_yearly_accepted():
    """Test that freq='yearly' is accepted."""
    request = TickerRequest(ticker="AAPL", freq="yearly", response_format="json")
    assert request.freq == "yearly"


def test_valid_freq_quarterly_accepted():
    """Test that freq='quarterly' is accepted."""
    request = TickerRequest(ticker="AAPL", freq="quarterly", response_format="json")
    assert request.freq == "quarterly"


def test_freq_case_sensitive():
    """Test that freq validation is case-sensitive (only lowercase accepted)."""
    with pytest.raises(ValidationError):
        TickerRequest(ticker="AAPL", freq="Yearly", response_format="json")
    
    with pytest.raises(ValidationError):
        TickerRequest(ticker="AAPL", freq="QUARTERLY", response_format="json")


def test_invalid_response_format_rejected():
    """Test that invalid response_format values are also rejected."""
    with pytest.raises(ValidationError) as exc_info:
        TickerRequest(ticker="AAPL", freq="yearly", response_format="xml")
    
    error = exc_info.value
    errors = error.errors()
    
    # Should have error about response_format field
    format_errors = [e for e in errors if 'response_format' in str(e.get('loc', []))]
    assert len(format_errors) > 0, "Should have validation error for 'response_format' field"


def test_error_message_clarity():
    """Test that validation error messages are clear and actionable."""
    with pytest.raises(ValidationError) as exc_info:
        TickerRequest(ticker="AAPL", freq="daily", response_format="json")
    
    error_str = str(exc_info.value)
    
    # Error should be clear enough for an LLM to understand what went wrong
    assert len(error_str) > 20, "Error message should be substantive"
    assert "freq" in error_str or "frequency" in error_str.lower()
