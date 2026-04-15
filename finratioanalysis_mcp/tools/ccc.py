"""T020: Cash Conversion Cycle tool.

Exposes FinRatioAnalysis.ccc() as an MCP tool.
"""

from typing import Any, Dict

from finratioanalysis_mcp.adapters import df_to_period_rows, to_markdown_table
from finratioanalysis_mcp.models import TickerRequest
from finratioanalysis_mcp.server import _call_library, mcp


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
def finratio_ccc(
    ticker: str,
    freq: str = "yearly",
    response_format: str = "json",
) -> Dict[str, Any]:
    """Return Cash Conversion Cycle components (DIO, DSO, DPO, CCC) per reporting period.
    
    Args:
        ticker: Upper-case ticker symbol (e.g., AAPL, BRK-B).
        freq: Reporting frequency - 'yearly' or 'quarterly' (default: yearly).
        response_format: Output format - 'json' or 'markdown' (default: json).
    
    Returns:
        Dictionary with 'data' key containing list of period rows, or error response.
    """
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
        method_name="ccc",
    )
    
    # Serialize to period rows
    rows = df_to_period_rows(df)
    
    # Handle markdown format
    if request.response_format == "markdown":
        markdown = to_markdown_table(rows)
        return {"data": markdown}
    
    return {"data": rows}
