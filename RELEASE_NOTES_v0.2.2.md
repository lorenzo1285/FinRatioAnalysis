## v0.2.2 - Complete MCP Documentation on PyPI

### What's Fixed
- ✅ **Complete MCP documentation now visible on PyPI** - Full MCP Server section with all 11 tools documented
- ✅ **Claude Desktop integration guide** - Step-by-step setup instructions included in README
- ✅ **Enhanced package metadata** - Better discoverability with MCP/LLM keywords

### PyPI Package Now Includes
- 🔌 **MCP Server (LLM Integration)** section with:
  - List of all 11 financial analysis tools
  - Claude Desktop configuration examples
  - Example prompts to try
  - Quick setup guide
  - Advanced configuration options

### All MCP Tools Documented on PyPI
1. `finratio_return_ratios` - ROE, ROA, ROCE, ROIC, margins
2. `finratio_efficiency_ratios` - Asset turnover, FCF margin, reinvestment rate
3. `finratio_valuation_growth_metrics` - P/E, EV/EBITDA, FCF yield, CAGR
4. `finratio_historical_valuation_metrics` - Time series of P/E, EV/EBITDA, FCF yield
5. `finratio_leverage_ratios` - Debt-to-equity, equity ratio, debt ratio
6. `finratio_liquidity_ratios` - Current ratio, quick ratio, cash ratio
7. `finratio_ccc` - Cash Conversion Cycle (DIO, DSO, DPO)
8. `finratio_z_score` - Altman Z-Score bankruptcy prediction
9. `finratio_capm` - CAPM expected return and Sharpe ratio
10. `finratio_wacc` - Weighted Average Cost of Capital
11. `finratio_company_snapshot` - All metrics in one call

### Installation

```bash
# Standard installation
pip install FinRatioAnalysis

# With MCP server support for Claude Desktop
pip install "FinRatioAnalysis[mcp]"
```

### Quick Start with Claude Desktop

Add to your `claude_desktop_config.json`:
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

Then try prompts like:
- *"What's Apple's ROIC trend over the last 4 years?"*
- *"Compare WACC across AAPL, MSFT, and GOOGL"*
- *"Give me a full fundamentals snapshot of NVDA"*

### Technical Details
- No code changes from v0.2.1
- Only README documentation enhancement for PyPI visibility
- Package size: ~66KB (wheel and source distribution)
- All 273 tests passing

### Links
- **PyPI:** https://pypi.org/project/FinRatioAnalysis/0.2.2/
- **GitHub:** https://github.com/lorenzo1285/FinRatioAnalysis
- **Documentation:** See README on PyPI or GitHub
