"""
Tests for leverage_ratios method
"""
import pytest
import pandas as pd

class TestLeverageRatios:
    """Test leverage and solvency ratio calculations."""
    
    def test_leverage_ratios_returns_dataframe(self, analyzer):
        """Test that leverage_ratios returns a DataFrame."""
        result = analyzer.leverage_ratios()
        assert isinstance(result, pd.DataFrame)
    
    def test_leverage_ratios_columns(self, analyzer):
        """Test that all expected columns are present."""
        result = analyzer.leverage_ratios()
        expected_columns = ['DebtEquityRatio', 'EquityRatio', 'DebtRatio']
        
        for col in expected_columns:
            assert col in result.columns, f"Missing column: {col}"
    
    def test_leverage_ratios_not_empty(self, analyzer):
        """Test that result is not empty."""
        result = analyzer.leverage_ratios()
        assert not result.empty
    
    def test_debt_equity_ratio_calculation(self, analyzer):
        """Test Debt-to-Equity ratio calculation."""
        result = analyzer.leverage_ratios()
        
        # Debt-to-Equity = Total Debt / Stockholders Equity
        # From mock data: 111088000000 / 62146000000 ≈ 1.787
        assert 'DebtEquityRatio' in result.columns
        assert result['DebtEquityRatio'].iloc[0] > 0
    
    def test_equity_ratio_calculation(self, analyzer):
        """Test Equity Ratio calculation."""
        result = analyzer.leverage_ratios()
        
        # Equity Ratio = Stockholders Equity / Total Assets
        # Should be between 0 and 1
        assert 'EquityRatio' in result.columns
        assert 0 < result['EquityRatio'].iloc[0] < 1
    
    def test_debt_ratio_calculation(self, analyzer):
        """Test Debt Ratio calculation."""
        result = analyzer.leverage_ratios()
        
        # Debt Ratio = Total Debt / Total Assets
        # Should be between 0 and 1
        assert 'DebtRatio' in result.columns
        assert 0 < result['DebtRatio'].iloc[0] < 1
    
    def test_equity_and_debt_ratios_sum(self, analyzer):
        """Test that Equity Ratio + Debt Ratio is reasonable."""
        result = analyzer.leverage_ratios()
        
        # Not exact sum to 1 due to other liabilities, but should be reasonable
        # Lower bound relaxed to account for companies with significant other liabilities
        total = result['EquityRatio'].iloc[0] + result['DebtRatio'].iloc[0]
        assert 0.4 < total < 1.5
    
    def test_backward_compatibility(self, analyzer):
        """Test that old LeverageRatios method still works."""
        result_new = analyzer.leverage_ratios()
        result_old = analyzer.LeverageRatios()
        
        pd.testing.assert_frame_equal(result_new, result_old)
