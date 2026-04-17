"""T024: CAPM tool.

Exposes FinRatioAnalysis.capm() as an MCP tool.
"""

from typing import Any, Dict

from finratioanalysis_mcp.adapters import df_to_snapshot, to_markdown_kv
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
def finratio_capm(
    ticker: str,
    freq: str = "yearly",
    response_format: str = "json",
) -> Dict[str, Any]:
    """Return CAPM expected return and Sharpe ratio.
    
    Args:
        ticker: Upper-case ticker symbol (e.g., AAPL, BRK-B).
        freq: Reporting frequency - 'yearly' or 'quarterly' (default: yearly).
        response_format: Output format - 'json' or 'markdown' (default: json).
    
    Returns:
        Dictionary with 'data' key containing snapshot object, or error response.
    
    Error Codes:
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
        
        # Call library method
        df = _call_library(
            ticker=request.ticker,
            freq=request.freq,
            method_name="capm",
        )
        
        # Serialize to snapshot
        snapshot = df_to_snapshot(df)
        
        # Handle markdown format
        if request.response_format == "markdown":
            markdown = to_markdown_kv(snapshot)
            return {"data": markdown}
        
        return {"data": snapshot}
    
    except MCPError as e:
        return error_response(e)
