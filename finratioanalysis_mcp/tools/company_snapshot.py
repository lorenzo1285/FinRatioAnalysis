"""T048: Company Snapshot tool.

Aggregate one-call fundamentals snapshot returning all 10 ratio families
with per-section partial success handling.
"""

from typing import Any, Dict

from finratioanalysis_mcp.adapters import df_to_period_rows, df_to_snapshot
from finratioanalysis_mcp.errors import MCPError, error_response
from finratioanalysis_mcp.models import parse_request
from finratioanalysis_mcp.server import _call_library, mcp


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
def finratio_company_snapshot(
    ticker: str,
    freq: str = "yearly",
    response_format: str = "json",
) -> Dict[str, Any]:
    """Aggregate one-call fundamentals snapshot: returns every ratio family in a single response.
    
    Returns all 10 ratio families (return, efficiency, leverage, liquidity, ccc, 
    valuation_growth, historical_valuation, z_score, capm, wacc) for a ticker.
    Sections that fail individually report a per-section error without aborting 
    the whole response.
    
    Args:
        ticker: Upper-case ticker symbol (e.g., AAPL, BRK-B).
        freq: Reporting frequency - 'yearly' or 'quarterly' (default: yearly).
        response_format: Output format - 'json' or 'markdown' (default: json).
    
    Returns:
        Dictionary with 'ticker', 'freq', and 'sections' containing all ratio families.
        Each section has either {"status": "ok", "data": ...} or 
        {"status": "error", "error": {...}}.
    
    Error Codes (per-section):
        INVALID_TICKER: Ticker format invalid (must match [A-Z0-9.\\-]+)
        UNSUPPORTED_FREQ: Frequency not 'yearly' or 'quarterly'
        DATA_UNAVAILABLE: No data returned for this ticker/frequency
        UPSTREAM_ERROR: Network/connection issue with Yahoo Finance
        INTERNAL_ERROR: Unexpected error during processing
    """
    try:
        # Validate input via Pydantic model
        request = parse_request(
            ticker=ticker,
            freq=freq,  # type: ignore
            response_format=response_format,  # type: ignore
        )
    except Exception as e:
        # Input validation failure — this is a top-level error, not per-section
        if isinstance(e, MCPError):
            return error_response(e)
        # Pydantic validation errors or other unexpected issues
        return error_response(
            MCPError(
                code="INTERNAL_ERROR",  # type: ignore
                message=f"Invalid request: {str(e)}",
                details={"error": str(e)},
            )
        )
    
    # Define all 10 sections with their method names and data shape types
    # Time-series methods return lists, snapshots return single objects
    sections_config = [
        ("return_ratios", "return_ratios", "timeseries"),
        ("efficiency_ratios", "efficiency_ratios", "timeseries"),
        ("leverage_ratios", "leverage_ratios", "timeseries"),
        ("liquidity_ratios", "liquidity_ratios", "timeseries"),
        ("ccc", "ccc", "timeseries"),
        ("historical_valuation_metrics", "historical_valuation_metrics", "timeseries"),
        ("valuation_growth_metrics", "valuation_growth_metrics", "snapshot"),
        ("z_score", "z_score", "snapshot"),
        ("capm", "capm", "snapshot"),
        ("wacc", "wacc", "snapshot"),
    ]
    
    sections: Dict[str, Dict[str, Any]] = {}
    
    # Call each method and populate sections with either data or error
    for section_name, method_name, shape_type in sections_config:
        try:
            # Call library method through the shared dispatcher
            df = _call_library(
                ticker=request.ticker,
                freq=request.freq,
                method_name=method_name,
            )
            
            # Serialize based on shape type
            if shape_type == "timeseries":
                data = df_to_period_rows(df)
            else:  # snapshot
                data = df_to_snapshot(df)
                
                # SPECIAL CASE: valuation_growth_metrics is the only snapshot
                # method that doesn't include Symbol in its DataFrame. Inject it
                # to maintain uniform snapshot shape across all sections.
                # (See T022 note in tasks.md and valuation_growth_metrics.py)
                if section_name == "valuation_growth_metrics":
                    data = {"Symbol": request.ticker, **data}
            
            # Successful section
            sections[section_name] = {
                "status": "ok",
                "data": data,
            }
        
        except MCPError as e:
            # Structured error from _call_library or adapters
            sections[section_name] = {
                "status": "error",
                "error": error_response(e),
            }
        
        except Exception as e:
            # Unexpected error — wrap as INTERNAL_ERROR per FR-006
            # (Never leak stack traces to client)
            sections[section_name] = {
                "status": "error",
                "error": error_response(
                    MCPError(
                        code="INTERNAL_ERROR",  # type: ignore
                        message=f"Failed to compute {section_name}",
                        details={"method": method_name, "error_type": type(e).__name__},
                    )
                ),
            }
    
    # Build top-level response
    response: Dict[str, Any] = {
        "ticker": request.ticker,
        "freq": request.freq,
        "sections": sections,
    }
    
    # Handle markdown format (if requested)
    # Note: For company_snapshot, markdown is complex — we keep JSON structure
    # but this could be enhanced in future to generate a formatted report
    if request.response_format == "markdown":
        # For now, markdown format for company_snapshot returns the same JSON
        # structure. A future enhancement could generate a formatted multi-section
        # markdown report, but that's beyond Phase 5 scope.
        pass
    
    return response
