---
description: "Task list for 001-mcp-server"
---

# Tasks: MCP Server for FinRatioAnalysis

**Input**: Design documents in `/specs/001-mcp-server/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: INCLUDED. Constitution Principle III (Test-First for Public Methods)
mandates unit + integration tests for every tool; contract tests are required
to enforce FR-003/FR-004/FR-015; the 10-Q evaluation suite is required by SC-005.

**Organization**: Grouped by user story. US1 is MVP; US2 and US3 layer on top.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: `US1`, `US2`, `US3`, or `FND` (foundational / shared)
- All paths are absolute-from-repo-root (e.g., `finratioanalysis_mcp/server.py`)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Bring the sibling package skeleton into existence.

- [x] **T001** Create package directories: `finratioanalysis_mcp/`,
  `finratioanalysis_mcp/tools/`, `tests_mcp/`, `tests_mcp/tools/`. Add empty
  `__init__.py` files in each.
- [x] **T002** Update `pyproject.toml`: add `[project.optional-dependencies]`
  with `mcp = ["mcp>=1.2", "pydantic>=2"]`, add `[project.scripts]` entry
  `finratioanalysis-mcp = "finratioanalysis_mcp.server:main"`, and add
  `finratioanalysis_mcp*` to `[tool.setuptools] packages`.
- [x] **T003** [P] Add `tests_mcp/` to `pytest.ini` testpaths (or create a
  separate `pytest-mcp.ini`) and register an `integration` marker if not
  already present.
- [x] **T004** [P] Create `finratioanalysis_mcp/__init__.py` with a
  `__version__ = "0.1.0"` literal.

**Checkpoint**: `pip install -e ".[mcp]"` succeeds; `python -c "import
finratioanalysis_mcp"` works.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure every tool depends on. Must complete before
any user story tasks.

- [x] **T005** [P] [FND] Implement `finratioanalysis_mcp/config.py` —
  Pydantic `Settings` model reading `FINRATIO_MCP_LOG_LEVEL`,
  `FINRATIO_MCP_TIMEOUT_SECONDS`, `FINRATIO_MCP_DEFAULT_FREQ`,
  `FINRATIO_MCP_CACHE_TTL_SECONDS` with defaults per research D9.
- [x] **T006** [P] [FND] Implement `finratioanalysis_mcp/errors.py` —
  `MCPError` exception + `ErrorCode` enum (`INVALID_TICKER`, `UNSUPPORTED_FREQ`,
  `DATA_UNAVAILABLE`, `UPSTREAM_ERROR`, `INTERNAL_ERROR`) + `error_response()`
  helper producing the `ErrorResponse` dict shape from data-model.md.
- [x] **T007** [P] [FND] Implement `finratioanalysis_mcp/models.py` — Pydantic
  v2 `TickerRequest` base (ticker regex, freq enum, response_format enum) per
  data-model.md §Shared input models.
- [x] **T008** [FND] Implement `finratioanalysis_mcp/adapters.py` —
  `df_to_period_rows(df) -> list[dict]`, `df_to_snapshot(df) -> dict` with
  `NaN→None` and ISO-8601 date rendering; plus `to_markdown_table(rows)` and
  `to_markdown_kv(snapshot)` for `response_format="markdown"` (research D6).
  Depends on T007.
- [x] **T009** [FND] Implement `finratioanalysis_mcp/server.py` — FastMCP
  instance `mcp = FastMCP("finratioanalysis_mcp")`, a `main()` that wires
  config + logging and runs `mcp.run()` on stdio, and a `_call_library(ticker,
  freq, method_name)` dispatcher that instantiates `FinRatioAnalysis` once and
  translates library exceptions to `MCPError`. Depends on T005, T006, T007.
- [x] **T010** [FND] Implement `finratioanalysis_mcp/__main__.py` — thin
  `from .server import main; main()` module entry point. Depends on T009.
- [x] **T011** [P] [FND] `tests_mcp/conftest.py` — pytest fixtures for a
  mocked `FinRatioAnalysis` class yielding canned DataFrames (one per method),
  plus a fixture returning a running FastMCP server (in-process).
- [x] **T012** [P] [FND] `tests_mcp/test_adapters.py` — unit tests for
  `df_to_period_rows` (ISO date, NaN→null, column preservation) and
  `df_to_snapshot`; Markdown renderers produce well-formed tables.
- [x] **T013** [P] [FND] `tests_mcp/test_errors.py` — each `ErrorCode` maps to
  the correct response shape; `MCPError` never leaks a stack trace.
- [x] **T014** [P] [FND] `tests_mcp/test_server_boot.py` — import
  `finratioanalysis_mcp.server`, assert `FastMCP` instance name and that
  `main()` is callable.

**Checkpoint**: Foundation complete. Running `python -m finratioanalysis_mcp`
starts (with zero tools) and exits cleanly on stdin close. All Phase 2 tests pass.

---

## Phase 3: User Story 1 — LLM can invoke per-method tools (Priority: P1) 🎯 MVP

**Goal**: Every public data-returning method of `FinRatioAnalysis` is
reachable as an MCP tool and returns correctly shaped JSON (FR-001..FR-004,
FR-008, FR-014, FR-015).

**Independent Test**: Start the server, connect MCP Inspector, invoke each
tool with `ticker="AAPL"`, confirm the response validates against the
matching `contracts/*.json` output schema.

### Contract tests for US1 (write FIRST, must FAIL before implementation)

- [x] **T015** [P] [US1] `tests_mcp/test_tool_contracts.py` — parametrized
  test that loads every `specs/001-mcp-server/contracts/*.json`, invokes the
  corresponding tool with a mocked ticker, and validates the response against
  the contract's `output` schema using `jsonschema`.

### Implementation for US1 — tools (all parallel; each tool lives in its own file)

- [x] **T016** [P] [US1] `finratioanalysis_mcp/tools/return_ratios.py` —
  register `finratio_return_ratios` with description, annotations (readOnly,
  idempotent, openWorld), dispatch to library `return_ratios()`, serialize via
  `adapters.df_to_period_rows`. Depends on T008, T009.
- [x] **T017** [P] [US1] `finratioanalysis_mcp/tools/efficiency_ratios.py` —
  `finratio_efficiency_ratios`.
- [x] **T018** [P] [US1] `finratioanalysis_mcp/tools/leverage_ratios.py` —
  `finratio_leverage_ratios`.
- [x] **T019** [P] [US1] `finratioanalysis_mcp/tools/liquidity_ratios.py` —
  `finratio_liquidity_ratios`.
- [x] **T020** [P] [US1] `finratioanalysis_mcp/tools/ccc.py` — `finratio_ccc`.
- [x] **T021** [P] [US1] `finratioanalysis_mcp/tools/historical_valuation_metrics.py`
  — `finratio_historical_valuation_metrics`.
- [x] **T022** [P] [US1] `finratioanalysis_mcp/tools/valuation_growth_metrics.py`
  — `finratio_valuation_growth_metrics` (snapshot shape).
  **NOTE (Option B shim):** Library's `valuation_growth_metrics()` is the only snapshot method without a `Symbol` column. Adapter MUST inject it:
  `row = df.iloc[0].to_dict(); return {"data": {"Symbol": ticker, **row}}`.
  Contract requires `Symbol`; mock fixture does NOT include it — the injection is what makes the contract test pass. Add a comment flagging this as a shim for upstream library inconsistency (removable if the library is ever fixed). Do NOT normalize column casing.
- [x] **T023** [P] [US1] `finratioanalysis_mcp/tools/z_score.py` —
  `finratio_z_score` (snapshot; `z_score_plot` NOT exposed).
- [x] **T024** [P] [US1] `finratioanalysis_mcp/tools/capm.py` —
  `finratio_capm`.
- [x] **T025** [P] [US1] `finratioanalysis_mcp/tools/wacc.py` —
  `finratio_wacc`.
- [x] **T026** [US1] `finratioanalysis_mcp/tools/__init__.py` — import every
  tool module so FastMCP registers them at server startup. Depends on
  T016–T025.

### Unit tests for US1 (one per tool)

- [x] **T027** [P] [US1] `tests_mcp/tools/test_return_ratios.py` — happy-path
  with mocked fixture; assert output shape + column set.
- [x] **T028** [P] [US1] `tests_mcp/tools/test_efficiency_ratios.py`.
- [x] **T029** [P] [US1] `tests_mcp/tools/test_leverage_ratios.py`.
- [x] **T030** [P] [US1] `tests_mcp/tools/test_liquidity_ratios.py`.
- [x] **T031** [P] [US1] `tests_mcp/tools/test_ccc.py`.
- [x] **T032** [P] [US1] `tests_mcp/tools/test_historical_valuation_metrics.py`.
- [x] **T033** [P] [US1] `tests_mcp/tools/test_valuation_growth_metrics.py`.
- [x] **T034** [P] [US1] `tests_mcp/tools/test_z_score.py`.
- [x] **T035** [P] [US1] `tests_mcp/tools/test_capm.py`.
- [x] **T036** [P] [US1] `tests_mcp/tools/test_wacc.py`.

### Markdown rendering for US1 (FR-013)

- [x] **T037** [US1] Extend each tool to honor `response_format="markdown"`
  by routing through `adapters.to_markdown_table` /
  `adapters.to_markdown_kv`. Single-commit cross-file edit touching all 10
  tools. Depends on T016–T025.
- [x] **T038** [P] [US1] `tests_mcp/test_markdown_format.py` — one
  parametrized test per tool verifying Markdown output is non-empty and
  contains the expected column headers.

**Checkpoint (MVP)**: US1 complete. `pytest tests_mcp/` green; MCP Inspector
lists 10 tools; each returns contract-valid JSON and Markdown. Spec SC-002
("100% of public analytical methods reachable") satisfied.

---

## Phase 4: User Story 2 — Graceful handling of bad inputs & missing data (Priority: P2)

**Goal**: Invalid tickers, bad frequencies, and bank-style missing fields
produce structured errors or `null` values — no stack traces, no crashes
(FR-005, FR-006; spec US2 scenarios 1–3).

### Tests for US2 (write FIRST)

- [x] **T039** [P] [US2] `tests_mcp/test_error_invalid_ticker.py` — invoke
  any tool with `ticker="ZZZZZ"`; assert response is an `ErrorResponse` with
  `code="INVALID_TICKER"`.
- [x] **T040** [P] [US2] `tests_mcp/test_error_unsupported_freq.py` — invoke
  with `freq="monthly"`; assert Pydantic validation rejects at the MCP
  boundary with a clear message referencing allowed values.
- [x] **T041** [P] [US2] `tests_mcp/test_bank_missing_fields.py` — mock
  library to return a DataFrame with `NaN`s in GrossProfit-derived columns;
  assert response contains `null` (not errors) for those columns and valid
  numerics elsewhere.
- [x] **T042** [P] [US2] `tests_mcp/test_no_stack_traces.py` — force the
  library mock to raise an arbitrary `Exception`; assert the MCP response is
  a well-formed `ErrorResponse` with `code="INTERNAL_ERROR"` and no traceback
  string in any field.

### Implementation for US2

- [x] **T043** [US2] Extend `finratioanalysis_mcp/server.py::_call_library`
  with a pre-validation step: regex-check ticker, catch `yfinance` / HTTP
  exceptions and map to `UPSTREAM_ERROR`; map empty/all-NaN DataFrames to
  `DATA_UNAVAILABLE` when the entire response would be unusable; everything
  else wrapped as `INTERNAL_ERROR`. Depends on T006, T009.
- [x] **T044** [US2] Add a top-level `try/except MCPError → error_response()`
  wrapper in the tool-dispatch helper so no tool leaks exceptions. Depends
  on T043.
- [x] **T045** [P] [US2] Document each error code in tool descriptions so
  LLMs can react appropriately (edit the 10 tool files; small descriptive
  addition only).

**Checkpoint**: US2 complete. T039–T042 all green. Running the integration
suite against a basket of 20 mixed-sector tickers yields ≥95% non-error
responses (SC-003).

---

## Phase 5: User Story 3 — `company_snapshot` aggregate tool (Priority: P3)

**Goal**: One-call fundamentals snapshot returning every ratio family with
per-section partial success (FR-001 bonus; spec US3 scenarios 1–2).

### Tests for US3 (write FIRST)

- [x] **T046** [P] [US3] `tests_mcp/tools/test_company_snapshot.py` —
  happy-path with all sections `status="ok"`; verify each section's `data`
  validates against the matching per-method contract.
- [x] **T047** [P] [US3] `tests_mcp/tools/test_company_snapshot_partial.py`
  — force CAPM to fail in the mock; assert `sections.capm.status="error"`
  with a valid `ErrorResponse` while all other sections remain `ok`.

### Implementation for US3

- [x] **T048** [US3] `finratioanalysis_mcp/tools/company_snapshot.py` —
  register `finratio_company_snapshot`; call all 10 per-method adapters
  inside try/except, assemble the `CompanySnapshot` shape per data-model.md.
  Depends on T026.
- [x] **T049** [US3] Import the new tool in `finratioanalysis_mcp/tools/__init__.py`.
  Depends on T048.

**Checkpoint**: US3 complete. `finratio_company_snapshot` visible in MCP
Inspector; happy path + partial-failure both pass.

---

## Phase 6: Integration Tests (live Yahoo Finance)

**Purpose**: End-to-end behavior against real data (Constitution III).

- [x] **T050** [P] `tests_mcp/test_integration_live.py` — mark
  `@pytest.mark.integration`; basket `["AAPL", "MSFT", "GOOGL", "JPM", "NVDA"]`;
  invoke each tool, assert contract compliance and non-null `ticker`/`Symbol`.
- [x] **T051** [P] `tests_mcp/test_integration_bank.py` — mark integration;
  JPM-only; asserts documented NaN behavior (no crashes) for GrossMargin etc.
- [x] **T052** [P] `tests_mcp/test_integration_recent_ipo.py` — mark
  integration; pick a recent IPO; assert `DATA_UNAVAILABLE` or `null` for
  3-yr CAGR.

---

## Phase 9: Technical Debt — Discovered During Integration Testing

**Source**: Live Yahoo Finance integration run (Phase 6, 2026-04-17).
These issues were found by running T050–T052 against real data. All three are
correctness gaps between the mock/contract layer and the real library surface.

### Mock & contract drift

- [ ] **T062** [P] Fix CAPM mock fixture and contract column names — real library
  returns `CAPM` and `Sharpe`; mocks and `contracts/finratio_capm.json` use
  `Beta` and `Expected_Return`. Update `tests_mcp/fixtures/library_schema.json`
  CAPM entry, regenerate the mock via `make_snapshot_df`, and align the contract.
  Verify `tests_mcp/tools/test_capm.py` still passes after the rename.

- [ ] **T063** [P] Fix `valuation_growth_metrics` mock fixture and contract
  column names — real library returns snake_case columns (`dividend_yield`,
  `payout_ratio`, `pe_ratio`, `forward_pe`, `ps_ratio`, `beta`, `ev_ebitda`,
  `fcf_yield`, `revenue_cagr_3y`, `net_income_cagr_3y`); mocks and contract use
  PascalCase names (`Revenue_Growth_3Y_CAGR`, `EPS_Growth_3Y_CAGR`, etc.).
  Update `library_schema.json`, contract, and `tests_mcp/tools/test_valuation_growth_metrics.py`.

### Library robustness (constitution Principle IV)

- [ ] **T064** Fix library `KeyError` on missing bank balance-sheet fields —
  `efficiency_ratios`, `liquidity_ratios`, `ccc`, and `z_score` raise `KeyError`
  when `Inventory`, `CurrentAssets`, etc. are absent (e.g., JPM). Constitution
  Principle IV mandates `NaN` return, not an exception. Each method must wrap
  `.loc[field]` access in a try/except (or use `.get`/`.reindex`) and substitute
  `NaN` for the missing row. Add targeted unit tests in `tests/` for a bank-like
  fixture with no Inventory/CurrentAssets columns. **Note**: this is a library
  change — requires a PATCH version bump and must not alter the DataFrame schema.

---

## Phase 7: LLM Evaluation (SC-005)

**Purpose**: Measure tool-selection accuracy per mcp-builder Phase 4.

- [ ] **T053** Author `specs/001-mcp-server/evaluation.xml` — 10 Q&A pairs
  (read-only, independent, verifiable, stable). Examples: "What is AAPL's
  latest yearly ROIC?", "Which of AAPL/MSFT/JPM has the lowest Altman Z-Score
  this year?", "What is NVDA's current P/E?".
- [ ] **T054** Verify each reference answer by invoking the matching tool
  directly and recording the value in an adjacent comment in the XML.
- [ ] **T055** Run `python .claude/skills/mcp-builder/scripts/evaluation.py
  specs/001-mcp-server/evaluation.xml`; record the pass rate. Target: ≥9/10.
  Depends on T053, T054, Phase 3 complete.

---

## Phase 8: Polish & Cross-Cutting

- [ ] **T056** [P] Update top-level `README.md` — add a "MCP Server" section
  linking to `specs/001-mcp-server/quickstart.md` and noting the
  `FinRatioAnalysis[mcp]` install extra.
- [ ] **T057** [P] Add a `CHANGELOG` entry for the new optional MCP extra
  (library version unchanged; MCP package is 0.1.0).
- [ ] **T058** Run `pytest tests/ tests_mcp/` end-to-end — confirm library
  test suite still green (no regressions) and MCP suite green.
- [ ] **T059** Walk through `specs/001-mcp-server/quickstart.md` on a clean
  venv on Windows and macOS/Linux (one each); fix any step that doesn't work
  verbatim.
- [ ] **T060** Manual MCP Inspector session: list tools, invoke 3 tools,
  confirm annotations `readOnlyHint=true` and `openWorldHint=true` are
  surfaced. Satisfies FR-015 acceptance.
- [ ] **T061** [P] Add uv publish workflow: append `[dependency-groups] dev`
  to `pyproject.toml` (pytest, jsonschema, build, twine) for `uv sync`
  parity, and update `PUBLISHING.md` + `QUICK_PUBLISH.md` with a `uv build`
  / `uv publish` section alongside the existing twine workflow. Verify the
  built wheel exposes `Provides-Extra: mcp` and ships the
  `finratioanalysis_mcp` package.

---

## Dependencies & Execution Order

### Phase dependencies

- Phase 1 (Setup) → no deps.
- Phase 2 (Foundational) → Phase 1 done. **Blocks all user stories.**
- Phase 3 (US1) → Phase 2 done. **MVP.**
- Phase 4 (US2) → Phase 2 done; best if US1 done for full tool surface.
- Phase 5 (US3) → US1 done (reuses all per-method tools).
- Phase 6 (Integration) → Phase 3/4/5 complete.
- Phase 7 (Evaluation) → Phase 3 done at minimum.
- Phase 8 (Polish) → everything else.

### Within a phase

- Tests marked [P] run in parallel.
- Tool files in `tools/` are fully independent → all [P] across T016–T025.
- Unit tests T027–T036 are [P] (different files).
- Integration tests T050–T052 are [P].

### Critical serial chain

`T001 → T002 → T009 → T026 → T037 → T048`
(setup → server skeleton → tool registration glue → markdown cross-edit →
aggregate tool).

---

## Parallel Example: tool implementation burst in Phase 3

```bash
# All 10 tool files + their unit tests can be opened in parallel:
Task: "Implement finratio_return_ratios in finratioanalysis_mcp/tools/return_ratios.py"
Task: "Implement finratio_efficiency_ratios in finratioanalysis_mcp/tools/efficiency_ratios.py"
...
Task: "Unit test for finratio_return_ratios in tests_mcp/tools/test_return_ratios.py"
Task: "Unit test for finratio_efficiency_ratios in tests_mcp/tools/test_efficiency_ratios.py"
...
```

---

## Implementation Strategy

### MVP path

1. Phase 1 → Phase 2 → Phase 3 (US1). **Stop. Validate with MCP Inspector.**
2. If Inspector walkthrough works, ship as `finratioanalysis_mcp==0.1.0`.

### Incremental delivery

- `0.1.0` → MVP (US1).
- `0.2.0` → + US2 (robustness) + integration suite.
- `0.3.0` → + US3 (`company_snapshot`) + evaluation suite.

### Constitution gate at each checkpoint

Re-verify Principles I, II, III, IV, V before merging. Library untouched →
Principle I/V automatic. DataFrame shapes preserved in adapters → Principle II.
Tests exist for every new tool → Principle III. NaN→null + structured errors
→ Principle IV.

---

## Notes

- `[P]` = different files, independent.
- Every tool file is self-contained — US1 tool tasks are maximally parallel.
- Tests MUST fail before the matching implementation is written (Principle III).
- Commit after each task or logical group; don't batch unrelated files.
- `z_score_plot()` is intentionally excluded from the tool surface — do not
  add it in a polish pass.
- No library modifications permitted in this feature branch. If friction
  appears, raise it as a separate spec, not a sneak-in.
