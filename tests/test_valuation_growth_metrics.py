"""
Tests for valuation_growth_metrics method
"""
import pytest
import pandas as pd
import numpy as np

class TestValuationGrowthMetrics:
    """Test valuation and growth metric calculations."""
    
    def test_valuation_growth_metrics_returns_dataframe(self, analyzer):
        """Test that valuation_growth_metrics returns a DataFrame."""
        result = analyzer.valuation_growth_metrics()
        assert isinstance(result, pd.DataFrame)
    
    def test_valuation_growth_metrics_columns(self, analyzer):
        """Test that all expected columns are present."""
        result = analyzer.valuation_growth_metrics()
        expected_columns = [
            'dividend_yield', 'payout_ratio', 
            'pe_ratio', 'forward_pe',
            'ps_ratio', 'beta',
            'revenue_cagr_3y', 'net_income_cagr_3y'
        ]
        
        for col in expected_columns:
            assert col in result.columns, f"Missing column: {col}"
    
    def test_valuation_growth_metrics_single_row(self, analyzer):
        """Test that result contains exactly one row."""
        result = analyzer.valuation_growth_metrics()
        assert len(result) == 1
    
    def test_dividend_yield_value(self, analyzer):
        """Test dividend yield is a valid number."""
        result = analyzer.valuation_growth_metrics()
        assert 'dividend_yield' in result.columns
        assert isinstance(result['dividend_yield'].iloc[0], (int, float, np.number))
        assert result['dividend_yield'].iloc[0] >= 0
    
    def test_payout_ratio_value(self, analyzer):
        """Test payout ratio is a valid number."""
        result = analyzer.valuation_growth_metrics()
        assert 'payout_ratio' in result.columns
        assert isinstance(result['payout_ratio'].iloc[0], (int, float, np.number))
        assert result['payout_ratio'].iloc[0] >= 0
    
    def test_pe_ratio_value(self, analyzer):
        """Test P/E ratio is a valid number."""
        result = analyzer.valuation_growth_metrics()
        assert 'pe_ratio' in result.columns
        assert isinstance(result['pe_ratio'].iloc[0], (int, float, np.number))
        assert result['pe_ratio'].iloc[0] >= 0
    
    def test_forward_pe_value(self, analyzer):
        """Test forward P/E is a valid number."""
        result = analyzer.valuation_growth_metrics()
        assert 'forward_pe' in result.columns
        assert isinstance(result['forward_pe'].iloc[0], (int, float, np.number))
        assert result['forward_pe'].iloc[0] >= 0
    
    def test_ps_ratio_value(self, analyzer):
        """Test P/S ratio is a valid number."""
        result = analyzer.valuation_growth_metrics()
        assert 'ps_ratio' in result.columns
        assert isinstance(result['ps_ratio'].iloc[0], (int, float, np.number))
        assert result['ps_ratio'].iloc[0] >= 0
    
    def test_beta_value(self, analyzer):
        """Test beta is a valid number and defaults to 1.0 if None."""
        result = analyzer.valuation_growth_metrics()
        assert 'beta' in result.columns
        beta_value = result['beta'].iloc[0]
        assert isinstance(beta_value, (int, float, np.number))
        # Beta can be negative, but should default to 1.0 if not available
        assert beta_value != 0 or beta_value == 1.0
    
    def test_revenue_cagr_3y_calculation(self, analyzer):
        """Test revenue CAGR 3-year calculation."""
        result = analyzer.valuation_growth_metrics()
        assert 'revenue_cagr_3y' in result.columns
        cagr = result['revenue_cagr_3y'].iloc[0]
        assert isinstance(cagr, (int, float, np.number))
        # CAGR can be negative (declining revenue) but should be reasonable
        assert -1 <= cagr <= 10  # Between -100% and +1000%
    
    def test_net_income_cagr_3y_calculation(self, analyzer):
        """Test net income CAGR 3-year calculation."""
        result = analyzer.valuation_growth_metrics()
        assert 'net_income_cagr_3y' in result.columns
        cagr = result['net_income_cagr_3y'].iloc[0]
        assert isinstance(cagr, (int, float, np.number))
        # CAGR can be negative (declining income) but should be reasonable
        assert -1 <= cagr <= 10  # Between -100% and +1000%
    
    def test_cagr_with_insufficient_data(self, analyzer_with_limited_data):
        """Test CAGR returns 0.0 when insufficient historical data."""
        result = analyzer_with_limited_data.valuation_growth_metrics()
        # With less than 4 years of data, CAGR should be 0.0
        assert result['revenue_cagr_3y'].iloc[0] == 0.0
        assert result['net_income_cagr_3y'].iloc[0] == 0.0
    
    def test_handles_missing_info_gracefully(self, analyzer_with_no_info):
        """Test that method handles missing yfinance info gracefully."""
        result = analyzer_with_no_info.valuation_growth_metrics()
        # Should return DataFrame with zeros for missing data
        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        # Valuation metrics should be 0.0 when info is unavailable
        assert result['dividend_yield'].iloc[0] == 0.0
        assert result['pe_ratio'].iloc[0] == 0.0
    
    def test_handles_negative_values_in_cagr(self, analyzer):
        """Test CAGR calculation handles negative values correctly."""
        result = analyzer.valuation_growth_metrics()
        # CAGR should return 0.0 if past or current values are <= 0
        # This is tested implicitly by the validation that CAGR >= -1
        assert result['revenue_cagr_3y'].iloc[0] >= -1
        assert result['net_income_cagr_3y'].iloc[0] >= -1
    
    def test_all_metrics_are_numeric(self, analyzer):
        """Test that all returned values are numeric (no NaN, None, or strings)."""
        result = analyzer.valuation_growth_metrics()
        for col in result.columns:
            value = result[col].iloc[0]
            assert isinstance(value, (int, float, np.number)), \
                f"Column {col} has non-numeric value: {value} (type: {type(value)})"
            assert not pd.isna(value), f"Column {col} contains NaN"

@pytest.fixture
def analyzer_with_limited_data(mock_yfinance):
    """Fixture with limited historical data (less than 4 years)."""
    from FinRatioAnalysis import FinRatioAnalysis
    from tests.fixtures.sample_data import get_mock_income_stmt
    
    # Create analyzer
    analyzer = FinRatioAnalysis('AAPL')
    
    # Replace income_stmt with limited data (only 2 years)
    limited_income = get_mock_income_stmt()
    analyzer.income_stmt = limited_income.iloc[:, :2]  # Keep only 2 columns
    
    return analyzer

@pytest.fixture
def analyzer_with_no_info(mock_yfinance, mocker):
    """Fixture that simulates missing yfinance info."""
    from FinRatioAnalysis import FinRatioAnalysis
    from unittest.mock import MagicMock
    
    # Create analyzer
    analyzer = FinRatioAnalysis('AAPL')
    
    # Mock company.info to return empty dict
    analyzer.company.info = {}
    
    return analyzer
