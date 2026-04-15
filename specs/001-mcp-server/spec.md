# Feature Specification: MCP Server for FinRatioAnalysis

**Feature Branch**: `001-mcp-server`
**Created**: 2026-04-15
**Status**: Draft
**Input**: User description: "Create an MCP so LLMs can use the FinRatioAnalysis library."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ask an LLM for a company's ratios and get real answers (Priority: P1)

An analyst chatting with an MCP-capable LLM (e.g., Claude Desktop, an IDE assistant,
or an internal agent) asks in natural language: *"What's Apple's ROIC and P/E for the
last four years?"* The LLM, through the MCP server, invokes FinRatioAnalysis against
live Yahoo Finance data and returns structured results the LLM can summarize,
compare, or chart.

**Why this priority**: This is the whole point of the feature — exposing the
library's core analytical methods so an LLM can answer fundamental-analysis
questions with real data instead of hallucinated numbers. Without this, the MCP
has no value.

**Independent Test**: Start the MCP server, connect any MCP-compliant client,
issue a tool call for `return_ratios(ticker="AAPL", freq="yearly")`, and verify a
structured response containing ROE, ROA, ROCE, ROIC, margins, and report dates
that matches what the Python library returns directly.

**Acceptance Scenarios**:

1. **Given** the MCP server is running and a client is connected, **When** the
   client requests the list of available tools, **Then** it receives one tool per
   public **data-returning** analytical method on `FinRatioAnalysis` (return,
   efficiency, leverage, liquidity, ccc, valuation growth, historical valuation,
   z_score, capm, wacc) with documented input schemas and descriptions.
   Side-effect methods like `z_score_plot()` (which renders a Plotly figure) are
   excluded from the tool surface.
2. **Given** a valid ticker and frequency, **When** the LLM invokes the
   `return_ratios` tool via MCP, **Then** the server returns a JSON payload whose
   shape mirrors the DataFrame-In/DataFrame-Out contract (array of period rows
   with named metric fields and ISO-formatted dates).
3. **Given** the LLM invokes a snapshot tool (e.g., `z_score`, `wacc`), **When**
   the call succeeds, **Then** the server returns a single-object JSON payload
   keyed by the documented column names (e.g., `Symbol`, `Z Score`, `Zone`).

---

### User Story 2 - Graceful handling of bad tickers and missing data (Priority: P2)

When the LLM passes an invalid ticker, an unsupported frequency, or requests a
metric that Yahoo Finance cannot supply for that company type (e.g., `GrossMargin`
for a bank), the MCP server returns a clear, machine-readable error or a
well-typed `null`/`NaN` so the LLM can explain the situation to the user instead
of crashing the conversation.

**Why this priority**: LLM-driven usage is inherently noisy — tickers get
misspelled, banks don't have the same fields as tech companies. Robust error
surfacing is required for a trustworthy agent experience, but it is secondary to
the core happy path.

**Independent Test**: Invoke tools with (a) a nonsense ticker `"ZZZZZ"`, (b)
`freq="monthly"`, and (c) a bank ticker (e.g., `JPM`) requesting metrics that rely
on `GrossProfit`. Verify each case returns a structured error or documented
`NaN`/`null` values — never an unhandled exception.

**Acceptance Scenarios**:

1. **Given** an invalid ticker, **When** any tool is invoked, **Then** the MCP
   response is a structured error object with a human-readable `message` and a
   stable `code` (e.g., `INVALID_TICKER`).
2. **Given** a bank ticker whose fallback logic yields `NaN` for some columns,
   **When** `return_ratios` is invoked, **Then** the response includes those rows
   with `null` for unavailable metrics and valid values for the rest.
3. **Given** an unsupported `freq` value, **When** any tool is invoked, **Then**
   the server rejects the call with a validation error referencing the allowed
   values (`yearly`, `quarterly`).

---

### User Story 3 - One-shot "full company snapshot" tool for agents (Priority: P3)

An LLM agent doing a holistic analysis wants a single call that returns every
available ratio family for a ticker, so it doesn't have to orchestrate ten tool
calls. A `company_snapshot` tool returns all ratio families in one structured
payload.

**Why this priority**: Quality-of-life improvement for agents. It does not enable
new capability — everything is reachable via the per-method tools in US1 — but it
reduces round-trips and LLM reasoning cost.

**Independent Test**: Invoke `company_snapshot(ticker="MSFT", freq="yearly")` and
verify the response contains sub-objects for each ratio family with the same
shapes US1 defines.

**Acceptance Scenarios**:

1. **Given** a valid ticker, **When** `company_snapshot` is invoked, **Then** the
   response contains keys for `return`, `efficiency`, `leverage`, `liquidity`,
   `ccc`, `valuation_growth`, `historical_valuation`, `z_score`, `capm`, `wacc`,
   each populated with the shape defined by the individual tool.
2. **Given** one sub-metric fails (e.g., CAPM cannot be computed), **When**
   `company_snapshot` runs, **Then** the remaining sections are populated and the
   failing section reports a per-section error object without aborting the whole
   response.

---

### Edge Cases

- **Rate limiting by Yahoo Finance**: rapid repeat calls from an agent may be
  throttled. The server should surface a retryable error code and not block the
  event loop.
- **Timezone-naive vs -aware timestamps**: historical price lookups must remain
  timezone-safe (already handled in the library) when serialized to JSON.
- **Newly IPO'd tickers** with less than three years of data: CAGR and historical
  series must return `null` rather than raising.
- **Non-English ticker metadata**: field names from yfinance are not guaranteed
  ASCII; JSON output MUST be UTF-8.
- **Concurrent tool calls from one client**: two overlapping requests for the same
  ticker must not corrupt shared cache state if caching is introduced.
- **Large payloads**: `historical_valuation_metrics` with quarterly frequency can
  produce many rows; responses should remain under MCP transport limits or paginate.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose an MCP server (stdio transport at minimum)
  that advertises a tool for each public analytical method of the
  `FinRatioAnalysis` class.
- **FR-002**: Each tool MUST declare a JSON Schema for its inputs covering at
  least `ticker` (string, required) and `freq` (enum: `yearly`, `quarterly`,
  default `yearly`), plus any method-specific parameters.
- **FR-003**: Each tool's response MUST be valid JSON whose structure mirrors the
  library's DataFrame contract: time-series methods return an ordered array of
  period objects with an ISO-8601 `date` field; snapshot methods return a single
  object.
- **FR-004**: The server MUST translate Python `NaN` values to JSON `null` and
  preserve numeric precision sufficient for financial analysis (at least 6
  significant digits).
- **FR-005**: The server MUST return structured error responses (with `code` and
  `message`) for invalid tickers, invalid frequencies, network failures, and
  missing-data conditions that cannot be represented as `null`.
- **FR-006**: The server MUST NOT crash or leak stack traces to the client on any
  library exception; all errors MUST be caught and converted to MCP error
  responses.
- **FR-007**: The server MUST be installable and runnable via a documented command
  (e.g., `python -m finratioanalysis_mcp` or a console script entry point) without
  requiring the user to write Python glue code.
- **FR-008**: Tool descriptions and parameter docs MUST be rich enough for an LLM
  to choose the correct tool from natural-language requests (include what each
  ratio means and when to use it).
- **FR-009**: The MCP server MUST NOT alter or wrap the library's public API —
  it is a thin adapter layer; behavior parity with direct library use is
  required.
- **FR-010**: Configuration (e.g., request timeout, log level, optional cache
  TTL) MUST be controllable via environment variables with sensible defaults.
- **FR-011**: The MCP server package MUST ship with its own test suite covering
  each tool's happy path and at least one error path, runnable under `pytest`.
- **FR-012**: Documentation MUST include a copy-pasteable configuration snippet
  for at least one reference MCP client (e.g., Claude Desktop `mcpServers` JSON).
- **FR-013**: Each tool MUST accept an optional `response_format` parameter with
  allowed values `json` (default) and `markdown`, and MUST render the same
  underlying data in the requested format — JSON for programmatic use, Markdown
  for human-readable presentation (tables for time-series, key/value lists for
  snapshots).
- **FR-014**: Tool names MUST use the `finratio_` service prefix and snake_case
  (e.g., `finratio_return_ratios`, `finratio_z_score`, `finratio_company_snapshot`)
  to avoid collisions with other MCP servers running alongside this one.
- **FR-015**: Every tool MUST declare MCP annotations `readOnlyHint=true`,
  `destructiveHint=false`, `idempotentHint=true`, and `openWorldHint=true` (the
  latter reflects dependency on the external Yahoo Finance data source).

### Key Entities *(include if feature involves data)*

- **Tool**: an MCP-exposed callable corresponding to one library method. Has a
  name, description, JSON input schema, and a response shape.
- **TickerRequest**: the common input envelope — `ticker` (symbol), `freq`
  (`yearly` | `quarterly`), plus tool-specific extras.
- **PeriodRow**: one row of a time-series response — `date` (ISO-8601) plus the
  metric fields defined by the underlying library method.
- **SnapshotObject**: a single-row response (e.g., for `z_score`, `wacc`,
  `valuation_growth_metrics`).
- **ErrorResponse**: `{ code: string, message: string, details?: object }` —
  returned for validation and runtime failures.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new user can configure the MCP server in an MCP-capable client
  and obtain Apple's ROIC from a natural-language prompt in under 5 minutes from
  a clean install.
- **SC-002**: 100% of the library's public analytical methods are reachable as
  MCP tools, verified by a contract test.
- **SC-003**: For a representative basket of 20 tickers across sectors (incl.
  banks and recent IPOs), 95% of tool invocations complete without raising; the
  remaining 5% return structured `ErrorResponse` rather than crashing.
- **SC-004**: End-to-end tool-call latency for a single-ticker, single-method
  request is under 5 seconds on a typical residential connection (dominated by
  Yahoo Finance I/O).
- **SC-005**: An LLM given only the tool descriptions selects the correct tool
  for at least 9 of 10 representative analyst prompts in an evaluation set.

## Assumptions

- MCP clients used to consume this server support the current MCP specification
  (tools, JSON Schema inputs, structured errors). Stdio transport is sufficient
  for v1; HTTP/SSE transport is out of scope unless explicitly requested.
- Yahoo Finance remains the sole data source; no API keys are required.
- Users running the MCP server have outbound internet access to Yahoo Finance.
- The MCP server ships alongside `FinRatioAnalysis` (either as a subpackage or a
  companion package) and depends on the same Python version floor (3.9+ in
  practice, 3.7+ declared).
- Authentication and multi-tenant access control are out of scope; the server
  runs locally under the user's own credentials/environment.
- Caching, rate-limiting, and persistent storage are NOT required for v1 but
  are allowed behind environment-variable flags if cheap to add.
- The existing DataFrame-In/DataFrame-Out contract (per the constitution) is the
  source of truth for response shapes; any drift is a library-side change, not
  an MCP-side change.
