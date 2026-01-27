"""
Tests for efficiency_ratios method
"""
import pytest
import pandas as pd

class TestEfficiencyRatios:
    """Test efficiency and activity ratio calculations."""
    
    def test_efficiency_ratios_returns_dataframe(self, analyzer):
        """Test that efficiency_ratios returns a DataFrame."""
        result = analyzer.efficiency_ratios()
        assert isinstance(result, pd.DataFrame)
    
    def test_efficiency_ratios_columns(self, analyzer):
        """Test that all expected columns are present."""
        result = analyzer.efficiency_ratios()
        expected_columns = ['AssetTurnover', 'ReceivableTurnover', 
                           'InventoryTurnover', 'FixedAssetTurnover']
        
        for col in expected_columns:
            assert col in result.columns, f"Missing column: {col}"
    
    def test_efficiency_ratios_not_empty(self, analyzer):
        """Test that result is not empty."""
        result = analyzer.efficiency_ratios()
        assert not result.empty
    
    def test_asset_turnover_calculation(self, analyzer):
        """Test Asset Turnover calculation."""
        result = analyzer.efficiency_ratios()
        
        # Asset Turnover = Total Revenue / Total Assets
        # Should be positive
        assert 'AssetTurnover' in result.columns
        assert result['AssetTurnover'].iloc[0] > 0
    
    def test_receivable_turnover_calculation(self, analyzer):
        """Test Receivable Turnover calculation."""
        result = analyzer.efficiency_ratios()
        
        # Receivable Turnover = Total Revenue / Receivables
        # Should be positive and typically > 1
        assert 'ReceivableTurnover' in result.columns
        assert result['ReceivableTurnover'].iloc[0] > 0
    
    def test_inventory_turnover_calculation(self, analyzer):
        """Test Inventory Turnover calculation."""
        result = analyzer.efficiency_ratios()
        
        # Inventory Turnover = Cost of Revenue / Inventory
        # Should be positive
        assert 'InventoryTurnover' in result.columns
        assert result['InventoryTurnover'].iloc[0] > 0
    
    def test_fixed_asset_turnover_calculation(self, analyzer):
        """Test Fixed Asset Turnover calculation."""
        result = analyzer.efficiency_ratios()
        
        # Fixed Asset Turnover = Revenue / (Total Assets - Current Assets)
        # Should be positive
        assert 'FixedAssetTurnover' in result.columns
        assert result['FixedAssetTurnover'].iloc[0] > 0
    
    def test_backward_compatibility(self, analyzer):
        """Test that old EfficiencyRatios method still works."""
        result_new = analyzer.efficiency_ratios()
        result_old = analyzer.EfficiencyRatios()
        
        pd.testing.assert_frame_equal(result_new, result_old)
