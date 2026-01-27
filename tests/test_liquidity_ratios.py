"""
Tests for liquidity_ratios method
"""
import pytest
import pandas as pd

class TestLiquidityRatios:
    """Test liquidity and cash flow ratio calculations."""
    
    def test_liquidity_ratios_returns_dataframe(self, analyzer):
        """Test that liquidity_ratios returns a DataFrame."""
        result = analyzer.liquidity_ratios()
        assert isinstance(result, pd.DataFrame)
    
    def test_liquidity_ratios_columns(self, analyzer):
        """Test that all expected columns are present."""
        result = analyzer.liquidity_ratios()
        expected_columns = ['CurrentRatios', 'QuickRatio', 'CashRatio', 'DIR',
                           'TIE', 'TIE_CB', 'CAPEX_OpCash', 'OpCashFlow']
        
        for col in expected_columns:
            assert col in result.columns, f"Missing column: {col}"
    
    def test_liquidity_ratios_not_empty(self, analyzer):
        """Test that result is not empty."""
        result = analyzer.liquidity_ratios()
        assert not result.empty
    
    def test_current_ratio_calculation(self, analyzer):
        """Test Current Ratio calculation."""
        result = analyzer.liquidity_ratios()
        
        # Current Ratio = Current Assets / Current Liabilities
        # Should be positive, ideally > 1
        assert 'CurrentRatios' in result.columns
        assert result['CurrentRatios'].iloc[0] > 0
    
    def test_quick_ratio_calculation(self, analyzer):
        """Test Quick Ratio calculation."""
        result = analyzer.liquidity_ratios()
        
        # Quick Ratio = (Cash + Receivables) / Current Liabilities
        # Should be positive
        assert 'QuickRatio' in result.columns
        assert result['QuickRatio'].iloc[0] > 0
    
    def test_cash_ratio_calculation(self, analyzer):
        """Test Cash Ratio calculation."""
        result = analyzer.liquidity_ratios()
        
        # Cash Ratio = Cash / Current Liabilities
        # Should be between 0 and 1 typically
        assert 'CashRatio' in result.columns
        assert result['CashRatio'].iloc[0] > 0
    
    def test_dir_calculation(self, analyzer):
        """Test Defensive Interval Ratio calculation."""
        result = analyzer.liquidity_ratios()
        
        # DIR = Current Assets / Daily Expenses
        # Should be positive (number of days)
        assert 'DIR' in result.columns
        assert result['DIR'].iloc[0] > 0
    
    def test_tie_calculation(self, analyzer):
        """Test Times Interest Earned calculation."""
        result = analyzer.liquidity_ratios()
        
        # TIE = EBIT / Interest Expense
        # Should be positive, ideally >> 1
        assert 'TIE' in result.columns
        assert result['TIE'].iloc[0] > 0
    
    def test_tie_cb_calculation(self, analyzer):
        """Test Cash-Based TIE calculation."""
        result = analyzer.liquidity_ratios()
        
        # TIE_CB = Operating Cash Flow / Interest Expense
        assert 'TIE_CB' in result.columns
        assert result['TIE_CB'].iloc[0] > 0
    
    def test_capex_opcash_calculation(self, analyzer):
        """Test CAPEX to Operating Cash Flow ratio."""
        result = analyzer.liquidity_ratios()
        
        # CAPEX_OpCash = Operating CF / Capital Expenditure
        assert 'CAPEX_OpCash' in result.columns
        assert result['CAPEX_OpCash'].iloc[0] > 0
    
    def test_opcashflow_calculation(self, analyzer):
        """Test Operating Cash Flow to Current Liabilities ratio."""
        result = analyzer.liquidity_ratios()
        
        # OpCashFlow = Operating CF / Current Liabilities
        assert 'OpCashFlow' in result.columns
        assert result['OpCashFlow'].iloc[0] > 0
    
    def test_backward_compatibility(self, analyzer):
        """Test that old LiquidityRatios method still works."""
        result_new = analyzer.liquidity_ratios()
        result_old = analyzer.LiquidityRatios()
        
        pd.testing.assert_frame_equal(result_new, result_old)
