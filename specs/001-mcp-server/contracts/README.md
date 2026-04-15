# Tool Contracts

One JSON Schema file per MCP tool. These schemas are the **authoritative
contract** between:
- the MCP client (LLM) — consumes `input` to format tool calls
- the MCP server — validates inputs, emits outputs matching `output`
- the contract tests in `tests_mcp/test_tool_contracts.py` — assert every
  response validates against the corresponding `output` schema

## File structure

Each file is a single JSON document with three top-level keys:

```json
{
  "name": "finratio_<method>",
  "description": "...",
  "annotations": {
    "readOnlyHint": true,
    "destructiveHint": false,
    "idempotentHint": true,
    "openWorldHint": true
  },
  "input": { /* JSON Schema for the tool's input object */ },
  "output": { /* JSON Schema for the tool's response */ }
}
```

## Shared input shape

Every tool shares the `TickerRequest` input shape defined in `data-model.md`:

```json
{
  "type": "object",
  "properties": {
    "ticker": {
      "type": "string",
      "minLength": 1,
      "maxLength": 10,
      "pattern": "^[A-Z0-9.\\-]+$",
      "description": "Upper-case ticker symbol. Supports '.' and '-' for share classes (e.g., BRK-B)."
    },
    "freq": {
      "type": "string",
      "enum": ["yearly", "quarterly"],
      "default": "yearly"
    },
    "response_format": {
      "type": "string",
      "enum": ["json", "markdown"],
      "default": "json"
    }
  },
  "required": ["ticker"],
  "additionalProperties": false
}
```

For brevity, each tool file references this via the literal shape (no `$ref`
resolution required for downstream consumers).

## Output conventions

- **Time-series tools** return an array of `PeriodRow` objects, each with a
  `date` string (ISO-8601) and one numeric field per library column.
- **Snapshot tools** return a single object with `Symbol` + metric fields.
- All numeric fields allow `null` to represent `NaN` / missing data (FR-004).
- On failure the response is an `ErrorResponse`:

  ```json
  {
    "code":    "INVALID_TICKER | UNSUPPORTED_FREQ | DATA_UNAVAILABLE | UPSTREAM_ERROR | INTERNAL_ERROR",
    "message": "string",
    "details": { }
  }
  ```

  The top-level response MUST match either the success `output` schema or the
  `ErrorResponse` schema — validated as `oneOf` in tests.

## Tool index

| File | Tool | Shape |
|---|---|---|
| `finratio_return_ratios.json` | `finratio_return_ratios` | time-series |
| `finratio_efficiency_ratios.json` | `finratio_efficiency_ratios` | time-series |
| `finratio_leverage_ratios.json` | `finratio_leverage_ratios` | time-series |
| `finratio_liquidity_ratios.json` | `finratio_liquidity_ratios` | time-series |
| `finratio_ccc.json` | `finratio_ccc` | time-series |
| `finratio_valuation_growth_metrics.json` | `finratio_valuation_growth_metrics` | snapshot |
| `finratio_historical_valuation_metrics.json` | `finratio_historical_valuation_metrics` | time-series |
| `finratio_z_score.json` | `finratio_z_score` | snapshot |
| `finratio_capm.json` | `finratio_capm` | snapshot |
| `finratio_wacc.json` | `finratio_wacc` | snapshot |
| `finratio_company_snapshot.json` | `finratio_company_snapshot` | composite |
