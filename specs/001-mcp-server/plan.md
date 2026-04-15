# Implementation Plan: MCP Server for FinRatioAnalysis

**Branch**: `001-mcp-server` | **Date**: 2026-04-15 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-mcp-server/spec.md`

## Summary

Expose every data-returning analytical method of the `FinRatioAnalysis` library
as a read-only MCP tool so MCP-capable LLM clients (Claude Desktop, IDE
assistants, agents) can answer fundamental-analysis questions against live Yahoo
Finance data. Delivered as a **sibling Python package** (`finratioanalysis_mcp`)
that imports `FinRatioAnalysis` in-process and adapts its DataFrame responses to
MCP-shaped JSON (or Markdown on request). Built on the official MCP Python SDK
(`FastMCP`) with Pydantic v2 input validation, stdio transport for v1, and a
10-question XML evaluation suite per the mcp-builder Phase-4 methodology.

No changes to the `FinRatioAnalysis` library are required for v1. The MCP layer
is a pure adapter.

## Technical Context

**Language/Version**: Python 3.10+ (library floor is 3.7+ per `pyproject.toml`;
FastMCP and Pydantic v2 require 3.10+, so the MCP package raises the floor for
itself only).
**Primary Dependencies**: `mcp` (official MCP Python SDK, includes FastMCP),
`pydantic>=2`, `FinRatioAnalysis` (this repo), transitive: `yfinance`, `pandas`,
`numpy`, `plotly`, `requests`.
**Storage**: N/A (stateless; no persistence; optional in-memory cache behind an
env var is a non-goal for v1).
**Testing**: `pytest` for unit + contract tests; `@pytest.mark.integration` for
live Yahoo Finance calls; MCP Inspector (`npx @modelcontextprotocol/inspector`)
for manual protocol verification; `scripts/evaluation.py` from the mcp-builder
skill for the 10-question LLM eval.
**Target Platform**: Local developer machines running an MCP-capable client
(Claude Desktop, Cline, Continue, etc.) on Windows, macOS, or Linux. Stdio
transport only in v1.
**Project Type**: Python library (sibling adapter package), installed alongside
`FinRatioAnalysis`.
**Performance Goals**: P50 end-to-end tool latency ≤ 5 s per SC-004 (dominated
by yfinance I/O); server startup ≤ 500 ms; memory footprint ≤ 150 MB.
**Constraints**: No external services beyond Yahoo Finance; no API keys; no
auth; single-user local scope. Must not mutate or wrap the library's public API
(constitution Principle I, FR-009).
**Scale/Scope**: 11 tools (10 per-method + 1 `company_snapshot`); ~1–2k LOC
Python; test corpus of ~30 unit tests + 10 eval Q&A pairs; representative
ticker basket of 20 symbols across sectors for robustness testing (SC-003).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Evaluated against `.specify/memory/constitution.md` v1.0.0:

| # | Principle | Status | Notes |
|---|-----------|--------|-------|
| I | Single-Package, Library-First | ✅ PASS | MCP ships as a **sibling package** `finratioanalysis_mcp`, not a new entry point inside `FinRatioAnalysis`. The library remains untouched. |
| II | DataFrame-In/DataFrame-Out Contract | ✅ PASS | MCP tools are faithful projections of the library's DataFrames: time-series → JSON arrays of period objects with ISO dates; snapshots → single JSON objects. Column names preserved. |
| III | Test-First for Public Methods | ✅ PASS | Each tool gets a unit test (mocked library) + a contract test (JSON Schema validation) + inclusion in the MCP-level integration marker. 10-question eval.xml completes the guarantee. |
| IV | Resilience to Missing/Irregular Data | ✅ PASS | `NaN → null` mapping (FR-004), structured error taxonomy (FR-005), no stack traces to client (FR-006). Bank / missing-field behavior inherits library fallbacks. |
| V | Backward-Compatible Evolution with SemVer | ✅ PASS | Zero changes to the library → no library version bump required. MCP package starts at its own `0.1.0` and versions independently. |

**Post-Phase-1 re-check**: PASS (no new violations introduced; see research.md
decisions).

**Complexity Tracking**: *N/A — no deviations from the constitution.*

## Project Structure

### Documentation (this feature)

```text
specs/001-mcp-server/
├── plan.md              # This file
├── research.md          # Phase 0 output — decisions + rationale + alternatives
├── data-model.md        # Phase 1 output — Pydantic / JSON Schema entities
├── quickstart.md        # Phase 1 output — install & first-call walkthrough
├── contracts/           # Phase 1 output — one JSON Schema per tool
│   ├── README.md
│   ├── finratio_return_ratios.json
│   ├── finratio_efficiency_ratios.json
│   ├── finratio_leverage_ratios.json
│   ├── finratio_liquidity_ratios.json
│   ├── finratio_ccc.json
│   ├── finratio_valuation_growth_metrics.json
│   ├── finratio_historical_valuation_metrics.json
│   ├── finratio_z_score.json
│   ├── finratio_capm.json
│   ├── finratio_wacc.json
│   └── finratio_company_snapshot.json
├── evaluation.xml       # Phase 4 output (created during /implement) — 10 Q&A pairs
└── tasks.md             # /speckit.tasks output — NOT produced by this command
```

### Source Code (repository root)

```text
# Existing (unchanged)
FinRatioAnalysis/
├── __init__.py
└── FinRatioAnalysis.py

# NEW: sibling package for the MCP adapter
finratioanalysis_mcp/
├── __init__.py
├── __main__.py           # `python -m finratioanalysis_mcp` entry point
├── server.py             # FastMCP instance + tool registrations
├── models.py             # Pydantic v2 input/output models
├── adapters.py           # DataFrame → JSON / Markdown serializers; NaN→null
├── errors.py             # Error taxonomy: INVALID_TICKER, UNSUPPORTED_FREQ, ...
├── config.py             # Env-var-driven settings (timeout, log level)
└── tools/
    ├── __init__.py
    ├── return_ratios.py
    ├── efficiency_ratios.py
    ├── leverage_ratios.py
    ├── liquidity_ratios.py
    ├── ccc.py
    ├── valuation_growth_metrics.py
    ├── historical_valuation_metrics.py
    ├── z_score.py
    ├── capm.py
    ├── wacc.py
    └── company_snapshot.py

tests/                    # existing tests untouched
tests_mcp/                # NEW — parallel test tree for the MCP package
├── conftest.py
├── test_server_boot.py
├── test_adapters.py
├── test_errors.py
├── test_tool_contracts.py       # validates responses against contracts/*.json
└── tools/
    ├── test_return_ratios.py
    ├── ...                       # one file per tool
    └── test_company_snapshot.py

# Packaging
pyproject.toml            # existing; gains an optional `mcp` extra:
                          #   pip install FinRatioAnalysis[mcp]
```

**Structure Decision**: **Sibling Python package inside the same repo**, shipped
as an optional install extra (`FinRatioAnalysis[mcp]`). This honors constitution
Principle I (the core library stays a single, self-contained unit) while keeping
the MCP adapter discoverable in the same source tree. Tests live in a parallel
`tests_mcp/` tree so `pytest tests/` still runs only library tests (preserving
existing CI behavior) and `pytest tests_mcp/` runs the MCP suite.

## Complexity Tracking

*No violations of the constitution. Section intentionally empty.*

---

## Phase 0: Outline & Research

Completed — see [research.md](./research.md) for decisions, rationale, and
alternatives considered. All technical choices resolved; no `NEEDS
CLARIFICATION` markers remain.

## Phase 1: Design & Contracts

Completed — see:
- [data-model.md](./data-model.md) — entities, validation rules, state
- [contracts/](./contracts/) — 11 JSON Schema files, one per tool
- [quickstart.md](./quickstart.md) — user-facing install & first-call walkthrough

**Agent context update**: The Spec Kit `update-agent-context.ps1` script can
be run post-plan to refresh Claude's context file with the new tech stack
(FastMCP, Pydantic v2, MCP Inspector). This is environment-dependent
(PowerShell) and can be deferred to implementation time.

## Next Command

Run `/speckit.tasks` to decompose this plan into an ordered, dependency-aware
`tasks.md`.
