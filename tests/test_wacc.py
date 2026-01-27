"""
Tests for wacc (Weighted Average Cost of Capital) method
"""
import pytest
import pandas as pd

class TestWACC:
    """Test WACC calculations."""
    
    def test_wacc_returns_dataframe(self, analyzer):
        """Test that wacc returns a DataFrame."""
        result = analyzer.wacc()
        assert isinstance(result, pd.DataFrame)
    
    def test_wacc_columns(self, analyzer):
        """Test that all expected columns are present."""
        result = analyzer.wacc()
        expected_columns = ['Symbol', 'WACC']
        
        for col in expected_columns:
            assert col in result.columns, f"Missing column: {col}"
    
    def test_wacc_not_empty(self, analyzer):
        """Test that result is not empty."""
        result = analyzer.wacc()
        assert not result.empty
    
    def test_wacc_symbol(self, analyzer):
        """Test that symbol is correctly set."""
        result = analyzer.wacc()
        assert result['Symbol'].iloc[0] == 'AAPL'
    
    def test_wacc_value_is_numeric(self, analyzer):
        """Test that WACC value is numeric or array."""
        result = analyzer.wacc()
        wacc_value = result['WACC'].iloc[0]
        
        # WACC can be a single value or array
        assert isinstance(wacc_value, (int, float)) or hasattr(wacc_value, '__iter__')
    
    def test_wacc_uses_capm(self, analyzer, mocker):
        """Test that WACC calls capm method."""
        # Spy on capm method
        spy = mocker.spy(analyzer, 'capm')
        
        analyzer.wacc()
        
        # Verify capm was called
        spy.assert_called_once()
    
    def test_wacc_formula_components(self, analyzer):
        """Test that WACC formula components are calculated."""
        # Just verify the method runs without errors
        result = analyzer.wacc()
        
        # WACC should be calculated
        assert 'WACC' in result.columns
    
    def test_backward_compatibility(self, analyzer):
        """Test that old WACC method still works."""
        result_new = analyzer.wacc()
        result_old = analyzer.WACC()
        
        pd.testing.assert_frame_equal(result_new, result_old)
    
    def test_wacc_consistency(self, analyzer):
        """Test that wacc returns consistent results."""
        result1 = analyzer.wacc()
        result2 = analyzer.wacc()
        
        # Values should be the same
        assert str(result1['WACC'].iloc[0]) == str(result2['WACC'].iloc[0])
