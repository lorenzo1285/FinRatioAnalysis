# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2026-04-17

### Added
- **MCP Server Support**: New optional `[mcp]` install extra enables LLM integration via Model Context Protocol
  - Install with: `pip install FinRatioAnalysis[mcp]`
  - Exposes all 10 analytical methods as MCP tools for Claude Desktop, IDE assistants, and other MCP-capable clients
  - Includes 11th aggregate tool `finratio_company_snapshot` for one-call fundamentals
  - Command-line entry point: `finratioanalysis-mcp` or `python -m finratioanalysis_mcp`
  - See [quickstart guide](specs/001-mcp-server/quickstart.md) for setup instructions

### Changed
- Minimum Python version raised to 3.10+ (for MCP optional dependencies only; core library remains compatible with 3.7+)
- Added `finratioanalysis_mcp` package to distribution alongside core `FinRatioAnalysis` library

### Technical Details
- MCP server built with FastMCP (official Python MCP SDK)
- JSON and Markdown response formats supported
- Structured error responses (no stack traces to clients)
- Comprehensive test coverage: 30+ unit tests, contract tests, and integration tests with live Yahoo Finance data
- LLM evaluation suite: 10-question Q&A benchmark included

---

## [0.2.0] - 2026-01-12

### Added
- **VCG (Value, Quality, Growth) Metrics Framework**
  - New `historical_valuation_metrics()` method providing time series data for P/E Ratio, EV/EBITDA, and FCF Yield
  - Enhanced `return_ratios()` with ROIC (Return on Invested Capital)
  - Enhanced `efficiency_ratios()` with FCF Margin and Reinvestment Rate
  - Enhanced `valuation_growth_metrics()` with EV/EBITDA and FCF Yield

### Fixed
- Timezone compatibility issues in historical price lookups
- DataFrame column consistency across all methods

---

## [0.1.x] - Earlier Versions

See git commit history for earlier changes.
