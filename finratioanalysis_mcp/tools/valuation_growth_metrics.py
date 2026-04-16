"""T022: Valuation & Growth Metrics tool.

Exposes FinRatioAnalysis.valuation_growth_metrics() as an MCP tool.

NOTE (Option B shim): The library's `valuation_growth_metrics()` is the only
snapshot method that does NOT include a `Symbol` column in its output (every
sibling snapshot method — z_score, capm, wacc — does). To give the LLM a
uniform snapshot shape where every response carries its source ticker, this
adapter injects `Symbol` as the first field of the response. Remove this shim
if/when the library is fixed upstream to include Symbol natively.
"""

from typing import Any, Dict

from finratioanalysis_mcp.adapters import df_to_snapshot, to_markdown_kv
from finratioanalysis_mcp.errors import MCPError, error_response
from finratioanalysis_mcp.models import TickerRequest
from finratioanalysis_mcp.server import _call_library, mcp


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
def finratio_valuation_growth_metrics(
    ticker: str,
    freq: str = "yearly",
    response_format: str = "json",
) -> Dict[str, Any]:
    """Return hybrid valuation and growth metrics (P/E, forward P/E, P/S, EV/EBITDA, FCF yield, dividend yield, payout ratio, beta, 3Y revenue & net income CAGR) as a snapshot.

    Args:
        ticker: Upper-case ticker symbol (e.g., AAPL, BRK-B).
        freq: Reporting frequency - 'yearly' or 'quarterly' (default: yearly).
        response_format: Output format - 'json' or 'markdown' (default: json).

    Returns:
        Dictionary with 'data' key containing a single snapshot dict keyed by
        Symbol + metric names, or error response.
    
    Error Codes:
        INVALID_TICKER: Ticker format invalid (must match [A-Z0-9.\\-]+)
        UNSUPPORTED_FREQ: Frequency not 'yearly' or 'quarterly'
        DATA_UNAVAILABLE: No data returned for this ticker/frequency
        UPSTREAM_ERROR: Network/connection issue with Yahoo Finance
        INTERNAL_ERROR: Unexpected error during processing
    """
    try:
        # Validate input via Pydantic model
        request = TickerRequest(
            ticker=ticker,
            freq=freq,  # type: ignore
            response_format=response_format,  # type: ignore
        )

        # Call library method
        df = _call_library(
            ticker=request.ticker,
            freq=request.freq,
            method_name="valuation_growth_metrics",
        )

        # Serialize to snapshot dict, then inject Symbol (Option B shim — see
        # module docstring). Symbol goes first so it is visually prominent in
        # both JSON and markdown renderings.
        snapshot = df_to_snapshot(df)
        snapshot = {"Symbol": request.ticker, **snapshot}

        # Handle markdown format
        if request.response_format == "markdown":
            markdown = to_markdown_kv(snapshot)
            return {"data": markdown}

        return {"data": snapshot}
    
    except MCPError as e:
        return error_response(e)
