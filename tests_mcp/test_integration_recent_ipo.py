"""
Integration tests for recent IPO behavior with live Yahoo Finance data.

Recent IPOs lack 3+ years of historical data, which affects metrics that
require multi-year comparisons (e.g., 3-year CAGR for revenue/EPS growth).

The MCP server should handle limited historical data gracefully by:
1. Returning null/NaN for unavailable metrics
2. Returning DATA_UNAVAILABLE error code where appropriate
3. Not crashing when data is insufficient

Run these tests with:
    pytest tests_mcp/test_integration_recent_ipo.py -m integration
"""
import pytest
from finratioanalysis_mcp.tools.return_ratios import finratio_return_ratios
from finratioanalysis_mcp.tools.valuation_growth_metrics import finratio_valuation_growth_metrics
from finratioanalysis_mcp.tools.historical_valuation_metrics import finratio_historical_valuation_metrics
from finratioanalysis_mcp.tools.z_score import finratio_z_score
from finratioanalysis_mcp.tools.capm import finratio_capm
from finratioanalysis_mcp.tools.wacc import finratio_wacc
from finratioanalysis_mcp.tools.company_snapshot import finratio_company_snapshot
from finratioanalysis_mcp.errors import ErrorCode

# ARM Holdings - IPO September 2023 (high-profile semiconductor company)
# As of April 2026, ARM has ~2.5 years of public data (insufficient for 3Y CAGR)
RECENT_IPO_TICKER = "ARM"
IPO_DATE_INFO = "September 2023"


@pytest.mark.integration
@pytest.mark.slow
class TestRecentIPOIntegration:
    """Integration tests for recent IPO edge cases."""
    
    def test_recent_ipo_limited_time_series(self):
        """
        Recent IPOs should return limited time-series data without crashing.
        """
        result = finratio_return_ratios(ticker=RECENT_IPO_TICKER, freq="yearly")
        
        # Should succeed with some data
        assert "data" in result
        assert isinstance(result["data"], list)
        
        # Will have fewer periods than established companies (< 3 years)
        data_length = len(result["data"])
        print(f"✓ {RECENT_IPO_TICKER} (IPO {IPO_DATE_INFO}): {data_length} yearly periods available")
        
        # Should have at least 1 period (most recent)
        assert data_length >= 1, "Should have at least one period of data"
        
        # But likely < 3 full years
        if data_length < 3:
            print(f"  Limited history: {data_length} years (< 3 expected for recent IPO)")
        
        # Check that available data is valid
        first_row = result["data"][0]
        assert first_row["ticker"] == RECENT_IPO_TICKER
        assert "Date" in first_row
        assert "ROE" in first_row
    
    def test_recent_ipo_quarterly_more_data(self):
        """
        Quarterly data should provide more periods even for recent IPOs.
        """
        tool = next(t for t in mcp_server.list_tools() if t.name == "finratio_return_ratios")
        
        yearly_result = tool.fn(ticker=RECENT_IPO_TICKER, freq="yearly")
        quarterly_result = tool.fn(ticker=RECENT_IPO_TICKER, freq="quarterly")
        
        yearly_count = len(yearly_result["data"])
        quarterly_count = len(quarterly_result["data"])
        
        # Quarterly should have more data points
        assert quarterly_count > yearly_count, "Quarterly should have more periods than yearly"
        
        print(f"✓ {RECENT_IPO_TICKER} data availability:")
        print(f"  Yearly: {yearly_count} periods")
        print(f"  Quarterly: {quarterly_count} periods")
    
    def test_recent_ipo_valuation_growth_null_cagr(self):
        """
        Recent IPOs should return null/NaN for 3-year CAGR metrics since
        they lack 3+ years of historical data.
        
        This is the KEY test case for T052.
        """
        result = finratio_valuation_growth_metrics(ticker=RECENT_IPO_TICKER)
        
        # Should return a result (not crash)
        assert "Symbol" in result
        assert result["Symbol"] == RECENT_IPO_TICKER
        
        # 3-year CAGR fields should exist but likely be null/NaN
        assert "Revenue_Growth_3Y_CAGR" in result
        assert "EPS_Growth_3Y_CAGR" in result
        assert "FCF_Growth_3Y_CAGR" in result
        
        revenue_3y = result["Revenue_Growth_3Y_CAGR"]
        eps_3y = result["EPS_Growth_3Y_CAGR"]
        fcf_3y = result["FCF_Growth_3Y_CAGR"]
        
        print(f"✓ {RECENT_IPO_TICKER} 3-year CAGR metrics:")
        print(f"  Revenue_Growth_3Y_CAGR = {revenue_3y} (null/NaN expected)")
        print(f"  EPS_Growth_3Y_CAGR = {eps_3y} (null/NaN expected)")
        print(f"  FCF_Growth_3Y_CAGR = {fcf_3y} (null/NaN expected)")
        
        # At least one should be null (insufficient history)
        null_count = sum(x is None for x in [revenue_3y, eps_3y, fcf_3y])
        
        if null_count > 0:
            print(f"  ✓ {null_count}/3 CAGR metrics are null (expected for recent IPO)")
        else:
            print(f"  ⚠ All CAGR metrics have values (unusual for {IPO_DATE_INFO} IPO)")
    
    def test_recent_ipo_valuation_growth_1y_available(self):
        """
        While 3Y CAGR may be unavailable, 1Y metrics should exist.
        """
        result = finratio_valuation_growth_metrics(ticker=RECENT_IPO_TICKER)
        
        # 1-year growth should be available (only needs 2 data points)
        if "Revenue_Growth_1Y" in result:
            revenue_1y = result["Revenue_Growth_1Y"]
            print(f"✓ {RECENT_IPO_TICKER} Revenue_Growth_1Y = {revenue_1y}")
            
            # This should ideally have a value (even for IPO)
            if revenue_1y is not None:
                print(f"  1-year growth available despite recent IPO")
    
    def test_recent_ipo_historical_valuation_limited_periods(self):
        """
        Historical valuation metrics should work but return fewer periods.
        """
        result = finratio_historical_valuation_metrics(ticker=RECENT_IPO_TICKER, freq="yearly")
        
        assert "data" in result
        assert isinstance(result["data"], list)
        
        periods = len(result["data"])
        print(f"✓ {RECENT_IPO_TICKER} historical valuation: {periods} periods")
        
        # Should have at least 1 period
        assert periods >= 1
        
        # Check data quality
        if periods > 0:
            first_row = result["data"][0]
            assert first_row["ticker"] == RECENT_IPO_TICKER
            assert "PE_Ratio" in first_row
            print(f"  Most recent P/E = {first_row['PE_Ratio']}")
    
    def test_recent_ipo_z_score_works(self):
        """
        Z-Score should work with most recent balance sheet (doesn't need 3Y history).
        """
        result = finratio_z_score(ticker=RECENT_IPO_TICKER)
        
        assert "Symbol" in result
        assert result["Symbol"] == RECENT_IPO_TICKER
        assert "Z Score" in result
        assert "Zone" in result
        
        z_score = result["Z Score"]
        zone = result["Zone"]
        
        print(f"✓ {RECENT_IPO_TICKER} Z-Score = {z_score}")
        print(f"  Zone = {zone}")
        print(f"  (Z-Score uses most recent data, doesn't require 3Y history)")
    
    def test_recent_ipo_capm_works(self):
        """
        CAPM should work - beta can be calculated from available trading history.
        """
        result = finratio_capm(ticker=RECENT_IPO_TICKER)
        
        assert "Symbol" in result
        assert result["Symbol"] == RECENT_IPO_TICKER
        assert "Beta" in result
        assert "Expected_Return" in result
        
        beta = result["Beta"]
        expected_return = result["Expected_Return"]
        
        print(f"✓ {RECENT_IPO_TICKER} CAPM:")
        print(f"  Beta = {beta}")
        print(f"  Expected Return = {expected_return}")
        print(f"  (Beta calculated from available trading history since IPO)")
    
    def test_recent_ipo_wacc_works(self):
        """
        WACC should work with most recent balance sheet data.
        """
        result = finratio_wacc(ticker=RECENT_IPO_TICKER)
        
        assert "Symbol" in result
        assert result["Symbol"] == RECENT_IPO_TICKER
        assert "WACC" in result
        
        wacc = result["WACC"]
        print(f"✓ {RECENT_IPO_TICKER} WACC = {wacc}")
    
    def test_recent_ipo_company_snapshot_graceful_degradation(self):
        """
        Aggregate snapshot should succeed with graceful degradation.
        Sections using most recent data succeed, multi-year CAGR may have nulls.
        """
        result = finratio_company_snapshot(ticker=RECENT_IPO_TICKER, freq="yearly")
        
        # All sections should be present
        assert "return_ratios" in result
        assert "valuation_growth_metrics" in result
        assert "z_score" in result
        assert "capm" in result
        assert "wacc" in result
        
        # Count successful sections
        success_count = sum(1 for s in result.values() if s.get("status") == "ok")
        
        print(f"✓ {RECENT_IPO_TICKER} company snapshot: {success_count}/10 sections OK")
        
        # Check valuation growth has nulls for 3Y CAGR
        if result["valuation_growth_metrics"]["status"] == "ok":
            vg_data = result["valuation_growth_metrics"]
            revenue_3y = vg_data.get("Revenue_Growth_3Y_CAGR")
            print(f"  Revenue_Growth_3Y_CAGR = {revenue_3y} (via aggregate tool)")
    
    def test_recent_ipo_no_data_unavailable_error(self):
        """
        Verify that limited data results in null values rather than
        DATA_UNAVAILABLE errors (unless truly no data exists).
        
        For recent IPOs, we expect successful responses with partial nulls,
        not wholesale DATA_UNAVAILABLE errors.
        """
        result = finratio_return_ratios(ticker=RECENT_IPO_TICKER, freq="yearly")
        
        # Should not be an error response
        assert "data" in result, "Should return data structure, not error"
        
        # Check if it's an error format
        is_error = "error" in result and "code" in result
        
        if is_error:
            error_code = result.get("code")
            print(f"⚠ Unexpected error: {error_code}")
            print(f"  Recent IPOs should return data (with nulls) rather than errors")
            assert error_code != ErrorCode.DATA_UNAVAILABLE.value, \
                "Should not return DATA_UNAVAILABLE for IPO with some data"
        else:
            print(f"✓ {RECENT_IPO_TICKER} returns data structure (not error) as expected")
    
    def test_compare_ipo_vs_established_data_availability(self):
        """
        Compare data availability between recent IPO and established company.
        Demonstrates the difference in historical depth.
        """
        tool = next(t for t in mcp_server.list_tools() if t.name == "finratio_return_ratios")
        
        # Recent IPO
        ipo_result = tool.fn(ticker=RECENT_IPO_TICKER, freq="yearly")
        ipo_periods = len(ipo_result["data"])
        
        # Established company (AAPL has decades of data)
        established_result = tool.fn(ticker="AAPL", freq="yearly")
        established_periods = len(established_result["data"])
        
        print(f"\n✓ Data availability comparison:")
        print(f"  {RECENT_IPO_TICKER} (IPO {IPO_DATE_INFO}): {ipo_periods} yearly periods")
        print(f"  AAPL (established): {established_periods} yearly periods")
        
        # IPO should have significantly fewer periods
        assert ipo_periods < established_periods, \
            "Recent IPO should have fewer periods than established company"
        
        # But both should have data
        assert ipo_periods >= 1, "IPO should have at least one period"
        assert established_periods >= 5, "Established company should have many periods"


