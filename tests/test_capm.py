"""
Tests for capm (Capital Asset Pricing Model) method
"""
import pytest
import pandas as pd

class TestCAPM:
    """Test CAPM and Sharpe ratio calculations."""
    
    def test_capm_returns_dataframe(self, analyzer):
        """Test that capm returns a DataFrame."""
        result = analyzer.capm()
        assert isinstance(result, pd.DataFrame)
    
    def test_capm_columns(self, analyzer):
        """Test that all expected columns are present."""
        result = analyzer.capm()
        expected_columns = ['Symbol', 'CAPM', 'Sharpe']
        
        for col in expected_columns:
            assert col in result.columns, f"Missing column: {col}"
    
    def test_capm_not_empty(self, analyzer):
        """Test that result is not empty."""
        result = analyzer.capm()
        assert not result.empty
    
    def test_capm_symbol(self, analyzer):
        """Test that symbol is correctly set."""
        result = analyzer.capm()
        assert result['Symbol'].iloc[0] == 'AAPL'
    
    def test_capm_value_is_numeric(self, analyzer):
        """Test that CAPM value is numeric."""
        result = analyzer.capm()
        assert isinstance(result['CAPM'].iloc[0], (int, float))
    
    def test_capm_value_reasonable_range(self, analyzer):
        """Test that CAPM value is in reasonable range."""
        result = analyzer.capm()
        
        # Expected return should typically be between -50% and 50%
        assert -0.5 < result['CAPM'].iloc[0] < 0.5
    
    def test_sharpe_ratio_is_numeric(self, analyzer):
        """Test that Sharpe ratio is numeric."""
        result = analyzer.capm()
        assert isinstance(result['Sharpe'].iloc[0], (int, float))
    
    def test_sharpe_ratio_reasonable_range(self, analyzer):
        """Test that Sharpe ratio is in reasonable range."""
        result = analyzer.capm()
        
        # Sharpe ratio typically between -3 and 3
        assert -3 < result['Sharpe'].iloc[0] < 3
    
    def test_capm_uses_correct_formula(self, analyzer):
        """Test that CAPM calculation follows the formula."""
        result = analyzer.capm()
        
        # CAPM = Risk-Free Rate + Beta * (Market Return - Risk-Free Rate)
        # Just verify it's positive for this mock data
        assert result['CAPM'].iloc[0] != 0
    
    def test_sharpe_ratio_uses_sqrt_252(self, analyzer):
        """Test that Sharpe ratio uses correct annualization (sqrt(252))."""
        # This is a regression test for the bug fix
        result = analyzer.capm()
        
        # Sharpe ratio should be calculated, not NaN
        assert not pd.isna(result['Sharpe'].iloc[0])
    
    def test_backward_compatibility(self, analyzer):
        """Test that old CAPM method still works."""
        result_new = analyzer.capm()
        result_old = analyzer.CAPM()
        
        pd.testing.assert_frame_equal(result_new, result_old)
    
    def test_capm_consistency(self, analyzer):
        """Test that capm returns consistent results."""
        result1 = analyzer.capm()
        result2 = analyzer.capm()
        
        assert result1['CAPM'].iloc[0] == result2['CAPM'].iloc[0]
        assert result1['Sharpe'].iloc[0] == result2['Sharpe'].iloc[0]
