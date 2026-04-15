"""FastMCP server for FinRatioAnalysis.

Provides MCP tools exposing financial ratio analysis methods
over stdio transport.
"""

import logging
import sys
import uuid
from typing import Any

import pandas as pd
from mcp.server.fastmcp import FastMCP

from FinRatioAnalysis import FinRatioAnalysis

from .config import settings
from .errors import ErrorCode, MCPError

# Initialize FastMCP server
mcp = FastMCP("finratioanalysis_mcp")

# Configure logging — MCP stdio servers MUST log to stderr so stdout stays
# reserved for the JSON-RPC protocol stream.
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(levelname)s %(name)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("finratioanalysis_mcp")


def _call_library(ticker: str, freq: str, method_name: str) -> pd.DataFrame:
    """Call a FinRatioAnalysis method and translate failures to MCPError.

    Input validation of ``ticker`` / ``freq`` happens at the MCP boundary via
    the ``TickerRequest`` Pydantic model (see ``models.py``). Ticker
    pre-flight validation against yfinance is deferred to T043 (US2).

    Args:
        ticker: Stock ticker symbol (already regex-validated upstream).
        freq: ``'yearly'`` or ``'quarterly'`` (already enum-validated upstream).
        method_name: Name of the FinRatioAnalysis method to invoke.

    Returns:
        DataFrame returned by the library method.

    Raises:
        MCPError: Structured error for the MCP client.
    """
    # Short correlation ID surfaced to the client and stamped on every log
    # line for this call — lets operators find the matching server-side
    # traceback from a user's error report (`ref=<req_id>`).
    req_id = uuid.uuid4().hex[:8]

    try:
        logger.info(
            "req=%s Calling %s for ticker=%s, freq=%s",
            req_id, method_name, ticker, freq,
        )

        analyzer = FinRatioAnalysis(ticker=ticker, freq=freq)

        if not hasattr(analyzer, method_name):
            raise MCPError(
                code=ErrorCode.INTERNAL_ERROR,
                message=f"Method '{method_name}' does not exist on FinRatioAnalysis (ref={req_id})",
                details={"method": method_name, "req_id": req_id},
            )

        result = getattr(analyzer, method_name)()

        if not isinstance(result, pd.DataFrame):
            raise MCPError(
                code=ErrorCode.INTERNAL_ERROR,
                message=f"Method '{method_name}' returned unexpected type: {type(result).__name__} (ref={req_id})",
                details={
                    "expected": "DataFrame",
                    "actual": type(result).__name__,
                    "req_id": req_id,
                },
            )

        # Truly empty result (no rows, no columns) → hard DATA_UNAVAILABLE.
        # Partial NaN rows are NOT errors: the adapter will map NaN → null
        # per constitution Principle IV / FR-004, and the LLM can reason
        # about missing fields itself.
        if result.empty:
            raise MCPError(
                code=ErrorCode.DATA_UNAVAILABLE,
                message=f"No data available for {ticker} at {freq} frequency (ref={req_id})",
                details={
                    "ticker": ticker,
                    "freq": freq,
                    "method": method_name,
                    "req_id": req_id,
                },
            )

        logger.info("req=%s Retrieved %s: shape=%s", req_id, method_name, result.shape)
        return result

    except MCPError:
        raise

    except Exception as e:
        # Upstream HTTP / network issues surfacing from yfinance / requests.
        upstream_names = {
            "ConnectionError",
            "Timeout",
            "TimeoutError",
            "HTTPError",
            "RequestException",
            "ReadTimeout",
            "ConnectTimeout",
        }
        if isinstance(e, (ConnectionError, TimeoutError)) or type(e).__name__ in upstream_names:
            logger.warning("req=%s Upstream error: %s", req_id, e)
            raise MCPError(
                code=ErrorCode.UPSTREAM_ERROR,
                message=f"Failed to reach Yahoo Finance (ref={req_id})",
                details={
                    "upstream": str(e),
                    "service": "yfinance",
                    "req_id": req_id,
                },
            ) from e

        # Anything else is an unanticipated bug — never leak the stack to the
        # client (FR-006); log it locally on stderr with the req_id so it can
        # be correlated to the client-visible reference.
        logger.exception("req=%s Unexpected error in _call_library", req_id)
        raise MCPError(
            code=ErrorCode.INTERNAL_ERROR,
            message=f"An unexpected error occurred while fetching financial data. (ref={req_id})",
            details={"error_type": type(e).__name__, "req_id": req_id},
        ) from e


def main() -> None:
    """Entry point for the MCP server.

    Configures logging and runs the FastMCP server on stdio transport.
    """
    # Hard Python-version guard: the MCP layer uses 3.10+ typing syntax
    # (`list[dict]`, PEP 604 unions). The library itself supports 3.7+;
    # only the `[mcp]` extra requires this floor.
    if sys.version_info < (3, 10):
        print(
            "finratioanalysis_mcp requires Python 3.10 or newer "
            f"(current: {sys.version.split()[0]}).",
            file=sys.stderr,
        )
        sys.exit(1)

    logger.info("Starting FinRatioAnalysis MCP server (log_level=%s)", settings.log_level)
    logger.info(
        "Configuration: timeout=%ss, default_freq=%s",
        settings.timeout_seconds,
        settings.default_freq,
    )

    try:
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception:
        logger.exception("Server error")
        sys.exit(1)


if __name__ == "__main__":
    main()
