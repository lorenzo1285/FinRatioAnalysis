# Phase 1 Data Model: MCP Server for FinRatioAnalysis

**Feature**: `001-mcp-server` | **Date**: 2026-04-15

All MCP-facing data structures, expressed as Pydantic v2 models. These drive
the auto-generated JSON Schema that ships in `contracts/` and is surfaced to
LLM clients.

---

## Shared input models

### `TickerRequest` (base)

Every tool extends this.

| Field | Type | Constraints | Default | Notes |
|---|---|---|---|---|
| `ticker` | `str` | `min_length=1, max_length=10, pattern=^[A-Z0-9.\-]+$` | *required* | Uppercase symbol; allows `.`, `-` (e.g., `BRK.B`, `RDS-A`). |
| `freq` | `Literal["yearly", "quarterly"]` | enum | `"yearly"` | Forwarded to `FinRatioAnalysis(ticker, freq)`. |
| `response_format` | `Literal["json", "markdown"]` | enum | `"json"` | Per FR-013. |

### Tool-specific inputs

All eleven tools share `TickerRequest` with no additional fields. If future
tools need extras (e.g., a custom risk-free rate for CAPM), they subclass and
add optional fields only.

---

## Output entities

### `PeriodRow` (time-series row)

The shape of one element in a time-series tool's array response.

| Field | Type | Notes |
|---|---|---|
| `date` | `str` (ISO-8601, `YYYY-MM-DD`) | Derived from the DataFrame index via `strftime("%Y-%m-%d")`. |
| *metric fields* | `float \| null` | One per column in the library DataFrame; `NaN` → `null` (FR-004). |

The exact metric fields per tool follow the library's documented column names
(see `README.md` §API Reference). The contract files pin them explicitly.

### `SnapshotObject`

Single-row response for `valuation_growth_metrics`, `z_score`, `capm`, `wacc`.

| Field | Type | Notes |
|---|---|---|
| `Symbol` | `str` | Always present — ticker echo. |
| *metric fields* | `float \| str \| null` | Per the library's single-row DataFrame columns (`Zone` is a string, others floats). |

### `CompanySnapshot`

Response for `finratio_company_snapshot`.

```
{
  "ticker": "AAPL",
  "freq": "yearly",
  "sections": {
    "return_ratios":              { "status": "ok",    "data": [PeriodRow, ...] },
    "efficiency_ratios":          { "status": "ok",    "data": [PeriodRow, ...] },
    "leverage_ratios":            { "status": "ok",    "data": [PeriodRow, ...] },
    "liquidity_ratios":           { "status": "ok",    "data": [PeriodRow, ...] },
    "ccc":                        { "status": "ok",    "data": [PeriodRow, ...] },
    "valuation_growth_metrics":   { "status": "ok",    "data": SnapshotObject  },
    "historical_valuation_metrics": { "status": "ok",  "data": [PeriodRow, ...] },
    "z_score":                    { "status": "ok",    "data": SnapshotObject  },
    "capm":                       { "status": "error", "error": ErrorResponse  },
    "wacc":                       { "status": "ok",    "data": SnapshotObject  }
  }
}
```

Per-section `status` allows partial success (spec US3 scenario 2): if CAPM
fails for a given ticker (e.g., insufficient price history), every other
section still populates and the failing section carries an `ErrorResponse`.

### `ErrorResponse`

| Field | Type | Notes |
|---|---|---|
| `code` | `Literal["INVALID_TICKER","UNSUPPORTED_FREQ","DATA_UNAVAILABLE","UPSTREAM_ERROR","INTERNAL_ERROR"]` | Closed vocabulary (research D7). |
| `message` | `str` | Human-readable; suitable for LLM → user relay. |
| `details` | `dict \| null` | Optional structured context (e.g., `{upstream: "HTTPError: 429"}`). |

---

## Validation rules

1. `ticker` is normalized to uppercase before use; regex rejects empty,
   lowercase-only, or characters outside `[A-Z0-9.-]`.
2. `freq` default (`yearly`) resolves at Pydantic layer — the library is always
   constructed with an explicit frequency.
3. `response_format` is consumed by the adapter layer only; it never reaches
   the library.
4. Output floats are preserved at pandas default precision (≥6 significant
   digits per FR-004); no rounding performed by the MCP layer.
5. Dates are ALWAYS rendered as `YYYY-MM-DD` strings in JSON, even if the
   underlying pandas index is timezone-aware (timezone is stripped after
   conversion to local date).

---

## State & lifecycle

The MCP server is **stateless by default**. A `FinRatioAnalysis` instance is
constructed per tool call and discarded. When `FINRATIO_MCP_CACHE_TTL_SECONDS`
is > 0 (opt-in), a process-local LRU cache keyed by `(ticker, freq, method)`
caches tool *responses* (not library objects) for the configured TTL. Cache is
dropped on server restart; never persisted.

---

## Non-goals for data model v1

- No user / session entities (single-user local).
- No rate-limit accounting entity (upstream throttling surfaces as
  `UPSTREAM_ERROR`).
- No pagination envelope (responses are bounded — ≤16 rows for quarterly
  historical valuation, smaller elsewhere).
