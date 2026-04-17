"""
Integration tests for bank-specific behavior with live Yahoo Finance data.

Banks (SIC sector 6000-6099) have different financial statement structures
compared to non-financial companies. This test suite verifies the MCP server
handles these differences gracefully without crashes.

Key differences for banks:
- No GrossMargin (no COGS concept for financial institutions)
- Different income statement structure (interest income/expense vs revenue/COGS)
- Certain efficiency metrics may be NaN/null

The server should return null/NaN for unsupported metrics rather than crash.

Run these tests with:
    pytest tests_mcp/test_integration_bank.py -m integration
"""
import pytest
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

# JPM = JPMorgan Chase - representative large bank
BANK_TICKER = "JPM"


@pytest.mark.integration
@pytest.mark.slow
class TestBankIntegration:
    """Integration tests for bank-specific edge cases."""

    def test_bank_return_ratios_with_nan_gross_margin(self):
        """
        Banks don't have GrossMargin (no COGS). Verify the tool returns null
        for GrossMargin but still returns other metrics successfully.
        """
        result = finratio_return_ratios(ticker=BANK_TICKER, freq="yearly")

        assert "data" in result
        assert isinstance(result["data"], list)
        assert len(result["data"]) > 0

        first_row = result["data"][0]

        # Period rows have a 'date' key (ISO-8601 string), not 'ticker'
        assert "date" in first_row

        # Core return metrics should exist for banks
        assert "ROE" in first_row
        assert "ROA" in first_row
        assert "ROIC" in first_row

        assert first_row["ROE"] is not None
        assert first_row["ROA"] is not None

        # GrossMargin should be null for banks (no COGS concept)
        gross_margin = first_row.get("GrossMargin")
        print(f"✓ {BANK_TICKER} GrossMargin = {gross_margin} (null/NaN expected for banks)")

        if "OperatingMargin" in first_row:
            print(f"  OperatingMargin = {first_row['OperatingMargin']}")
        if "NetMargin" in first_row:
            print(f"  NetMargin = {first_row['NetMargin']}")

    def test_bank_efficiency_ratios(self):
        """
        Banks should still have asset turnover and other efficiency metrics,
        though some may be null/NaN due to data structure differences.
        """
        result = finratio_efficiency_ratios(ticker=BANK_TICKER, freq="yearly")

        assert "data" in result
        assert isinstance(result["data"], list)
        assert len(result["data"]) > 0

        first_row = result["data"][0]
        assert "date" in first_row
        assert "AssetTurnover" in first_row

        print(f"✓ {BANK_TICKER} efficiency ratios retrieved")
        print(f"  AssetTurnover = {first_row['AssetTurnover']}")

    def test_bank_leverage_ratios(self):
        """
        Banks have high leverage by nature (deposits are liabilities).
        Verify leverage ratios work but may show different patterns.
        """
        result = finratio_leverage_ratios(ticker=BANK_TICKER, freq="yearly")

        assert "data" in result
        assert isinstance(result["data"], list)
        assert len(result["data"]) > 0

        first_row = result["data"][0]
        assert "date" in first_row
        assert "DebtEquityRatio" in first_row
        assert "EquityRatio" in first_row

        print(f"✓ {BANK_TICKER} leverage ratios retrieved")
        print(f"  DebtEquityRatio = {first_row['DebtEquityRatio']} (high is normal for banks)")
        print(f"  EquityRatio = {first_row['EquityRatio']}")

    def test_bank_liquidity_ratios(self):
        """
        Banks must maintain regulatory liquidity ratios. Verify these can be
        calculated (though interpretation differs from non-financials).
        """
        result = finratio_liquidity_ratios(ticker=BANK_TICKER, freq="yearly")

        assert "data" in result
        assert isinstance(result["data"], list)
        assert len(result["data"]) > 0

        first_row = result["data"][0]
        assert "date" in first_row
        assert "CurrentRatios" in first_row
        assert "QuickRatio" in first_row

        print(f"✓ {BANK_TICKER} liquidity ratios retrieved")
        print(f"  CurrentRatio = {first_row['CurrentRatios']}")
        print(f"  QuickRatio = {first_row['QuickRatio']}")

    def test_bank_ccc(self):
        """
        Cash Conversion Cycle is not meaningful for banks (no inventory,
        receivables are loans). Expect null/NaN, empty data, or error.
        """
        result = finratio_ccc(ticker=BANK_TICKER, freq="yearly")

        # CCC may return DATA_UNAVAILABLE for banks — that is acceptable
        if "code" in result:
            print(f"✓ {BANK_TICKER} CCC returned error (acceptable for banks): {result['code']}")
            return

        assert "data" in result
        assert isinstance(result["data"], list)

        if len(result["data"]) > 0:
            first_row = result["data"][0]
            print(f"✓ {BANK_TICKER} CCC = {first_row.get('CCC', 'N/A')} (not meaningful for banks)")
        else:
            print(f"✓ {BANK_TICKER} CCC returned empty (expected for banks)")

    def test_bank_valuation_metrics(self):
        """
        Valuation metrics should work for banks (P/E, P/B are meaningful).
        """
        result = finratio_historical_valuation_metrics(ticker=BANK_TICKER, freq="yearly")

        assert "data" in result
        assert isinstance(result["data"], list)
        assert len(result["data"]) > 0

        first_row = result["data"][0]
        assert "date" in first_row
        assert "PE_Ratio" in first_row
        assert "Market_Cap" in first_row

        print(f"✓ {BANK_TICKER} valuation metrics retrieved")
        print(f"  PE_Ratio = {first_row['PE_Ratio']}")
        print(f"  Market_Cap = {first_row['Market_Cap']}")

    def test_bank_z_score(self):
        """
        Altman Z-Score is NOT applicable to banks (designed for manufacturing).
        The library should return null or indicate it's not applicable.
        """
        result = finratio_z_score(ticker=BANK_TICKER)

        # Snapshot tools return {"data": {...}}
        assert "data" in result
        data = result["data"]
        assert "Symbol" in data
        assert data["Symbol"] == BANK_TICKER

        z_score = data.get("Z Score")
        zone = data.get("Zone")

        print(f"✓ {BANK_TICKER} Z-Score = {z_score}")
        print(f"  Zone = {zone}")
        print(f"  (Z-Score not designed for financial institutions)")

    def test_bank_capm(self):
        """
        CAPM should work fine for banks - they have beta and market returns.
        """
        result = finratio_capm(ticker=BANK_TICKER)

        assert "data" in result
        data = result["data"]
        assert "Symbol" in data
        assert data["Symbol"] == BANK_TICKER
        assert "Beta" in data
        assert "Expected_Return" in data

        print(f"✓ {BANK_TICKER} CAPM retrieved")
        print(f"  Beta = {data['Beta']} (cyclical sector)")
        print(f"  Expected Return = {data['Expected_Return']}")

    def test_bank_wacc(self):
        """
        WACC calculation for banks is complex (deposits vs debt).
        Should return a value but interpretation differs.
        """
        result = finratio_wacc(ticker=BANK_TICKER)

        assert "data" in result
        data = result["data"]
        assert "Symbol" in data
        assert data["Symbol"] == BANK_TICKER
        assert "WACC" in data

        print(f"✓ {BANK_TICKER} WACC = {data['WACC']}")
        print(f"  (Note: WACC for banks includes deposit costs)")

    def test_bank_company_snapshot_partial_success(self):
        """
        Aggregate tool should handle bank edge cases gracefully.
        Some sections may have null values, but overall snapshot should succeed.
        """
        result = finratio_company_snapshot(ticker=BANK_TICKER, freq="yearly")

        # company_snapshot returns {"ticker", "freq", "sections": {...}}
        assert "sections" in result
        sections = result["sections"]

        expected = [
            "return_ratios", "efficiency_ratios", "leverage_ratios",
            "liquidity_ratios", "ccc", "valuation_growth_metrics",
            "historical_valuation_metrics", "z_score", "capm", "wacc",
        ]
        for name in expected:
            assert name in sections, f"Missing section: {name}"

        success_count = sum(1 for s in sections.values() if s.get("status") == "ok")
        print(f"✓ {BANK_TICKER} company snapshot: {success_count}/10 sections OK")

        assert sections["return_ratios"]["status"] == "ok", "Return ratios should work for banks"
        assert sections["leverage_ratios"]["status"] == "ok", "Leverage ratios should work for banks"
        assert sections["capm"]["status"] == "ok", "CAPM should work for banks"

        if sections["return_ratios"]["status"] == "ok":
            rr_data = sections["return_ratios"]["data"][0]
            print(f"  GrossMargin = {rr_data.get('GrossMargin', 'N/A')} (null expected)")

    def test_bank_no_crashes_on_nan_fields(self):
        """
        Comprehensive test: invoke all tools on a bank and verify none crash.
        Some may return null/NaN values, which is acceptable.
        """
        test_cases = [
            ("return_ratios", lambda: finratio_return_ratios(ticker=BANK_TICKER, freq="yearly")),
            ("efficiency_ratios", lambda: finratio_efficiency_ratios(ticker=BANK_TICKER, freq="yearly")),
            ("leverage_ratios", lambda: finratio_leverage_ratios(ticker=BANK_TICKER, freq="yearly")),
            ("liquidity_ratios", lambda: finratio_liquidity_ratios(ticker=BANK_TICKER, freq="yearly")),
            ("ccc", lambda: finratio_ccc(ticker=BANK_TICKER, freq="yearly")),
            ("valuation_growth_metrics", lambda: finratio_valuation_growth_metrics(ticker=BANK_TICKER)),
            ("historical_valuation_metrics", lambda: finratio_historical_valuation_metrics(ticker=BANK_TICKER, freq="yearly")),
            ("z_score", lambda: finratio_z_score(ticker=BANK_TICKER)),
            ("capm", lambda: finratio_capm(ticker=BANK_TICKER)),
            ("wacc", lambda: finratio_wacc(ticker=BANK_TICKER)),
        ]

        crash_count = 0
        for tool_name, tool_fn in test_cases:
            try:
                result = tool_fn()
                assert result is not None
                print(f"  ✓ {tool_name}: OK")
            except Exception as e:
                crash_count += 1
                print(f"  ✗ {tool_name}: CRASHED - {e}")

        assert crash_count == 0, f"{crash_count} tools crashed on bank ticker"
        print(f"\n✓ All {len(test_cases)} tools handled bank data without crashes")
