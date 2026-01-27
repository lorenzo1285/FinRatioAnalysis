"""
Pytest configuration and shared fixtures
"""
import pytest
from unittest.mock import MagicMock, patch
from tests.fixtures.sample_data import (
    get_mock_company_info,
    get_mock_balance_sheet,
    get_mock_income_stmt,
    get_mock_cash_flow,
    get_mock_price_history,
    get_mock_market_history,
    get_mock_treasury_rate
)

@pytest.fixture
def mock_yfinance(mocker):
    """Mock yfinance Ticker to avoid real API calls."""
    
    # Create mock ticker
    mock_ticker = MagicMock()
    mock_ticker.get_info.return_value = get_mock_company_info()
    mock_ticker.get_balance_sheet.return_value = get_mock_balance_sheet()
    mock_ticker.get_income_stmt.return_value = get_mock_income_stmt()
    mock_ticker.get_cash_flow.return_value = get_mock_cash_flow()
    mock_ticker.history.return_value = get_mock_price_history()
    
    # Mock market ticker (S&P 500)
    mock_market = MagicMock()
    mock_market.history.return_value = get_mock_market_history()
    
    def ticker_side_effect(symbol):
        if symbol == '^GSPC':
            return mock_market
        return mock_ticker
    
    # Patch yf.Ticker
    mocker.patch('yfinance.Ticker', side_effect=ticker_side_effect)
    
    # Patch requests.get for Treasury rates (FRED API)
    mock_response = mocker.Mock()
    mock_response.text = get_mock_treasury_rate().to_csv()
    mock_response.raise_for_status = mocker.Mock()
    mocker.patch('requests.get', return_value=mock_response)
    
    return mock_ticker

@pytest.fixture
def analyzer(mock_yfinance):
    """Create a FinRatioAnalysis instance with mocked data."""
    from FinRatioAnalysis import FinRatioAnalysis
    return FinRatioAnalysis('AAPL', 'yearly')


# =============================================================================
# REAL DATA FIXTURES (for integration tests)
# =============================================================================

@pytest.fixture
def real_analyzer():
    """
    Create a FinRatioAnalysis instance with REAL yfinance data.
    
    Use this fixture for integration tests by marking them with @pytest.mark.integration
    
    Example:
        @pytest.mark.integration
        def test_with_real_data(real_analyzer):
            result = real_analyzer.return_ratios()
            assert not result.empty
    """
    from FinRatioAnalysis import FinRatioAnalysis
    # Using a stable, well-known ticker
    return FinRatioAnalysis('AAPL', 'yearly')


@pytest.fixture
def real_analyzer_quarterly():
    """Create a FinRatioAnalysis instance with REAL quarterly data."""
    from FinRatioAnalysis import FinRatioAnalysis
    return FinRatioAnalysis('AAPL', 'quarterly')


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", 
        "integration: marks tests that use real API calls (deselect with '-m \"not integration\"')"
    )
    config.addinivalue_line(
        "markers",
        "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
