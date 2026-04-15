# Quickstart: FinRatioAnalysis MCP Server

Five-minute path from clean machine to an LLM answering questions with
real financial data via MCP.

---

## 1. Install

```bash
pip install "FinRatioAnalysis[mcp]"
```

This installs the core library plus the MCP adapter (`finratioanalysis_mcp`)
and its dependencies (`mcp`, `pydantic>=2`).

Verify:

```bash
python -m finratioanalysis_mcp --help
# or
finratioanalysis-mcp --help
```

You should see the server banner and available flags.

---

## 2. Smoke-test with the MCP Inspector

The MCP Inspector is the official tool for poking at an MCP server without an
LLM in the loop.

```bash
npx @modelcontextprotocol/inspector python -m finratioanalysis_mcp
```

In the Inspector UI:
1. Open the **Tools** tab — you should see 11 `finratio_*` tools listed.
2. Select `finratio_return_ratios`, set `ticker=AAPL`, `freq=yearly`, and **Run**.
3. Inspect the JSON response: an array of period rows with `date`, `ROE`,
   `ROA`, `ROCE`, `ROIC`, `GrossMargin`, `OperatingMargin`, `NetProfit`.

---

## 3. Wire into Claude Desktop

Edit your Claude Desktop config:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

Add an entry under `mcpServers`:

```json
{
  "mcpServers": {
    "finratioanalysis": {
      "command": "python",
      "args": ["-m", "finratioanalysis_mcp"],
      "env": {
        "FINRATIO_MCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

Restart Claude Desktop. The `finratioanalysis` server should appear in the
tools indicator.

---

## 4. Ask your first question

In Claude Desktop, try:

> *"What is Apple's ROIC and P/E ratio for the last four years? Summarize the
> trend."*

Claude will:
1. Call `finratio_return_ratios(ticker="AAPL", freq="yearly")` for ROIC.
2. Call `finratio_historical_valuation_metrics(ticker="AAPL", freq="yearly")`
   for historical P/E.
3. Merge and narrate the result.

Other prompts to try:
- *"Compute the Altman Z-Score for JPM and classify the zone."*
- *"Compare WACC across AAPL, MSFT, and GOOGL."*
- *"Give me a full fundamentals snapshot of NVDA."* (triggers
  `finratio_company_snapshot`)

---

## 5. Markdown output (optional)

For a human-readable rendering in tools that display Markdown, pass
`response_format="markdown"`:

```text
finratio_return_ratios(ticker="AAPL", freq="yearly", response_format="markdown")
```

Returns a Markdown table instead of JSON — useful when the client renders
tool output verbatim.

---

## 6. Configuration

All optional, env-var driven:

| Env var | Default | Purpose |
|---|---|---|
| `FINRATIO_MCP_LOG_LEVEL` | `INFO` | Python logging level. |
| `FINRATIO_MCP_TIMEOUT_SECONDS` | `15` | Per-tool wall-clock budget. |
| `FINRATIO_MCP_DEFAULT_FREQ` | `yearly` | Default if client omits `freq`. |
| `FINRATIO_MCP_CACHE_TTL_SECONDS` | `0` | In-memory response cache TTL (0 = off). |

Set inside Claude Desktop's `env` block in the config above.

---

## 7. Troubleshooting

- **`INVALID_TICKER` error**: the ticker string didn't match `^[A-Z0-9.\-]+$` or
  yfinance returned no metadata. Uppercase the symbol; for dual-class shares,
  use Yahoo's notation (`BRK-B`, not `BRK.B`).
- **`DATA_UNAVAILABLE`**: the ticker is too new (e.g., <3 years of statements
  for CAGR) or yfinance is missing fields for this company type. Expected for
  some banks and recent IPOs.
- **`UPSTREAM_ERROR`**: Yahoo Finance network/throttling issue — retry after a
  few seconds. Increase `FINRATIO_MCP_TIMEOUT_SECONDS` if on a slow link.
- **Server doesn't appear in Claude Desktop**: check the JSON config is valid
  (use `jq . < claude_desktop_config.json`) and that `python -m
  finratioanalysis_mcp` runs successfully in your shell.

---

## 8. Next steps for contributors

- Run the MCP test suite: `pytest tests_mcp/`
- Run the integration tests against live data: `pytest tests_mcp/ -m integration`
- Run the LLM evaluation: `python .claude/skills/mcp-builder/scripts/evaluation.py specs/001-mcp-server/evaluation.xml`
