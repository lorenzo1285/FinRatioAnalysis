"""Unit tests for company_snapshot tool (T046).

Happy-path: all 10 sections return status="ok" with valid data.
"""

import pytest
from unittest.mock import patch

from finratioanalysis_mcp.tools.company_snapshot import finratio_company_snapshot


def test_company_snapshot_happy_path(
    mock_return_ratios_df,
    mock_efficiency_ratios_df,
    mock_leverage_ratios_df,
    mock_liquidity_ratios_df,
    mock_ccc_df,
    mock_historical_valuation_metrics_df,
    mock_valuation_growth_metrics_df,
    mock_z_score_df,
    mock_capm_df,
    mock_wacc_df,
):
    """Test successful company_snapshot call with all sections succeeding."""
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        mock_instance.return_ratios.return_value = mock_return_ratios_df
        mock_instance.efficiency_ratios.return_value = mock_efficiency_ratios_df
        mock_instance.leverage_ratios.return_value = mock_leverage_ratios_df
        mock_instance.liquidity_ratios.return_value = mock_liquidity_ratios_df
        mock_instance.ccc.return_value = mock_ccc_df
        mock_instance.historical_valuation_metrics.return_value = mock_historical_valuation_metrics_df
        mock_instance.valuation_growth_metrics.return_value = mock_valuation_growth_metrics_df
        mock_instance.z_score.return_value = mock_z_score_df
        mock_instance.capm.return_value = mock_capm_df
        mock_instance.wacc.return_value = mock_wacc_df
        
        response = finratio_company_snapshot(ticker="AAPL", freq="yearly", response_format="json")
    
    # Assert top-level response structure
    assert "ticker" in response
    assert response["ticker"] == "AAPL"
    assert "freq" in response
    assert response["freq"] == "yearly"
    assert "sections" in response
    assert isinstance(response["sections"], dict)
    
    # Verify all 10 sections are present
    expected_sections = [
        "return_ratios",
        "efficiency_ratios",
        "leverage_ratios",
        "liquidity_ratios",
        "ccc",
        "historical_valuation_metrics",
        "valuation_growth_metrics",
        "z_score",
        "capm",
        "wacc",
    ]
    for section_name in expected_sections:
        assert section_name in response["sections"], f"Missing section: {section_name}"
    
    # Verify each section has status="ok" and valid data
    # Time-series sections (return list of period rows)
    for section_name in [
        "return_ratios",
        "efficiency_ratios",
        "leverage_ratios",
        "liquidity_ratios",
        "ccc",
        "historical_valuation_metrics",
    ]:
        section = response["sections"][section_name]
        assert section["status"] == "ok", f"Section {section_name} not ok"
        assert "data" in section
        assert isinstance(section["data"], list)
        assert len(section["data"]) > 0
        assert "date" in section["data"][0]
    
    # Snapshot sections (return single object)
    for section_name in [
        "valuation_growth_metrics",
        "z_score",
        "capm",
        "wacc",
    ]:
        section = response["sections"][section_name]
        assert section["status"] == "ok", f"Section {section_name} not ok"
        assert "data" in section
        assert isinstance(section["data"], dict)
        assert "Symbol" in section["data"]


def test_company_snapshot_quarterly_freq(
    mock_return_ratios_df,
    mock_efficiency_ratios_df,
    mock_leverage_ratios_df,
    mock_liquidity_ratios_df,
    mock_ccc_df,
    mock_historical_valuation_metrics_df,
    mock_valuation_growth_metrics_df,
    mock_z_score_df,
    mock_capm_df,
    mock_wacc_df,
):
    """Test company_snapshot with quarterly frequency."""
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        mock_instance.return_ratios.return_value = mock_return_ratios_df
        mock_instance.efficiency_ratios.return_value = mock_efficiency_ratios_df
        mock_instance.leverage_ratios.return_value = mock_leverage_ratios_df
        mock_instance.liquidity_ratios.return_value = mock_liquidity_ratios_df
        mock_instance.ccc.return_value = mock_ccc_df
        mock_instance.historical_valuation_metrics.return_value = mock_historical_valuation_metrics_df
        mock_instance.valuation_growth_metrics.return_value = mock_valuation_growth_metrics_df
        mock_instance.z_score.return_value = mock_z_score_df
        mock_instance.capm.return_value = mock_capm_df
        mock_instance.wacc.return_value = mock_wacc_df
        
        response = finratio_company_snapshot(ticker="MSFT", freq="quarterly", response_format="json")
    
    assert response["ticker"] == "MSFT"
    assert response["freq"] == "quarterly"
    assert "sections" in response


def test_company_snapshot_validates_contract_shape(
    mock_return_ratios_df,
    mock_efficiency_ratios_df,
    mock_leverage_ratios_df,
    mock_liquidity_ratios_df,
    mock_ccc_df,
    mock_historical_valuation_metrics_df,
    mock_valuation_growth_metrics_df,
    mock_z_score_df,
    mock_capm_df,
    mock_wacc_df,
):
    """Test company_snapshot response matches expected contract shape."""
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        mock_instance.return_ratios.return_value = mock_return_ratios_df
        mock_instance.efficiency_ratios.return_value = mock_efficiency_ratios_df
        mock_instance.leverage_ratios.return_value = mock_leverage_ratios_df
        mock_instance.liquidity_ratios.return_value = mock_liquidity_ratios_df
        mock_instance.ccc.return_value = mock_ccc_df
        mock_instance.historical_valuation_metrics.return_value = mock_historical_valuation_metrics_df
        mock_instance.valuation_growth_metrics.return_value = mock_valuation_growth_metrics_df
        mock_instance.z_score.return_value = mock_z_score_df
        mock_instance.capm.return_value = mock_capm_df
        mock_instance.wacc.return_value = mock_wacc_df
        
        response = finratio_company_snapshot(ticker="AAPL", freq="yearly", response_format="json")
    
    # Verify each section matches the per-method contract shape
    # Per data-model.md, each section has either:
    # - {"status": "ok", "data": [...]} for time-series
    # - {"status": "ok", "data": {...}} for snapshots
    # - {"status": "error", "error": {...}} for failures
    
    for section_name, section_data in response["sections"].items():
        assert "status" in section_data
        if section_data["status"] == "ok":
            assert "data" in section_data
            assert "error" not in section_data
        elif section_data["status"] == "error":
            assert "error" in section_data
            assert "data" not in section_data
