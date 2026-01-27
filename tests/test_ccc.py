"""
Tests for ccc (Cash Conversion Cycle) method
"""
import pytest
import pandas as pd

class TestCCC:
    """Test Cash Conversion Cycle calculations."""
    
    def test_ccc_returns_dataframe(self, analyzer):
        """Test that ccc returns a DataFrame."""
        result = analyzer.ccc()
        assert isinstance(result, pd.DataFrame)
    
    def test_ccc_columns(self, analyzer):
        """Test that all expected columns are present."""
        result = analyzer.ccc()
        expected_columns = ['DIO', 'DSO', 'DPO', 'CCC']
        
        for col in expected_columns:
            assert col in result.columns, f"Missing column: {col}"
    
    def test_ccc_not_empty(self, analyzer):
        """Test that result is not empty."""
        result = analyzer.ccc()
        assert not result.empty
    
    def test_dio_calculation(self, analyzer):
        """Test Days Inventory Outstanding calculation."""
        result = analyzer.ccc()
        
        # DIO = (Average Inventory / COGS) * 365
        # Should be positive number of days
        assert 'DIO' in result.columns
        assert result['DIO'].iloc[0] > 0
    
    def test_dso_calculation(self, analyzer):
        """Test Days Sales Outstanding calculation."""
        result = analyzer.ccc()
        
        # DSO = (Average Receivables / Revenue) * 365
        # Should be positive number of days
        assert 'DSO' in result.columns
        assert result['DSO'].iloc[0] > 0
    
    def test_dpo_calculation(self, analyzer):
        """Test Days Payables Outstanding calculation."""
        result = analyzer.ccc()
        
        # DPO = (Average Payables / COGS) * 365
        # Should be positive number of days
        assert 'DPO' in result.columns
        assert result['DPO'].iloc[0] > 0
    
    def test_ccc_formula(self, analyzer):
        """Test that CCC = DIO + DSO - DPO."""
        result = analyzer.ccc()
        
        # Verify the formula for first period
        calculated_ccc = result['DIO'].iloc[0] + result['DSO'].iloc[0] - result['DPO'].iloc[0]
        actual_ccc = result['CCC'].iloc[0]
        
        # Use approximate equality for floating point
        assert abs(calculated_ccc - actual_ccc) < 0.001
    
    def test_ccc_can_be_negative(self, analyzer):
        """Test that CCC can be negative (which is good)."""
        result = analyzer.ccc()
        
        # CCC can be positive or negative
        # Just verify it's a number
        assert isinstance(result['CCC'].iloc[0], (int, float))
    
    def test_backward_compatibility(self, analyzer):
        """Test that old CCC method still works."""
        result_new = analyzer.ccc()
        result_old = analyzer.CCC()
        
        pd.testing.assert_frame_equal(result_new, result_old)
