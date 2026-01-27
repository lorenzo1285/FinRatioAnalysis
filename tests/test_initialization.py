"""
Tests for FinRatioAnalysis initialization and input validation
"""
import pytest
from FinRatioAnalysis import FinRatioAnalysis

class TestInitialization:
    """Test class initialization and input validation."""
    
    def test_valid_initialization(self, analyzer):
        """Test successful initialization with valid ticker."""
        assert analyzer.symbol == 'AAPL'
        assert analyzer.marketCap == 3000000000000
        assert analyzer.beta == 1.2
        assert analyzer.freq == 'yearly'
    
    def test_invalid_ticker_empty_string(self):
        """Test that empty ticker raises ValueError."""
        with pytest.raises(ValueError, match="Ticker must be a non-empty string"):
            FinRatioAnalysis('', 'yearly')
    
    def test_invalid_ticker_none(self):
        """Test that None ticker raises ValueError."""
        with pytest.raises(ValueError, match="Ticker must be a non-empty string"):
            FinRatioAnalysis(None, 'yearly')
    
    def test_invalid_frequency(self):
        """Test that invalid frequency raises ValueError."""
        with pytest.raises(ValueError, match="Frequency must be 'quarterly' or 'yearly'"):
            FinRatioAnalysis('AAPL', 'monthly')
    
    def test_quarterly_frequency(self, mock_yfinance):
        """Test initialization with quarterly frequency."""
        analyzer = FinRatioAnalysis('AAPL', 'quarterly')
        assert analyzer.freq == 'quarterly'
    
    def test_default_frequency(self, mock_yfinance):
        """Test that default frequency is 'yearly'."""
        analyzer = FinRatioAnalysis('AAPL')
        assert analyzer.freq == 'yearly'
    
    def test_balance_sheet_loaded(self, analyzer):
        """Test that balance sheet data is loaded."""
        assert not analyzer.balance_sheet.empty
        assert 'TotalAssets' in analyzer.balance_sheet.index
    
    def test_income_stmt_loaded(self, analyzer):
        """Test that income statement data is loaded."""
        assert not analyzer.income_stmt.empty
        assert 'NetIncome' in analyzer.income_stmt.index
    
    def test_cash_flow_loaded(self, analyzer):
        """Test that cash flow data is loaded."""
        assert not analyzer.cash_flow.empty
        assert 'OperatingCashFlow' in analyzer.cash_flow.index
    
    def test_market_data_loaded(self, analyzer):
        """Test that market data is loaded."""
        assert not analyzer.market_close.empty
        assert not analyzer.close.empty
    
    def test_treasury_rate_loaded(self, analyzer):
        """Test that Treasury rate data is loaded."""
        assert not analyzer.rate_10.empty
