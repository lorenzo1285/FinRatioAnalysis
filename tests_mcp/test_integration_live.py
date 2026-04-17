"""
Integration tests with live Yahoo Finance data via MCP tools.

Tests the complete MCP server against real market data for a basket of 
representative companies spanning different sectors.

Run these tests with:
    pytest tests_mcp/test_integration_live.py -m integration
"""
import asyncio
import pytest
from finratioanalysis_mcp.server import mcp
from finratioanalysis_mcp.tools.return_ratios import finratio_return_ratios
from finratioanalysis_mcp.tools.efficiency_ratios import finratio_efficiency_ratios
from finratioanalysis_mcp.tools.leverage_ratios import finratio_leverage_ratios
from finratioanalysis_mcp.tools.liquidity_ratios import finratio_liquidity_ratios
from finratioanalysis_mcp.tools.ccc import finratio_ccc
from finratioanalysis_mcp.tools.valuation_growth_metrics import finratio_valuation_growth_metrics
from finratioanalysis_mcp.tools.historical_valuation_metrics import finratio_historical_valuation_metrics
from finratioanalysis_mcp.tools.z_score import finratio_z_score
from finratioanalysis_mcp.tools.capm import finratio_capm
from finratioanalysis_mcp.tools.wacc import finratio_wacc
from finratioanalysis_mcp.tools.company_snapshot import finratio_company_snapshot

# Test basket: Tech giants, financial, and semiconductor sectors
TEST_BASKET = ["AAPL", "MSFT", "GOOGL", "JPM", "NVDA"]


@pytest.mark.integration
@pytest.mark.slow
class TestLiveIntegration:
    """Integration tests against live Yahoo Finance data."""
    
    def test_finratio_return_ratios_live(self):
        """Test return_ratios tool with live data from test basket."""
        for ticker in TEST_BASKET:
            result = finratio_return_ratios(ticker=ticker, freq="yearly")
            
            # Assert contract compliance
            assert "data" in result
            assert isinstance(result["data"], list)
            assert len(result["data"]) > 0, f"{ticker} returned empty data"
            
            # Assert required fields present
            first_row = result["data"][0]
            assert "date" in first_row
            assert "ROE" in first_row
            assert "ROA" in first_row
            assert "ROIC" in first_row
            
            print(f"✓ {ticker}: {len(result['data'])} periods")
    
    def test_finratio_efficiency_ratios_live(self):
        """Test efficiency_ratios tool with live data from test basket."""
        for ticker in TEST_BASKET:
            result = finratio_efficiency_ratios(ticker=ticker, freq="yearly")
            
            # Some companies may not have all fields (e.g., GOOGL missing Inventory)
            if "code" in result:
                # Error response is acceptable for companies with missing data
                print(f"⚠ {ticker}: {result['code']} - {result.get('details', {}).get('error_type', 'unknown')}")
                continue
            
            assert "data" in result
            assert isinstance(result["data"], list)
            assert len(result["data"]) > 0
            
            first_row = result["data"][0]
            assert "AssetTurnover" in first_row
            
            print(f"✓ {ticker}: efficiency ratios OK")
    
    def test_finratio_leverage_ratios_live(self):
        """Test leverage_ratios tool with live data from test basket."""
        for ticker in TEST_BASKET:
            result = finratio_leverage_ratios(ticker=ticker, freq="yearly")
            
            assert "data" in result
            assert isinstance(result["data"], list)
            assert len(result["data"]) > 0
            
            first_row = result["data"][0]
            assert "DebtEquityRatio" in first_row
            
            print(f"✓ {ticker}: leverage ratios OK")
    
    def test_finratio_liquidity_ratios_live(self):
        """Test liquidity_ratios tool with live data from test basket."""
        for ticker in TEST_BASKET:
            result = finratio_liquidity_ratios(ticker=ticker, freq="yearly")
            
            # Some companies may not have all required fields
            if "code" in result:
                print(f"⚠ {ticker}: {result['code']} - {result.get('details', {}).get('error_type', 'unknown')}")
                continue
            
            assert "data" in result
            assert isinstance(result["data"], list)
            assert len(result["data"]) > 0
            
            first_row = result["data"][0]
            assert "CurrentRatios" in first_row
            
            print(f"✓ {ticker}: liquidity ratios OK")
    
    def test_finratio_ccc_live(self):
        """Test ccc tool with live data from test basket."""
        for ticker in TEST_BASKET:
            result = finratio_ccc(ticker=ticker, freq="yearly")
            
            # CCC requires inventory - not all companies have it
            if "code" in result:
                print(f"⚠ {ticker}: {result['code']} - {result.get('details', {}).get('error_type', 'unknown')}")
                continue
            
            assert "data" in result
            assert isinstance(result["data"], list)
            assert len(result["data"]) > 0
            
            first_row = result["data"][0]
            assert "CCC" in first_row
            assert "DIO" in first_row
            
            print(f"✓ {ticker}: cash conversion cycle OK")
    
    def test_finratio_valuation_growth_metrics_live(self):
        """Test valuation_growth_metrics tool with live data from test basket."""
        for ticker in TEST_BASKET:
            result = finratio_valuation_growth_metrics(ticker=ticker)
            
            # Snapshot tool - wrapped in {'data': {...}}
            assert "data" in result
            data = result["data"]
            assert "Symbol" in data
            assert data["Symbol"] == ticker
            assert "Revenue_Growth_3Y_CAGR" in data or "revenue_cagr_3y" in data
            
            print(f"✓ {ticker}: valuation growth metrics OK")
    
    def test_finratio_historical_valuation_metrics_live(self):
        """Test historical_valuation_metrics tool with live data from test basket."""
        for ticker in TEST_BASKET:
            result = finratio_historical_valuation_metrics(ticker=ticker, freq="yearly")
            
            assert "data" in result
            assert isinstance(result["data"], list)
            assert len(result["data"]) > 0
            
            first_row = result["data"][0]
            assert "PE_Ratio" in first_row
            assert "Market_Cap" in first_row
            
            print(f"✓ {ticker}: historical valuation metrics OK")
    
    def test_finratio_z_score_live(self):
        """Test z_score tool with live data from test basket."""
        for ticker in TEST_BASKET:
            result = finratio_z_score(ticker=ticker)
            
            # Z-Score not applicable to banks - may return error
            if "code" in result:
                print(f"⚠ {ticker}: {result['code']} (Z-Score not applicable to this company type)")
                continue
            
            # Snapshot tool - wrapped in {'data': {...}}
            assert "data" in result
            data = result["data"]
            assert "Symbol" in data
            assert data["Symbol"] == ticker
            assert "Z Score" in data
            assert "Zone" in data
            
            # Z-Score should be numeric (could be null for banks)
            if data["Z Score"] is not None:
                assert isinstance(data["Z Score"], (int, float))
            
            print(f"✓ {ticker}: Z-Score = {data['Z Score']}")
    
    def test_finratio_capm_live(self):
        """Test capm tool with live data from test basket."""
        for ticker in TEST_BASKET:
            result = finratio_capm(ticker=ticker)
            
            # Snapshot tool - wrapped in {'data': {...}}
            assert "data" in result
            data = result["data"]
            assert "Symbol" in data
            assert data["Symbol"] == ticker
            
            # Beta or CAPM should be present
            has_metric = "Beta" in data or "CAPM" in data
            assert has_metric, f"Neither Beta nor CAPM found in {list(data.keys())}"
            
            print(f"✓ {ticker}: CAPM OK")
    
    def test_finratio_wacc_live(self):
        """Test wacc tool with live data from test basket."""
        for ticker in TEST_BASKET:
            result = finratio_wacc(ticker=ticker)
            
            # Snapshot tool - wrapped in {'data': {...}}
            assert "data" in result
            data = result["data"]
            assert "Symbol" in data
            assert data["Symbol"] == ticker
            assert "WACC" in data
            
            # WACC should be numeric (could be null if data missing)
            if data["WACC"] is not None:
                assert isinstance(data["WACC"], (int, float))
            
            print(f"✓ {ticker}: WACC = {data['WACC']}")
    
    def test_finratio_company_snapshot_live(self):
        """Test company_snapshot aggregate tool with live data from test basket."""
        for ticker in TEST_BASKET:
            result = finratio_company_snapshot(ticker=ticker, freq="yearly")
            
            # company_snapshot returns {ticker, freq, sections: {...}}
            assert "sections" in result
            sections = result["sections"]
            
            # All 10 sections should be present
            assert "return_ratios" in sections
            assert "efficiency_ratios" in sections
            assert "leverage_ratios" in sections
            assert "liquidity_ratios" in sections
            assert "ccc" in sections
            assert "valuation_growth_metrics" in sections
            assert "historical_valuation_metrics" in sections
            assert "z_score" in sections
            assert "capm" in sections
            assert "wacc" in sections
            
            # Each section should have status
            for section_name, section_data in sections.items():
                assert "status" in section_data
                assert section_data["status"] in ["ok", "error"]
                
                # If OK, should have data
                if section_data["status"] == "ok":
                    assert "data" in section_data
            
            # Count successful sections
            success_count = sum(1 for s in sections.values() if s["status"] == "ok")
            print(f"✓ {ticker}: company snapshot OK ({success_count}/10 sections successful)")
    
    def test_all_tools_discoverable(self):
        """Verify all 11 tools are discoverable via MCP list_tools."""
        tools = asyncio.run(mcp.list_tools())
        tool_names = [t.name for t in tools]
        
        expected_tools = [
            "finratio_return_ratios",
            "finratio_efficiency_ratios",
            "finratio_leverage_ratios",
            "finratio_liquidity_ratios",
            "finratio_ccc",
            "finratio_valuation_growth_metrics",
            "finratio_historical_valuation_metrics",
            "finratio_z_score",
            "finratio_capm",
            "finratio_wacc",
            "finratio_company_snapshot",
        ]
        
        for expected in expected_tools:
            assert expected in tool_names, f"Tool {expected} not found"
        
        print(f"✓ All 11 tools discoverable")
    
    def test_quarterly_frequency_support(self):
        """Verify quarterly frequency works for time-series tools."""
        # Test quarterly with AAPL
        result = finratio_return_ratios(ticker="AAPL", freq="quarterly")
        
        assert "data" in result
        assert isinstance(result["data"], list)
        assert len(result["data"]) > 0
        
        # Should have more periods than yearly
        yearly_result = finratio_return_ratios(ticker="AAPL", freq="yearly")
        assert len(result["data"]) > len(yearly_result["data"])
        
        print(f"✓ Quarterly frequency: {len(result['data'])} periods vs {len(yearly_result['data'])} yearly")

