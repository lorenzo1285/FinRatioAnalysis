"""Error handling for FinRatioAnalysis MCP Server.

Defines error codes, exceptions, and response formatting per research D7.
"""

from enum import Enum
from typing import Any


class ErrorCode(str, Enum):
    """Fixed vocabulary of MCP error codes."""

    INVALID_TICKER = "INVALID_TICKER"
    UNSUPPORTED_FREQ = "UNSUPPORTED_FREQ"
    DATA_UNAVAILABLE = "DATA_UNAVAILABLE"
    UPSTREAM_ERROR = "UPSTREAM_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class MCPError(Exception):
    """MCP-specific exception with structured error code.
    
    Attributes:
        code: ErrorCode enum value
        message: Human-readable error message
        details: Optional structured context for troubleshooting
    """

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        details: dict[str, Any] | None = None,
    ):
        self.code = code
        self.message = message
        self.details = details
        super().__init__(message)


def error_response(error: MCPError) -> dict[str, Any]:
    """Convert MCPError to ErrorResponse dict shape.
    
    Args:
        error: MCPError instance
        
    Returns:
        Dictionary with code, message, and optional details
    """
    response: dict[str, Any] = {
        "code": error.code.value,
        "message": error.message,
    }
    
    if error.details:
        response["details"] = error.details
    
    return response
