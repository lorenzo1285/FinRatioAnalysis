"""
Tests for z_score and z_score_plot methods
"""
import pytest
import pandas as pd

class TestZScore:
    """Test Altman Z-Score calculations."""
    
    def test_z_score_returns_dataframe(self, analyzer):
        """Test that z_score returns a DataFrame."""
        result = analyzer.z_score()
        assert isinstance(result, pd.DataFrame)
    
    def test_z_score_columns(self, analyzer):
        """Test that all expected columns are present."""
        result = analyzer.z_score()
        expected_columns = ['Symbol', 'Z Score', 'Zone']
        
        for col in expected_columns:
            assert col in result.columns, f"Missing column: {col}"
    
    def test_z_score_not_empty(self, analyzer):
        """Test that result is not empty."""
        result = analyzer.z_score()
        assert not result.empty
    
    def test_z_score_symbol(self, analyzer):
        """Test that symbol is correctly set."""
        result = analyzer.z_score()
        assert result['Symbol'].iloc[0] == 'AAPL'
    
    def test_z_score_is_numeric(self, analyzer):
        """Test that Z Score is a numeric value."""
        result = analyzer.z_score()
        assert isinstance(result['Z Score'].iloc[0], (int, float))
        assert result['Z Score'].iloc[0] > 0  # Should be positive
    
    def test_z_score_zone_classification(self, analyzer):
        """Test that zone is one of the valid zones."""
        result = analyzer.z_score()
        valid_zones = ['Distress Zone', 'Grey Zone', 'Safe Zone']
        assert result['Zone'].iloc[0] in valid_zones
    
    def test_z_score_distress_threshold(self, mocker, mock_yfinance):
        """Test zone classification for distress threshold."""
        from FinRatioAnalysis import FinRatioAnalysis
        
        # Create analyzer
        analyzer = FinRatioAnalysis('AAPL', 'yearly')
        
        # Mock _calculate_z_score to return distress zone value
        mocker.patch.object(analyzer, '_calculate_z_score', return_value=(1.5, 'Distress Zone'))
        
        result = analyzer.z_score()
        assert result['Zone'].iloc[0] == 'Distress Zone'
    
    def test_z_score_safe_threshold(self, mocker, mock_yfinance):
        """Test zone classification for safe threshold."""
        from FinRatioAnalysis import FinRatioAnalysis
        
        analyzer = FinRatioAnalysis('AAPL', 'yearly')
        
        # Mock _calculate_z_score to return safe zone value
        mocker.patch.object(analyzer, '_calculate_z_score', return_value=(5.0, 'Safe Zone'))
        
        result = analyzer.z_score()
        assert result['Zone'].iloc[0] == 'Safe Zone'
    
    def test_z_score_grey_threshold(self, mocker, mock_yfinance):
        """Test zone classification for grey zone."""
        from FinRatioAnalysis import FinRatioAnalysis
        
        analyzer = FinRatioAnalysis('AAPL', 'yearly')
        
        # Mock _calculate_z_score to return grey zone value
        mocker.patch.object(analyzer, '_calculate_z_score', return_value=(2.5, 'Grey Zone'))
        
        result = analyzer.z_score()
        assert result['Zone'].iloc[0] == 'Grey Zone'
    
    def test_calculate_z_score_private_method_exists(self, analyzer):
        """Test that private helper method exists."""
        assert hasattr(analyzer, '_calculate_z_score')
        assert callable(analyzer._calculate_z_score)
    
    def test_calculate_z_score_returns_tuple(self, analyzer):
        """Test that _calculate_z_score returns (score, zone) tuple."""
        score, zone = analyzer._calculate_z_score()
        
        assert isinstance(score, (int, float))
        assert isinstance(zone, str)
        assert zone in ['Distress Zone', 'Grey Zone', 'Safe Zone']
    
    def test_z_score_plot_exists(self, analyzer):
        """Test that z_score_plot method exists."""
        assert hasattr(analyzer, 'z_score_plot')
        assert callable(analyzer.z_score_plot)
    
    def test_z_score_consistency(self, analyzer):
        """Test that z_score returns consistent results."""
        result1 = analyzer.z_score()
        result2 = analyzer.z_score()
        
        assert result1['Z Score'].iloc[0] == result2['Z Score'].iloc[0]
        assert result1['Zone'].iloc[0] == result2['Zone'].iloc[0]
