"""Pydantic models for MCP request/response validation.

Per data-model.md - shared input models for all tools.
"""

from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from finratioanalysis_mcp.errors import ErrorCode, MCPError


class TickerRequest(BaseModel):
    """Base request model for all FinRatioAnalysis tools.

    Attributes:
        ticker: Stock ticker symbol (uppercase, allows . and -)
        freq: Data frequency (yearly or quarterly)
        response_format: Output format (json or markdown)
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    ticker: str = Field(
        min_length=1,
        max_length=10,
        pattern=r"^[A-Z0-9.\-]+$",
        description="Stock ticker symbol (e.g., AAPL, BRK.B, RDS-A)",
    )

    freq: Literal["yearly", "quarterly"] = Field(
        default="yearly",
        description="Data frequency: yearly or quarterly",
    )

    response_format: Literal["json", "markdown"] = Field(
        default="json",
        description="Response format: json (structured) or markdown (table)",
    )


def parse_request(**kwargs: Any) -> "TickerRequest":
    """Build a TickerRequest and translate Pydantic errors into MCPError.

    Without this wrapper, ValidationError escapes the tool's `except MCPError`
    block and the MCP client receives an unstructured crash instead of a clean
    INVALID_TICKER / UNSUPPORTED_FREQ ErrorResponse. Each tool calls this
    helper in place of `TickerRequest(...)`.
    """
    try:
        return TickerRequest(**kwargs)
    except ValidationError as e:
        first = e.errors()[0]
        loc = first.get("loc", ())
        field = loc[0] if loc else None

        if field == "ticker":
            raise MCPError(
                code=ErrorCode.INVALID_TICKER,
                message="Invalid ticker format. Must be upper-case alphanumerics with optional '.' or '-' (e.g., AAPL, BRK-B).",
                details={"field": "ticker", "pydantic_error": first.get("msg", "")},
            ) from e
        if field == "freq":
            raise MCPError(
                code=ErrorCode.UNSUPPORTED_FREQ,
                message="Unsupported frequency. Must be 'yearly' or 'quarterly'.",
                details={"field": "freq", "pydantic_error": first.get("msg", "")},
            ) from e
        raise MCPError(
            code=ErrorCode.INTERNAL_ERROR,
            message=f"Request validation failed on field '{field}'.",
            details={"field": str(field), "pydantic_error": first.get("msg", "")},
        ) from e
