"""
Integration tests using REAL yfinance data.

These tests make actual API calls to Yahoo Finance and FRED.
They are slower and require internet connection.

Run these tests with:
    pytest tests/test_integration_real_data.py

Skip integration tests with:
    pytest -m "not integration"

Run ONLY integration tests with:
    pytest -m integration
"""
import pytest
import pandas as pd
import numpy as np


@pytest.mark.integration
@pytest.mark.slow
class TestRealDataIntegration:
    """Integration tests with real Yahoo Finance data."""
    
    def test_real_initialization(self, real_analyzer):
        """Test initialization with real data."""
        assert real_analyzer.symbol == 'AAPL'
        assert real_analyzer.marketCap is not None
        assert real_analyzer.marketCap > 0
        assert real_analyzer.beta is not None
        print(f"\n✓ Initialized AAPL - Market Cap: ${real_analyzer.marketCap:,.0f}")
    
    def test_real_return_ratios(self, real_analyzer):
        """Test return ratios with real data."""
        result = real_analyzer.return_ratios()
        
        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert 'ROE' in result.columns
        assert 'ROA' in result.columns
        assert 'ROCE' in result.columns
        assert 'GrossMargin' in result.columns
        
        # Check that values are reasonable (not NaN or infinite)
        assert not result.isna().all().any()
        print(f"\n✓ Return Ratios Retrieved:")
        print(result.head())
    
    def test_real_leverage_ratios(self, real_analyzer):
        """Test leverage ratios with real data."""
        result = real_analyzer.leverage_ratios()
        
        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert 'DebtEquityRatio' in result.columns
        assert 'EquityRatio' in result.columns
        assert 'DebtRatio' in result.columns
        
        print(f"\n✓ Leverage Ratios Retrieved:")
        print(result.head())
    
    def test_real_efficiency_ratios(self, real_analyzer):
        """Test efficiency ratios with real data."""
        result = real_analyzer.efficiency_ratios()
        
        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert 'AssetTurnover' in result.columns
        
        print(f"\n✓ Efficiency Ratios Retrieved:")
        print(result.head())
    
    def test_real_liquidity_ratios(self, real_analyzer):
        """Test liquidity ratios with real data."""
        result = real_analyzer.liquidity_ratios()
        
        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert 'CurrentRatios' in result.columns
        assert 'QuickRatio' in result.columns
        
        print(f"\n✓ Liquidity Ratios Retrieved:")
        print(result.head())
    
    def test_real_ccc(self, real_analyzer):
        """Test Cash Conversion Cycle with real data."""
        result = real_analyzer.ccc()
        
        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert 'DIO' in result.columns
        assert 'DSO' in result.columns
        assert 'DPO' in result.columns
        assert 'CCC' in result.columns
        
        print(f"\n✓ Cash Conversion Cycle Retrieved:")
        print(result.head())
    
    def test_real_z_score(self, real_analyzer):
        """Test Altman Z-Score with real data."""
        result = real_analyzer.z_score()
        
        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert 'Symbol' in result.columns
        assert 'Z Score' in result.columns
        assert 'Zone' in result.columns
        
        z_score_value = result['Z Score'].values[0]
        zone = result['Zone'].values[0]
        
        assert zone in ['Distress Zone', 'Grey Zone', 'Safe Zone']
        print(f"\n✓ Z-Score: {z_score_value:.3f} ({zone})")
    
    def test_real_capm(self, real_analyzer):
        """Test CAPM calculation with real data."""
        result = real_analyzer.capm()
        
        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert 'Symbol' in result.columns
        assert 'CAPM' in result.columns
        assert 'Sharpe' in result.columns
        
        capm_value = result['CAPM'].values[0]
        sharpe_value = result['Sharpe'].values[0]
        
        # CAPM should be reasonable (between -50% and 100%)
        assert -0.5 < capm_value < 1.0
        
        print(f"\n✓ CAPM: {capm_value:.4f} ({capm_value*100:.2f}%)")
        print(f"✓ Sharpe Ratio: {sharpe_value:.4f}")
    
    def test_real_wacc(self, real_analyzer):
        """Test WACC calculation with real data."""
        result = real_analyzer.wacc()
        
        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert 'Symbol' in result.columns
        assert 'WACC' in result.columns
        
        wacc_value = result['WACC'].values[0]
        
        # WACC should be reasonable (between 0% and 50%)
        assert 0 < wacc_value < 0.5
        
        print(f"\n✓ WACC: {wacc_value:.4f} ({wacc_value*100:.2f}%)")
    
    def test_real_quarterly_data(self, real_analyzer_quarterly):
        """Test with quarterly frequency."""
        assert real_analyzer_quarterly.freq == 'quarterly'
        
        result = real_analyzer_quarterly.return_ratios()
        assert not result.empty
        
        # Quarterly should have more data points
        print(f"\n✓ Quarterly data periods: {len(result)}")


@pytest.mark.integration
class TestMultipleTickers:
    """Test with different ticker symbols."""
    
    @pytest.mark.parametrize("ticker", [
        "MSFT",  # Microsoft
        "GOOGL", # Alphabet
        "JPM",   # JPMorgan Chase (financial sector)
    ])
    def test_different_tickers(self, ticker):
        """Test initialization and basic analysis for different companies."""
        from FinRatioAnalysis import FinRatioAnalysis
        
        analyzer = FinRatioAnalysis(ticker, 'yearly')
        
        assert analyzer.symbol == ticker
        assert analyzer.marketCap > 0
        
        # Test that we can get return ratios
        result = analyzer.return_ratios()
        assert not result.empty
        
        print(f"\n✓ {ticker} - Market Cap: ${analyzer.marketCap:,.0f}")
        print(f"  Latest ROE: {result['ROE'].iloc[0]:.4f}")


@pytest.mark.integration
class TestErrorHandlingRealData:
    """Test error handling with real API."""
    
    def test_invalid_ticker_real_api(self):
        """Test that invalid ticker raises appropriate error."""
        from FinRatioAnalysis import FinRatioAnalysis
        
        with pytest.raises(ValueError, match="Invalid ticker|Failed to fetch"):
            FinRatioAnalysis('INVALID_TICKER_XYZ123', 'yearly')
    
    def test_delisted_ticker(self):
        """Test behavior with delisted/problematic ticker."""
        from FinRatioAnalysis import FinRatioAnalysis
        
        # This should fail gracefully
        with pytest.raises(ValueError):
            FinRatioAnalysis('INVALIDXXX', 'yearly')


if __name__ == "__main__":
    # Run integration tests directly
    pytest.main([__file__, "-v", "-s", "-m", "integration"])
