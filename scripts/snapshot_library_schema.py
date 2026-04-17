"""Snapshot real FinRatioAnalysis column schemas to a JSON file.

Run once (and whenever the library's public column surface changes):

    python scripts/snapshot_library_schema.py

Output: tests_mcp/fixtures/library_schema.json

The snapshot is the single source of truth for mock DataFrame column names
in tests_mcp/conftest.py. This prevents unit tests from passing against
invented column names that don't match the real library — the class of
false positive called out during T014 review.

Ticker choice: AAPL is used because it has complete data across every
public method. If a method still returns empty for AAPL (unlikely),
fall back to MSFT.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from FinRatioAnalysis import FinRatioAnalysis

TICKER = "AAPL"

# Methods that return a time-series DataFrame (date-indexed, multi-row).
TIMESERIES_METHODS = [
    "return_ratios",
    "efficiency_ratios",
    "leverage_ratios",
    "liquidity_ratios",
    "ccc",
    "historical_valuation_metrics",
]

# Methods that return a single-row snapshot DataFrame.
SNAPSHOT_METHODS = [
    "valuation_growth_metrics",
    "z_score",
    "capm",
    "wacc",
]


def snapshot() -> dict:
    fra = FinRatioAnalysis(TICKER)
    schema: dict[str, dict] = {}

    for name in TIMESERIES_METHODS + SNAPSHOT_METHODS:
        df = getattr(fra, name)()
        if df is None or df.empty:
            print(f"WARN: {name}() returned empty for {TICKER}", file=sys.stderr)
            schema[name] = {"kind": "unknown", "columns": [], "index_name": None}
            continue

        schema[name] = {
            "kind": "timeseries" if name in TIMESERIES_METHODS else "snapshot",
            "columns": list(df.columns),
            "index_name": df.index.name,
        }
        print(f"OK   {name}: {len(df.columns)} cols")

    return schema


def main() -> int:
    out_path = Path(__file__).resolve().parents[1] / "tests_mcp" / "fixtures" / "library_schema.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    schema = snapshot()
    out_path.write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
