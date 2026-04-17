"""Unit tests for company_snapshot partial failure handling (T047).

Partial failure: one or more sections return status="error" while others succeed.
"""

import pytest
from unittest.mock import patch

from finratioanalysis_mcp.errors import ErrorCode, MCPError
from finratioanalysis_mcp.tools.company_snapshot import finratio_company_snapshot


def test_company_snapshot_partial_failure_capm(
    mock_return_ratios_df,
    mock_efficiency_ratios_df,
    mock_leverage_ratios_df,
    mock_liquidity_ratios_df,
    mock_ccc_df,
    mock_historical_valuation_metrics_df,
    mock_valuation_growth_metrics_df,
    mock_z_score_df,
    mock_wacc_df,
):
    """Test company_snapshot when CAPM fails but other sections succeed."""
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        
        # Set up 9 successful methods
        mock_instance.return_ratios.return_value = mock_return_ratios_df
        mock_instance.efficiency_ratios.return_value = mock_efficiency_ratios_df
        mock_instance.leverage_ratios.return_value = mock_leverage_ratios_df
        mock_instance.liquidity_ratios.return_value = mock_liquidity_ratios_df
        mock_instance.ccc.return_value = mock_ccc_df
        mock_instance.historical_valuation_metrics.return_value = mock_historical_valuation_metrics_df
        mock_instance.valuation_growth_metrics.return_value = mock_valuation_growth_metrics_df
        mock_instance.z_score.return_value = mock_z_score_df
        mock_instance.wacc.return_value = mock_wacc_df
        
        # Force CAPM to raise an error (e.g., insufficient price history)
        mock_instance.capm.side_effect = Exception("Insufficient price data for CAPM calculation")
        
        response = finratio_company_snapshot(ticker="AAPL", freq="yearly", response_format="json")
    
    # Assert top-level response structure is intact
    assert "ticker" in response
    assert response["ticker"] == "AAPL"
    assert "sections" in response
    
    # Verify all 10 sections are present (even the failing one)
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
    
    # Verify 9 successful sections have status="ok"
    successful_sections = [
        "return_ratios",
        "efficiency_ratios",
        "leverage_ratios",
        "liquidity_ratios",
        "ccc",
        "historical_valuation_metrics",
        "valuation_growth_metrics",
        "z_score",
        "wacc",
    ]
    for section_name in successful_sections:
        section = response["sections"][section_name]
        assert section["status"] == "ok", f"Section {section_name} should be ok, got {section['status']}"
        assert "data" in section
        assert "error" not in section
    
    # Verify CAPM section has status="error" with proper error structure
    capm_section = response["sections"]["capm"]
    assert capm_section["status"] == "error"
    assert "error" in capm_section
    assert "data" not in capm_section
    
    # Verify error object structure (per data-model.md ErrorResponse)
    error = capm_section["error"]
    assert "code" in error
    assert error["code"] in [
        "INVALID_TICKER",
        "UNSUPPORTED_FREQ",
        "DATA_UNAVAILABLE",
        "UPSTREAM_ERROR",
        "INTERNAL_ERROR",
    ]
    assert "message" in error
    assert isinstance(error["message"], str)
    assert len(error["message"]) > 0


def test_company_snapshot_multiple_failures(
    mock_return_ratios_df,
    mock_efficiency_ratios_df,
    mock_leverage_ratios_df,
    mock_liquidity_ratios_df,
    mock_ccc_df,
    mock_historical_valuation_metrics_df,
    mock_valuation_growth_metrics_df,
):
    """Test company_snapshot when multiple sections fail."""
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        
        # Set up 7 successful methods
        mock_instance.return_ratios.return_value = mock_return_ratios_df
        mock_instance.efficiency_ratios.return_value = mock_efficiency_ratios_df
        mock_instance.leverage_ratios.return_value = mock_leverage_ratios_df
        mock_instance.liquidity_ratios.return_value = mock_liquidity_ratios_df
        mock_instance.ccc.return_value = mock_ccc_df
        mock_instance.historical_valuation_metrics.return_value = mock_historical_valuation_metrics_df
        mock_instance.valuation_growth_metrics.return_value = mock_valuation_growth_metrics_df
        
        # Force 3 methods to fail
        mock_instance.z_score.side_effect = Exception("Z-Score calculation failed")
        mock_instance.capm.side_effect = Exception("CAPM calculation failed")
        mock_instance.wacc.side_effect = Exception("WACC calculation failed")
        
        response = finratio_company_snapshot(ticker="AAPL", freq="yearly", response_format="json")
    
    # Assert 7 sections succeeded
    successful_count = sum(
        1 for section in response["sections"].values() if section["status"] == "ok"
    )
    assert successful_count == 7
    
    # Assert 3 sections failed
    failed_count = sum(
        1 for section in response["sections"].values() if section["status"] == "error"
    )
    assert failed_count == 3
    
    # Verify specific failed sections
    assert response["sections"]["z_score"]["status"] == "error"
    assert response["sections"]["capm"]["status"] == "error"
    assert response["sections"]["wacc"]["status"] == "error"
    
    # Verify specific successful sections
    assert response["sections"]["return_ratios"]["status"] == "ok"
    assert response["sections"]["efficiency_ratios"]["status"] == "ok"


def test_company_snapshot_data_unavailable_error(
    mock_return_ratios_df,
    mock_efficiency_ratios_df,
    mock_leverage_ratios_df,
    mock_liquidity_ratios_df,
    mock_ccc_df,
    mock_historical_valuation_metrics_df,
    mock_valuation_growth_metrics_df,
    mock_z_score_df,
    mock_wacc_df,
):
    """Test company_snapshot when CAPM raises MCPError with DATA_UNAVAILABLE."""
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        mock_instance = MockClass.return_value
        
        # Set up 9 successful methods
        mock_instance.return_ratios.return_value = mock_return_ratios_df
        mock_instance.efficiency_ratios.return_value = mock_efficiency_ratios_df
        mock_instance.leverage_ratios.return_value = mock_leverage_ratios_df
        mock_instance.liquidity_ratios.return_value = mock_liquidity_ratios_df
        mock_instance.ccc.return_value = mock_ccc_df
        mock_instance.historical_valuation_metrics.return_value = mock_historical_valuation_metrics_df
        mock_instance.valuation_growth_metrics.return_value = mock_valuation_growth_metrics_df
        mock_instance.z_score.return_value = mock_z_score_df
        mock_instance.wacc.return_value = mock_wacc_df
        
        # Force CAPM to raise a structured MCPError
        mock_instance.capm.side_effect = MCPError(
            code=ErrorCode.DATA_UNAVAILABLE,
            message="Insufficient price history for CAPM calculation",
            details={"method": "capm"},
        )
        
        response = finratio_company_snapshot(ticker="AAPL", freq="yearly", response_format="json")
    
    # Verify CAPM error is properly structured
    capm_section = response["sections"]["capm"]
    assert capm_section["status"] == "error"
    assert capm_section["error"]["code"] == "DATA_UNAVAILABLE"
    assert "price history" in capm_section["error"]["message"].lower()
    
    # Verify other sections still succeeded
    assert response["sections"]["return_ratios"]["status"] == "ok"
    assert response["sections"]["wacc"]["status"] == "ok"
