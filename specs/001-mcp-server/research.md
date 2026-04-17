# Phase 0 Research: MCP Server for FinRatioAnalysis

**Feature**: `001-mcp-server` | **Date**: 2026-04-15

All technical unknowns from the spec's Technical Context have been resolved.
This document records decisions, rationale, and the alternatives considered.

---

## D1. Language & Framework

**Decision**: Python 3.10+ using the official MCP Python SDK (`mcp` package,
which bundles FastMCP).

**Rationale**:
- `FinRatioAnalysis` is a Python library; in-process import avoids a subprocess
  boundary and preserves pandas objects natively.
- FastMCP auto-generates tool input schemas from Pydantic models and docstrings,
  matching the mcp-builder skill's recommended Python pattern.
- Official SDK is actively maintained by Anthropic/MCP maintainers.

**Alternatives considered**:
- **TypeScript + `@modelcontextprotocol/sdk`** (the mcp-builder default): would
  require a subprocess call out to Python or a REST shim — extra moving parts
  with no benefit since no TypeScript-only capability is needed.
- **Low-level MCP SDK without FastMCP**: more boilerplate, no gain. Rejected.
- **Bare JSON-RPC / custom protocol**: violates spec FR-001 (must be MCP).
  Rejected.

---

## D2. Transport

**Decision**: stdio transport only for v1.

**Rationale**: Spec assumptions explicitly scope v1 to local single-user use;
stdio is the canonical local transport per mcp-builder best practices and the
default for Claude Desktop `mcpServers` entries.

**Alternatives considered**:
- **Streamable HTTP** (mcp-builder's recommended remote transport): adds auth,
  CORS, lifecycle, deploy surface. Out of scope for v1; can be added later
  without breaking stdio clients (they're configured independently).
- **SSE**: deprecated per mcp-builder guidance. Rejected.

---

## D3. Packaging

**Decision**: Ship the MCP adapter as a **sibling Python package**
(`finratioanalysis_mcp/`) in the same repository, exposed via an **optional
install extra**: `pip install FinRatioAnalysis[mcp]`.

**Rationale**:
- Honors constitution Principle I: `FinRatioAnalysis` remains a single,
  self-contained library with no new entry points inside it.
- Discoverability: users browsing this repo find the MCP next to the library.
- Optional extra keeps the core install lightweight (no MCP dependency for
  users who just want the library in a notebook).
- Independent versioning is trivial (separate `__version__` in
  `finratioanalysis_mcp/__init__.py`).

**Alternatives considered**:
- **Subpackage `FinRatioAnalysis.mcp`**: blurs library boundary; forces `mcp`
  and `pydantic` into the core dependency graph (or requires gated imports).
  Rejected.
- **Separate repo**: extra release overhead, orphaned tests, harder to keep in
  sync with library changes. Rejected for v1; revisit if the MCP grows large.

---

## D4. Tool Surface

**Decision**: One MCP tool per **data-returning** public method of
`FinRatioAnalysis`, plus one aggregate `finratio_company_snapshot`. Tool names
use the `finratio_` service prefix and snake_case (FR-014).

Full tool list (11):

| Tool | Library method | Shape |
|---|---|---|
| `finratio_return_ratios` | `return_ratios()` | time-series |
| `finratio_efficiency_ratios` | `efficiency_ratios()` | time-series |
| `finratio_leverage_ratios` | `leverage_ratios()` | time-series |
| `finratio_liquidity_ratios` | `liquidity_ratios()` | time-series |
| `finratio_ccc` | `ccc()` | time-series |
| `finratio_valuation_growth_metrics` | `valuation_growth_metrics()` | snapshot |
| `finratio_historical_valuation_metrics` | `historical_valuation_metrics()` | time-series |
| `finratio_z_score` | `z_score()` | snapshot |
| `finratio_capm` | `capm()` | snapshot |
| `finratio_wacc` | `wacc()` | snapshot |
| `finratio_company_snapshot` | — (aggregate) | composite |

**Excluded**: `z_score_plot()` — side-effect method rendering a Plotly figure
(spec US1 scenario 1 clarification).

**Rationale**: mcp-builder best practices favor comprehensive API coverage over
curated "workflow" tools when uncertain; the `company_snapshot` aggregate is
added as a QoL convenience (US3) without hiding the per-method tools.

---

## D5. Input Validation

**Decision**: Pydantic v2 models per tool, sharing a `TickerRequest` base.

Base model:
```python
class TickerRequest(BaseModel):
    ticker: str = Field(min_length=1, max_length=10, pattern=r"^[A-Z0-9.\-]+$")
    freq: Literal["yearly", "quarterly"] = "yearly"
    response_format: Literal["json", "markdown"] = "json"
```

**Rationale**: Pydantic v2 is the mcp-builder Python-guide idiom; FastMCP picks
up `Field` constraints as JSON Schema automatically; `Literal` enums give the
LLM precise allowed values in the tool schema.

**Alternatives considered**:
- **Dataclasses**: no automatic JSON Schema generation via FastMCP. Rejected.
- **Manual JSON Schema**: duplicates effort, easy to drift. Rejected.

---

## D6. Serialization (DataFrame → JSON / Markdown)

**Decision**: Central `adapters.py` module with two functions per shape:

- Time-series: `df_to_period_rows(df) → list[dict]` — `df.reset_index()` with
  the index column renamed to `date` and strftime-ed to ISO-8601, then
  `to_dict(orient="records")`; `NaN → None` via `df.where(pd.notna(df), None)`.
- Snapshot: `df_to_snapshot(df) → dict` — `df.iloc[0].to_dict()` with the
  same NaN handling.
- Markdown: built on top of the above using `tabulate` (already a pandas
  optional dep) or a small hand-rolled pipe-table formatter to avoid a new
  dependency.

**Rationale**: Satisfies FR-003 (ISO-8601 dates), FR-004 (NaN→null with
6-sig-fig precision via pandas default float formatting), and FR-013 (dual
format). One adapter module keeps the per-tool code trivial (DRY per
mcp-builder Phase 3.1).

**Alternatives considered**:
- **`df.to_json(orient="records", date_format="iso")`**: produces a string, not
  a list, forcing a re-parse. Rejected.
- **Custom `json.JSONEncoder`**: unnecessary given pandas handles this.
  Rejected.

---

## D7. Error Taxonomy

**Decision**: Structured error shape `{code, message, details?}` with a fixed
code vocabulary:

| Code | When |
|---|---|
| `INVALID_TICKER` | Ticker string fails regex or yfinance returns empty metadata. |
| `UNSUPPORTED_FREQ` | `freq` is not `yearly`/`quarterly` (Pydantic should catch first). |
| `DATA_UNAVAILABLE` | All rows would be NaN (e.g., newly IPO'd ticker asked for 3-yr CAGR). |
| `UPSTREAM_ERROR` | yfinance / network / HTTP failure; wraps original message in `details.upstream`. |
| `INTERNAL_ERROR` | Anything else; never exposes stack traces (FR-006). |

Errors are raised via a small `MCPError` exception caught at the tool
boundary and converted to an MCP-protocol error response.

**Rationale**: mcp-builder best practices: "error messages should guide agents
toward solutions" — fixed codes let LLMs route recovery logic; `details`
carries troubleshooting hints (e.g., `{suggested_tickers: [...]}` for near-miss
tickers later).

---

## D8. Tool Annotations

**Decision**: Apply MCP annotations uniformly (FR-015):

```python
annotations = {
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": True,  # external Yahoo Finance dependency
}
```

**Rationale**: All tools are pure reads against a live external API; `openWorld`
is true because results can change between calls (new earnings reports, price
moves). Matches mcp-builder annotation guidance exactly.

---

## D9. Configuration

**Decision**: Env-var-driven settings via a `config.py` `Settings` Pydantic
model with defaults:

| Env var | Default | Purpose |
|---|---|---|
| `FINRATIO_MCP_LOG_LEVEL` | `INFO` | Python logging level. |
| `FINRATIO_MCP_TIMEOUT_SECONDS` | `15` | Per-tool wall-clock budget. |
| `FINRATIO_MCP_DEFAULT_FREQ` | `yearly` | Default when client omits `freq`. |
| `FINRATIO_MCP_CACHE_TTL_SECONDS` | `0` (disabled) | Optional in-memory LRU cache; off by default. |

**Rationale**: Satisfies FR-010. Keeps config surface minimal; no file-based
config needed for v1.

---

## D10. Testing Strategy

**Decision**: Three layers.

1. **Unit tests** (`tests_mcp/tools/test_*.py`) — mock `FinRatioAnalysis` with a
   fixture returning canned DataFrames; assert adapter output matches expected
   JSON shape.
2. **Contract tests** (`tests_mcp/test_tool_contracts.py`) — validate every
   sample response against the matching `contracts/*.json` JSON Schema using
   `jsonschema`.
3. **Integration tests** (`@pytest.mark.integration`) — boot the FastMCP server
   in-process, issue real tool calls against a small live-ticker basket
   (`AAPL`, `MSFT`, `JPM`).
4. **LLM evaluation** — `specs/001-mcp-server/evaluation.xml` with 10 Q&A pairs
   run through the mcp-builder `scripts/evaluation.py` harness to measure SC-005.

**Rationale**: Mirrors constitution Principle III (unit + integration per
public method) and adds contract tests as the machine-checkable enforcement of
FR-003/FR-004/FR-015.

---

## D11. Entry Point & Distribution

**Decision**:
- Console script `finratioanalysis-mcp` registered via `pyproject.toml`
  `[project.scripts]`.
- `python -m finratioanalysis_mcp` also works via `__main__.py`.
- Both call `server.main()` which starts FastMCP on stdio.

**Rationale**: Satisfies FR-007 (installable and runnable without user glue
code). `python -m` form is the convention Claude Desktop `mcpServers` config
examples use.

---

## D12. Evaluation Suite

**Decision**: Author 10 stable, verifiable Q&A pairs in
`specs/001-mcp-server/evaluation.xml` during the `/speckit.implement` phase,
e.g.:
- "For AAPL yearly, what is the latest ROIC?"
- "Which of AAPL, MSFT, GOOGL has the highest Altman Z-Score?"
- "What is JPM's current P/E ratio?"

Stability: answers are fetched from yfinance at eval-creation time and
documented alongside the question as the reference answer. A small tolerance
window (±1%) is allowed at run time to accommodate upstream data revisions.

**Rationale**: Satisfies SC-005; follows the mcp-builder Phase 4 template
exactly (XML format per `evaluation.md`).

---

## Open Questions

**None.** All Technical Context items have decisions; no `NEEDS CLARIFICATION`
remains. The plan may proceed to `/speckit.tasks`.
