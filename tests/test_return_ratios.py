"""
Tests for return_ratios method
"""
import pytest
import pandas as pd

class TestReturnRatios:
    """Test return and profitability ratio calculations."""
    
    def test_return_ratios_returns_dataframe(self, analyzer):
        """Test that return_ratios returns a DataFrame."""
        result = analyzer.return_ratios()
        assert isinstance(result, pd.DataFrame)
    
    def test_return_ratios_columns(self, analyzer):
        """Test that all expected columns are present."""
        result = analyzer.return_ratios()
        expected_columns = ['ROE', 'ROA', 'ROCE', 'GrossMargin', 'OperatingMargin', 'NetProfit']
        
        for col in expected_columns:
            assert col in result.columns, f"Missing column: {col}"
    
    def test_return_ratios_not_empty(self, analyzer):
        """Test that result is not empty."""
        result = analyzer.return_ratios()
        assert not result.empty
    
    def test_roe_calculation(self, analyzer):
        """Test ROE (Return on Equity) calculation."""
        result = analyzer.return_ratios()
        
        # ROE = Net Income / Stockholders Equity
        # From mock data: 96995000000 / 62146000000 ≈ 1.561
        assert 'ROE' in result.columns
        assert result['ROE'].iloc[0] > 0
    
    def test_roa_calculation(self, analyzer):
        """Test ROA (Return on Assets) calculation."""
        result = analyzer.return_ratios()
        
        # ROA = Net Income / Total Assets
        # From mock data: 96995000000 / 352755000000 ≈ 0.275
        assert 'ROA' in result.columns
        assert 0 < result['ROA'].iloc[0] < 1
    
    def test_roce_calculation(self, analyzer):
        """Test ROCE (Return on Capital Employed) calculation."""
        result = analyzer.return_ratios()
        
        # ROCE = EBIT / (Total Assets - Current Liabilities)
        assert 'ROCE' in result.columns
        assert result['ROCE'].iloc[0] > 0
    
    def test_gross_margin_calculation(self, analyzer):
        """Test Gross Margin calculation."""
        result = analyzer.return_ratios()
        
        # Gross Margin = Gross Profit / Total Revenue
        # Should be between 0 and 1 (or as percentage)
        assert 'GrossMargin' in result.columns
        assert 0 < result['GrossMargin'].iloc[0] < 1
    
    def test_operating_margin_calculation(self, analyzer):
        """Test Operating Margin calculation."""
        result = analyzer.return_ratios()
        
        # Operating Margin = EBIT / Total Revenue
        assert 'OperatingMargin' in result.columns
        assert 0 < result['OperatingMargin'].iloc[0] < 1
    
    def test_net_profit_calculation(self, analyzer):
        """Test Net Profit Margin calculation."""
        result = analyzer.return_ratios()
        
        # Net Profit = Net Income / Total Revenue
        assert 'NetProfit' in result.columns
        assert 0 < result['NetProfit'].iloc[0] < 1
    
    def test_return_ratios_has_time_series(self, analyzer):
        """Test that result has multiple time periods."""
        result = analyzer.return_ratios()
        # Mock data has 3 periods, now includes ROIC (7 columns total)
        assert len(result.columns) == 7
    
    def test_backward_compatibility(self, analyzer):
        """Test that old ReturnRatios method still works."""
        result_new = analyzer.return_ratios()
        result_old = analyzer.ReturnRatios()
        
        # Both should return the same DataFrame
        pd.testing.assert_frame_equal(result_new, result_old)
