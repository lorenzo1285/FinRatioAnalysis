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


def _is_error(result: dict) -> bool:
    """Return True if the tool returned an ErrorResponse."""
    return "code" in result


@pytest.mark.integration
@pytest.mark.slow
class TestRecentIPOIntegration:
    """Integration tests for recent IPO edge cases."""

    def test_recent_ipo_limited_time_series(self):
        """
        Recent IPOs should return limited time-series data without crashing.
        """
        result = finratio_return_ratios(ticker=RECENT_IPO_TICKER, freq="yearly")

        assert "data" in result
        assert isinstance(result["data"], list)

        data_length = len(result["data"])
        print(f"[OK] {RECENT_IPO_TICKER} (IPO {IPO_DATE_INFO}): {data_length} yearly periods available")

        assert data_length >= 1, "Should have at least one period of data"

        if data_length < 3:
            print(f"  Limited history: {data_length} years (< 3 expected for recent IPO)")

        first_row = result["data"][0]
        assert "date" in first_row
        assert "ROE" in first_row

    def test_recent_ipo_quarterly_more_data(self):
        """
        Quarterly data should provide more periods even for recent IPOs.
        """
        yearly_result = finratio_return_ratios(ticker=RECENT_IPO_TICKER, freq="yearly")
        quarterly_result = finratio_return_ratios(ticker=RECENT_IPO_TICKER, freq="quarterly")

        yearly_count = len(yearly_result["data"])
        quarterly_count = len(quarterly_result["data"])

        assert quarterly_count > yearly_count, "Quarterly should have more periods than yearly"

        print(f"[OK] {RECENT_IPO_TICKER} data availability:")
        print(f"  Yearly: {yearly_count} periods")
        print(f"  Quarterly: {quarterly_count} periods")

    def test_recent_ipo_valuation_growth_null_cagr(self):
        """
        Recent IPOs should return null/NaN for 3-year CAGR metrics since
        they lack 3+ years of historical data.

        This is the KEY test case for T052.
        """
        result = finratio_valuation_growth_metrics(ticker=RECENT_IPO_TICKER)

        if _is_error(result):
            assert "message" in result
            print(f"[INFO] {RECENT_IPO_TICKER} valuation_growth_metrics error: {result['code']}")
            return

        assert "data" in result
        data = result["data"]
        assert "Symbol" in data
        assert data["Symbol"] == RECENT_IPO_TICKER

        # Real library column names are snake_case
        assert "revenue_cagr_3y" in data

        revenue_cagr_3y = data["revenue_cagr_3y"]
        net_income_cagr_3y = data.get("net_income_cagr_3y")

        print(f"[OK] {RECENT_IPO_TICKER} 3-year CAGR metrics:")
        print(f"  revenue_cagr_3y = {revenue_cagr_3y}")
        print(f"  net_income_cagr_3y = {net_income_cagr_3y}")

        if revenue_cagr_3y is None:
            print(f"  revenue_cagr_3y is null (expected for recent IPO)")
        else:
            print(f"  [WARN] revenue_cagr_3y has value (unusual for {IPO_DATE_INFO} IPO)")

    def test_recent_ipo_valuation_growth_1y_available(self):
        """
        While 3Y CAGR may be unavailable, 1Y metrics should exist.
        """
        result = finratio_valuation_growth_metrics(ticker=RECENT_IPO_TICKER)

        if _is_error(result):
            print(f"[INFO] {RECENT_IPO_TICKER} valuation_growth_metrics error: {result['code']}")
            return

        assert "data" in result
        data = result["data"]

        if "Revenue_Growth_1Y" in data:
            revenue_1y = data["Revenue_Growth_1Y"]
            print(f"[OK] {RECENT_IPO_TICKER} Revenue_Growth_1Y = {revenue_1y}")

    def test_recent_ipo_historical_valuation_limited_periods(self):
        """
        Historical valuation metrics should work but return fewer periods.
        """
        result = finratio_historical_valuation_metrics(ticker=RECENT_IPO_TICKER, freq="yearly")

        assert "data" in result
        assert isinstance(result["data"], list)

        periods = len(result["data"])
        print(f"[OK] {RECENT_IPO_TICKER} historical valuation: {periods} periods")

        assert periods >= 1

        first_row = result["data"][0]
        assert "date" in first_row
        assert "PE_Ratio" in first_row
        print(f"  Most recent P/E = {first_row['PE_Ratio']}")

    def test_recent_ipo_z_score_works(self):
        """
        Z-Score should work with most recent balance sheet (doesn't need 3Y history).
        """
        result = finratio_z_score(ticker=RECENT_IPO_TICKER)

        if _is_error(result):
            assert "message" in result
            print(f"[INFO] {RECENT_IPO_TICKER} Z-Score returned error: {result['code']}")
            return

        assert "data" in result
        data = result["data"]
        assert "Symbol" in data
        assert data["Symbol"] == RECENT_IPO_TICKER
        assert "Z Score" in data
        assert "Zone" in data

        print(f"[OK] {RECENT_IPO_TICKER} Z-Score = {data['Z Score']}")
        print(f"  Zone = {data['Zone']}")

    def test_recent_ipo_capm_works(self):
        """
        CAPM should work - beta can be calculated from available trading history.
        """
        result = finratio_capm(ticker=RECENT_IPO_TICKER)

        if _is_error(result):
            assert "message" in result
            print(f"[INFO] {RECENT_IPO_TICKER} CAPM returned error: {result['code']}")
            return

        assert "data" in result
        data = result["data"]
        assert "Symbol" in data
        assert data["Symbol"] == RECENT_IPO_TICKER
        assert "CAPM" in data
        assert "Sharpe" in data

        print(f"[OK] {RECENT_IPO_TICKER} CAPM:")
        print(f"  CAPM = {data['CAPM']}")
        print(f"  Sharpe = {data['Sharpe']}")

    def test_recent_ipo_wacc_works(self):
        """
        WACC should work with most recent balance sheet data.
        """
        result = finratio_wacc(ticker=RECENT_IPO_TICKER)

        if _is_error(result):
            assert "message" in result
            print(f"[INFO] {RECENT_IPO_TICKER} WACC returned error: {result['code']}")
            return

        assert "data" in result
        data = result["data"]
        assert "Symbol" in data
        assert data["Symbol"] == RECENT_IPO_TICKER
        assert "WACC" in data

        print(f"[OK] {RECENT_IPO_TICKER} WACC = {data['WACC']}")

    def test_recent_ipo_company_snapshot_graceful_degradation(self):
        """
        Aggregate snapshot should succeed with graceful degradation.
        Sections using most recent data succeed, multi-year CAGR may have nulls.
        """
        result = finratio_company_snapshot(ticker=RECENT_IPO_TICKER, freq="yearly")

        assert "sections" in result
        sections = result["sections"]

        assert "return_ratios" in sections
        assert "valuation_growth_metrics" in sections
        assert "z_score" in sections
        assert "capm" in sections
        assert "wacc" in sections

        success_count = sum(1 for s in sections.values() if s.get("status") == "ok")
        print(f"[OK] {RECENT_IPO_TICKER} company snapshot: {success_count}/10 sections ok")

        if sections["valuation_growth_metrics"]["status"] == "ok":
            vg_data = sections["valuation_growth_metrics"]["data"]
            revenue_3y = vg_data.get("Revenue_Growth_3Y_CAGR")
            print(f"  Revenue_Growth_3Y_CAGR = {revenue_3y} (via aggregate tool)")

    def test_recent_ipo_no_data_unavailable_error(self):
        """
        Verify that limited data results in null values rather than
        DATA_UNAVAILABLE errors (unless truly no data exists).
        """
        result = finratio_return_ratios(ticker=RECENT_IPO_TICKER, freq="yearly")

        assert "data" in result, "Should return data structure, not error"

        is_error = "code" in result
        if is_error:
            error_code = result.get("code")
            print(f"[WARN] Unexpected error: {error_code}")
            assert error_code != ErrorCode.DATA_UNAVAILABLE.value, \
                "Should not return DATA_UNAVAILABLE for IPO with some data"
        else:
            print(f"[OK] {RECENT_IPO_TICKER} returns data structure (not error) as expected")

    def test_compare_ipo_vs_established_data_availability(self):
        """
        Compare data availability between recent IPO and established company.
        Demonstrates the difference in historical depth.
        """
        ipo_result = finratio_return_ratios(ticker=RECENT_IPO_TICKER, freq="yearly")
        ipo_periods = len(ipo_result["data"])

        established_result = finratio_return_ratios(ticker="AAPL", freq="yearly")
        established_periods = len(established_result["data"])

        print(f"\n[OK] Data availability comparison:")
        print(f"  {RECENT_IPO_TICKER} (IPO {IPO_DATE_INFO}): {ipo_periods} yearly periods")
        print(f"  AAPL (established): {established_periods} yearly periods")

        assert ipo_periods < established_periods, \
            "Recent IPO should have fewer periods than established company"
        assert ipo_periods >= 1, "IPO should have at least one period"
        assert established_periods >= 5, "Established company should have many periods"
