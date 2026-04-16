"""T038: Parametrized tests for markdown format output across all tools.

This test suite verifies that all tools honor the response_format="markdown"
parameter per FR-013, producing well-formed markdown output containing the
expected column headers.
"""

import pytest
from unittest.mock import patch

from finratioanalysis_mcp.tools.return_ratios import finratio_return_ratios
from finratioanalysis_mcp.tools.efficiency_ratios import finratio_efficiency_ratios
from finratioanalysis_mcp.tools.leverage_ratios import finratio_leverage_ratios
from finratioanalysis_mcp.tools.liquidity_ratios import finratio_liquidity_ratios
from finratioanalysis_mcp.tools.ccc import finratio_ccc
from finratioanalysis_mcp.tools.historical_valuation_metrics import finratio_historical_valuation_metrics
from finratioanalysis_mcp.tools.valuation_growth_metrics import finratio_valuation_growth_metrics
from finratioanalysis_mcp.tools.z_score import finratio_z_score
from finratioanalysis_mcp.tools.capm import finratio_capm
from finratioanalysis_mcp.tools.wacc import finratio_wacc


# Time-series tools return markdown tables with | separators
TIME_SERIES_TOOLS = [
    (
        "return_ratios",
        finratio_return_ratios,
        ["date", "ROE", "ROA", "ROCE", "ROIC", "GrossMargin", "OperatingMargin", "NetProfit"],
        "mock_return_ratios_df"
    ),
    (
        "efficiency_ratios",
        finratio_efficiency_ratios,
        ["date", "AssetTurnover", "ReceivableTurnover", "InventoryTurnover", "FixedAssetTurnover", "FCF_Margin", "ReinvestmentRate"],
        "mock_efficiency_ratios_df"
    ),
    (
        "leverage_ratios",
        finratio_leverage_ratios,
        ["date", "DebtEquityRatio", "EquityRatio", "DebtRatio"],
        "mock_leverage_ratios_df"
    ),
    (
        "liquidity_ratios",
        finratio_liquidity_ratios,
        ["date", "CurrentRatios", "QuickRatio", "CashRatio", "DIR", "TIE", "TIE_CB", "CAPEX_OpCash", "OpCashFlow"],
        "mock_liquidity_ratios_df"
    ),
    (
        "ccc",
        finratio_ccc,
        ["date", "DIO", "DSO", "DPO", "CCC"],
        "mock_ccc_df"
    ),
    (
        "historical_valuation_metrics",
        finratio_historical_valuation_metrics,
        ["date", "Market_Cap", "PE_Ratio", "EV_EBITDA", "FCF_Yield"],
        "mock_historical_valuation_metrics_df"
    ),
]

# Snapshot tools return markdown key-value lists
SNAPSHOT_TOOLS = [
    (
        "valuation_growth_metrics",
        finratio_valuation_growth_metrics,
        ["Symbol", "dividend_yield", "payout_ratio", "pe_ratio", "forward_pe", "ps_ratio", "beta", "ev_ebitda", "fcf_yield", "revenue_cagr_3y", "net_income_cagr_3y"],
        "mock_valuation_growth_metrics_df"
    ),
    (
        "z_score",
        finratio_z_score,
        ["Symbol", "Z Score", "Zone"],
        "mock_z_score_df"
    ),
    (
        "capm",
        finratio_capm,
        ["Symbol", "CAPM", "Sharpe"],
        "mock_capm_df"
    ),
    (
        "wacc",
        finratio_wacc,
        ["Symbol", "WACC"],
        "mock_wacc_df"
    ),
]


@pytest.mark.parametrize("tool_name,tool_func,expected_headers,fixture_name", TIME_SERIES_TOOLS, ids=[t[0] for t in TIME_SERIES_TOOLS])
def test_timeseries_markdown_format(tool_name, tool_func, expected_headers, fixture_name, request):
    """Test that time-series tools produce well-formed markdown tables.
    
    Verifies:
    - Response contains 'data' key with string value
    - Output contains markdown table separators (|)
    - All expected column headers are present
    """
    # Get the fixture by name
    mock_df = request.getfixturevalue(fixture_name)
    
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        setattr(mock_instance, tool_name, lambda: mock_df)
        
        response = tool_func(ticker="AAPL", freq="yearly", response_format="markdown")
    
    # Assert response structure
    assert "data" in response, f"{tool_name}: Missing 'data' key in response"
    assert isinstance(response["data"], str), f"{tool_name}: 'data' should be a string for markdown format"
    assert len(response["data"]) > 0, f"{tool_name}: Markdown output is empty"
    
    # Verify markdown table format
    assert "|" in response["data"], f"{tool_name}: Markdown output missing table separator '|'"
    
    # Verify all expected headers are present
    markdown_output = response["data"]
    for header in expected_headers:
        assert header in markdown_output, f"{tool_name}: Missing expected header '{header}' in markdown output"


@pytest.mark.parametrize("tool_name,tool_func,expected_keys,fixture_name", SNAPSHOT_TOOLS, ids=[t[0] for t in SNAPSHOT_TOOLS])
def test_snapshot_markdown_format(tool_name, tool_func, expected_keys, fixture_name, request):
    """Test that snapshot tools produce well-formed markdown key-value lists.
    
    Verifies:
    - Response contains 'data' key with string value
    - Output is non-empty
    - All expected keys are present
    """
    # Get the fixture by name
    mock_df = request.getfixturevalue(fixture_name)
    
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        setattr(mock_instance, tool_name, lambda: mock_df)
        
        response = tool_func(ticker="AAPL", freq="yearly", response_format="markdown")
    
    # Assert response structure
    assert "data" in response, f"{tool_name}: Missing 'data' key in response"
    assert isinstance(response["data"], str), f"{tool_name}: 'data' should be a string for markdown format"
    assert len(response["data"]) > 0, f"{tool_name}: Markdown output is empty"
    
    # Verify all expected keys are present in the markdown output
    markdown_output = response["data"]
    for key in expected_keys:
        assert key in markdown_output, f"{tool_name}: Missing expected key '{key}' in markdown output"


def test_all_tools_covered():
    """Sanity check: verify we're testing all 10 US1 tools."""
    total_tools = len(TIME_SERIES_TOOLS) + len(SNAPSHOT_TOOLS)
    assert total_tools == 10, f"Expected 10 tools, but have {total_tools} defined in test parameters"
