"""Pydantic models for MCP request/response validation.

Per data-model.md - shared input models for all tools.
"""

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


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
