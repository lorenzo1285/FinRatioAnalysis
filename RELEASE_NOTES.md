## Summary

Adds Model Context Protocol (MCP) server support to enable LLM integration with financial analysis tools.

## Major Features
- 🆕 MCP server with 11 financial analysis tools
- 🔌 Claude Desktop integration support  
- 📊 All existing ratios exposed via natural language queries
- 📚 Comprehensive documentation and examples
- 🧪 Full test coverage (273 tests)

## What's Included
- New `finratioanalysis_mcp` package with FastMCP server
- Optional `[mcp]` install extra for LLM dependencies
- Example notebook demonstrating all MCP tools
- Enhanced documentation (README, CONTRIBUTING, quickstart)
- GitHub community files (issue templates, PR template, FUNDING)
- Multi-platform CI/CD testing (Ubuntu, Windows, macOS)

## Installation

### Standard Installation
```bash
pip install FinRatioAnalysis
```

### With MCP Server Support
```bash
pip install "FinRatioAnalysis[mcp]"
```

## Claude Desktop Setup

1. Install with MCP support: `pip install "FinRatioAnalysis[mcp]"`
2. Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "finratioanalysis": {
      "command": "python",
      "args": ["-m", "finratioanalysis_mcp"]
    }
  }
}
```
3. Restart Claude Desktop and start analyzing!

## Example Queries
- "What's Apple's ROIC trend over the last 4 years?"
- "Calculate the Altman Z-Score for Tesla"
- "Compare WACC across AAPL, MSFT, and GOOGL"
- "Give me a full fundamentals snapshot of NVIDIA"

## Breaking Changes
None - fully backward compatible with existing library usage

## Verified With
- Python 3.10, 3.11, 3.12, 3.13
- Windows 11, Ubuntu, macOS
- Claude Desktop integration working

See [CHANGELOG.md](https://github.com/lorenzo1285/FinRatioAnalysis/blob/main/CHANGELOG.md) for complete details.
