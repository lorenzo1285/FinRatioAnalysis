# FinRatioAnalysis

[![PyPI version](https://badge.fury.io/py/FinRatioAnalysis.svg)](https://badge.fury.io/py/FinRatioAnalysis)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP Support](https://img.shields.io/badge/MCP-Enabled-purple.svg)](https://modelcontextprotocol.io)
[![Downloads](https://static.pepy.tech/badge/finratioanalysis)](https://pepy.tech/project/finratioanalysis)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/FinRatioAnalysis)](https://pypi.org/project/FinRatioAnalysis/)

A comprehensive Python package for financial ratio analysis and fundamental analysis of publicly traded companies using real-time data from Yahoo Finance.

**🆕 Now with MCP Server Support** - Integrate financial analysis directly into Claude Desktop and other LLM applications!

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [MCP Server (LLM Integration)](#mcp-server-llm-integration)
- [VCG (Value, Quality, Growth) Analysis](#vcg-value-quality-growth-analysis)
- [API Reference](#api-reference)
- [Examples](#example-analyzing-multiple-companies)
- [Testing](#testing)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

## Features

**Profitability & Return Metrics:**
- Return on Equity (ROE)
- Return on Assets (ROA)
- Return on Capital Employed (ROCE)
- **NEW: Return on Invested Capital (ROIC)** - Quality metric for capital efficiency
- Gross Margin, Operating Margin, Net Profit Margin

**Valuation & Growth Metrics:**
- **NEW: Historical P/E Ratio** - Time series of Price-to-Earnings
- **NEW: Historical EV/EBITDA** - Enterprise Value to EBITDA over time
- **NEW: Historical FCF Yield** - Free Cash Flow Yield trends
- Current P/E, P/S, Forward P/E
- Dividend Yield & Payout Ratio
- Revenue & Net Income CAGR (3-year growth)
- Beta (market volatility)

**Leverage & Solvency:**
- Debt-to-Equity Ratio
- Equity Ratio, Debt Ratio
- Interest Coverage Ratios

**Efficiency Ratios:**
- Asset Turnover
- Receivables Turnover
- Inventory Turnover
- Fixed Asset Turnover
- **NEW: FCF Margin** - Free Cash Flow efficiency
- **NEW: Reinvestment Rate** - Growth capital allocation

**Liquidity Analysis:**
- Current Ratio, Quick Ratio, Cash Ratio
- Days Inventory Ratio (DIR)
- Operating Cash Flow Ratios

**Advanced Metrics:**
- Cash Conversion Cycle (CCC)
- Altman Z-Score (bankruptcy prediction)
- Capital Asset Pricing Model (CAPM)
- Sharpe Ratio
- Weighted Average Cost of Capital (WACC)

**Special Features:**
- ✅ **VCG (Value, Quality, Growth) Analysis Framework**
- ✅ **Historical valuation metrics with time series data**
- ✅ Supports both tech companies and financial institutions (banks)
- ✅ Automatic fallback logic for missing financial data
- ✅ Quarterly and yearly data frequency
- ✅ Interactive Z-Score visualization with Plotly
- ✅ Comprehensive unit and integration tests

## Installation

### Standard Installation

```bash
pip install FinRatioAnalysis
```

### With MCP Server Support (for LLM integration)

```bash
pip install "FinRatioAnalysis[mcp]"
```

**Dependencies** (automatically installed):
- `yfinance` - Real-time financial data
- `pandas` - Data manipulation
- `numpy` - Numerical operations
- `plotly` - Interactive visualizations
- `requests` - API calls

## Quick Start

```python
from FinRatioAnalysis import FinRatioAnalysis

# Create analyzer instance
apple = FinRatioAnalysis('AAPL', freq='yearly')  # freq: 'yearly' or 'quarterly'

# Calculate profitability ratios (now includes ROIC)
returns = apple.return_ratios()
print(returns)  # ROE, ROA, ROCE, ROIC, Gross Margin, Operating Margin, Net Profit

# Calculate efficiency ratios (now includes FCF Margin & Reinvestment Rate)
efficiency = apple.efficiency_ratios()
print(efficiency)  # Asset Turnover, FCF_Margin, ReinvestmentRate, etc.

# Get valuation & growth metrics (current market values)
valuation = apple.valuation_growth_metrics()
print(valuation)  # P/E, EV/EBITDA, FCF Yield, Revenue CAGR, etc.

# NEW: Historical valuation metrics (time series with dates)
historical_val = apple.historical_valuation_metrics()
print(historical_val)  # P/E, EV/EBITDA, FCF Yield for each period

# Calculate leverage ratios
leverage = apple.leverage_ratios()
print(leverage)  # Debt-to-Equity, Equity Ratio, Debt Ratio

# Calculate liquidity ratios
liquidity = apple.liquidity_ratios()
print(liquidity)  # Current Ratio, Quick Ratio, Cash Ratio, etc.

# Cash Conversion Cycle
ccc = apple.ccc()
print(ccc)  # DIO, DSO, DPO, CCC

# Altman Z-Score (bankruptcy risk)
z_score = apple.z_score()
print(z_score)  # Z-Score value and classification

# Visualize Z-Score
apple.z_score_plot()  # Interactive Plotly chart

# CAPM and Sharpe Ratio
capm = apple.capm()
print(capm)  # Expected Return, Sharpe Ratio

# Weighted Average Cost of Capital
wacc = apple.wacc()
print(wacc)  # WACC percentage
```

## MCP Server (LLM Integration)

🔌 **Model Context Protocol (MCP) Support** - FinRatioAnalysis now includes an optional MCP server that enables LLMs like Claude to perform financial analysis through natural language queries.

### Available MCP Tools

The MCP server exposes **11 financial analysis tools**:

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
11. `finratio_company_snapshot` - **All metrics in one call** (aggregate tool)

### Quick Setup

FinRatioAnalysis now includes an optional MCP (Model Context Protocol) server that enables LLMs like Claude to perform financial analysis through natural language:

```bash
# Install with MCP support
pip install "FinRatioAnalysis[mcp]"

# Start the MCP server (standalone mode)
finratioanalysis-mcp
# or
python -m finratioanalysis_mcp
```

### Claude Desktop Integration

**Use Cases:**
- Ask Claude Desktop: *"What's Apple's ROIC trend over the last 4 years?"*
- Natural language queries automatically invoke the right financial tools
- Get fundamentals analysis without writing code

**Quick Setup for Claude Desktop:**

1. **Find your Claude Desktop config file:**
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

2. **Add the MCP server configuration:**

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

**Alternative with `uv` (if you use uv for package management):**
```json
{
  "mcpServers": {
    "finratioanalysis": {
      "command": "uv",
      "args": ["run", "--with", "finratioanalysis[mcp]", "finratioanalysis-mcp"]
    }
  }
}
```

3. **Restart Claude Desktop** completely (quit and reopen) and look for the 🔌 connector icon!

**Example prompts to try:**
- *"What's Apple's ROIC trend over the last 4 years?"*
- *"Compare WACC across AAPL, MSFT, and GOOGL"*
- *"Give me a full fundamentals snapshot of NVDA"*
- *"Calculate the Altman Z-Score for Tesla and interpret the result"*
- *"Show me the historical P/E ratio and EV/EBITDA for Microsoft"*
- *"What's the Cash Conversion Cycle for Amazon?"*

📚 For detailed setup instructions and troubleshooting, see the [MCP Quickstart Guide](specs/001-mcp-server/quickstart.md).

### Advanced Configuration

**Using `uv` package manager:**
```json
{
  "mcpServers": {
    "finratioanalysis": {
      "command": "uv",
      "args": ["run", "--with", "finratioanalysis[mcp]", "finratioanalysis-mcp"]
    }
  }
}
```

**With local development directory:**
```json
{
  "mcpServers": {
    "finratioanalysis": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/FinRatioAnalysis", "python", "-m", "finratioanalysis_mcp"],
      "env": {
        "FINRATIO_MCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

## VCG (Value, Quality, Growth) Analysis

The package now includes comprehensive VCG metrics for fundamental analysis:

```python
from FinRatioAnalysis import FinRatioAnalysis
import pandas as pd

analyzer = FinRatioAnalysis('AAPL', freq='yearly')

# VALUE METRICS - Historical trends
historical = analyzer.historical_valuation_metrics()
print("Historical Valuation:")
print(historical[['PE_Ratio', 'EV_EBITDA', 'FCF_Yield']])

# QUALITY METRICS - Profitability & efficiency
quality = pd.concat([
    analyzer.return_ratios()[['ROIC', 'ROE']],
    analyzer.efficiency_ratios()[['FCF_Margin']]
], axis=1)
print("\nQuality Metrics:")
print(quality)

# GROWTH METRICS - Revenue & investment trends
growth = analyzer.valuation_growth_metrics()[['revenue_cagr_3y', 'net_income_cagr_3y']]
reinvestment = analyzer.efficiency_ratios()[['ReinvestmentRate']]
print("\nGrowth Metrics:")
print(pd.concat([growth.T, reinvestment], axis=1))
```

## Quarterly vs Yearly Analysis

```python
# Yearly analysis (default) - 4 annual periods
yearly = FinRatioAnalysis('AAPL', freq='yearly')
print(yearly.historical_valuation_metrics())  # 4 years of data

# Quarterly analysis - 4 quarterly periods
quarterly = FinRatioAnalysis('AAPL', freq='quarterly')
print(quarterly.historical_valuation_metrics())  # Last 4 quarters
print(quarterly.return_ratios())  # Quarterly ROIC, ROE, etc.
```

## Example: Analyzing Multiple Companies

```python
from FinRatioAnalysis import FinRatioAnalysis
import pandas as pd

tickers = ['AAPL', 'MSFT', 'GOOGL', 'JPM']  # Tech + Bank
results = {}

for ticker in tickers:
    analyzer = FinRatioAnalysis(ticker, freq='yearly')
    
    # Get latest values
    returns = analyzer.return_ratios().iloc[0]
    leverage = analyzer.leverage_ratios().iloc[0]
    valuation = analyzer.valuation_growth_metrics().iloc[0]
    z = analyzer.z_score().iloc[0]
    wacc = analyzer.wacc()
    
    results[ticker] = {
        'ROE': returns['ROE'],
        'ROIC': returns['ROIC'],
        'Debt/Equity': leverage['DebtEquityRatio'],
        'P/E': valuation['pe_ratio'],
        'EV/EBITDA': valuation['ev_ebitda'],
        'FCF Yield': valuation['fcf_yield'],
        'Revenue CAGR': valuation['revenue_cagr_3y'],
        'Z-Score': z['Z Score'],
        'WACC': wacc['WACC'].iloc[0]
    }

df = pd.DataFrame(results).T
print(df.round(2))
```

## API Reference

### Core Methods

#### `return_ratios() -> pd.DataFrame`
Returns profitability metrics with dates as index:
- `ROE` - Return on Equity
- `ROA` - Return on Assets  
- `ROCE` - Return on Capital Employed
- **`ROIC`** - Return on Invested Capital (NEW)
- `GrossMargin`, `OperatingMargin`, `NetProfit`

#### `efficiency_ratios() -> pd.DataFrame`
Returns efficiency metrics with dates as index:
- `AssetTurnover`, `ReceivableTurnover`, `InventoryTurnover`, `FixedAssetTurnover`
- **`FCF_Margin`** - Free Cash Flow Margin (NEW)
- **`ReinvestmentRate`** - Capital reinvestment rate (NEW)

#### `valuation_growth_metrics() -> pd.DataFrame`
Returns current market valuation metrics (single row):
- `pe_ratio`, `forward_pe`, `ps_ratio`
- **`ev_ebitda`** - Enterprise Value / EBITDA (NEW)
- **`fcf_yield`** - Free Cash Flow Yield (NEW)
- `dividend_yield`, `payout_ratio`, `beta`
- `revenue_cagr_3y`, `net_income_cagr_3y`

#### `historical_valuation_metrics() -> pd.DataFrame` (NEW)
Returns historical valuation metrics with dates as index:
- `Market_Cap` - Historical market capitalization
- `PE_Ratio` - Price-to-Earnings for each period
- `EV_EBITDA` - Enterprise Value / EBITDA for each period
- `FCF_Yield` - Free Cash Flow Yield for each period

**Works with both yearly and quarterly data!**

#### `leverage_ratios() -> pd.DataFrame`
Returns leverage metrics with dates as index:
- `DebtEquityRatio`, `EquityRatio`, `DebtRatio`

#### `liquidity_ratios() -> pd.DataFrame`
Returns liquidity metrics with dates as index:
- `CurrentRatio`, `QuickRatio`, `CashRatio`
- `DIR`, `TIE`, `TIE_CB`, `CAPEX_OpCash`, `OpCashFlow`

#### `ccc() -> pd.DataFrame`
Returns Cash Conversion Cycle metrics with dates as index:
- `DIO`, `DSO`, `DPO`, `CCC`

#### `z_score() -> pd.DataFrame`
Returns Altman Z-Score for bankruptcy prediction (single row):
- `Symbol`, `Z Score`, `Zone`

#### `z_score_plot() -> None`
Displays interactive Plotly gauge chart of Z-Score

#### `capm() -> pd.DataFrame`
Returns CAPM metrics (single row):
- `Symbol`, `CAPM`, `Sharpe`

#### `wacc() -> pd.DataFrame`
Returns Weighted Average Cost of Capital (single row):
- `Symbol`, `WACC`

## Supported Company Types

The package intelligently handles different types of companies:

**Tech/Manufacturing Companies:** Full metrics including ROCE, ROIC, Gross Margin, Operating Margin, FCF Margin

**Financial Institutions (Banks):** Automatically adapts metrics - uses alternative calculations when standard fields (like GrossProfit, CurrentLiabilities) are unavailable

## What's New in Latest Version

### VCG (Value, Quality, Growth) Metrics
- **ROIC** - Added to `return_ratios()` for quality assessment
- **Historical Valuation Metrics** - New `historical_valuation_metrics()` method provides time series of P/E, EV/EBITDA, and FCF Yield
- **FCF Margin** - Added to `efficiency_ratios()` to measure cash flow efficiency
- **Reinvestment Rate** - Added to `efficiency_ratios()` to track growth capital allocation
- **Enhanced Valuation** - `valuation_growth_metrics()` now includes EV/EBITDA and FCF Yield

### Key Improvements
- All VCG metrics support both yearly and quarterly analysis
- Historical valuation metrics match the format of other ratio methods (dates in index)
- Automatic timezone handling for stock price data
- Comprehensive error handling and fallback logic

## Testing

The package includes comprehensive tests:

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/test_return_ratios.py
pytest tests/test_efficiency_ratios.py
pytest tests/test_valuation_growth_metrics.py
pytest tests/test_integration_real_data.py
pytest -m integration  # Real data tests only
```

## Documentation

### Examples and Guides

- 📓 [**Python Library Examples**](example/example.ipynb) - Complete walkthrough of all features including VCG analysis
- 🔌 [**MCP Server Examples**](example/example_mcp.ipynb) - Demonstration of all 11 MCP tools with live data
- 📚 [**MCP Quickstart Guide**](specs/001-mcp-server/quickstart.md) - Claude Desktop setup and configuration
- 📄 [**MCP Technical Spec**](specs/001-mcp-server/spec.md) - Detailed MCP implementation documentation

### Reference Materials

- [CFI Financial Ratios Cheat Sheet](https://corporatefinanceinstitute.com/assets/CFI-Financial-Ratios-Cheat-Sheet-eBook.pdf) - Detailed formulas and interpretations
- [Model Context Protocol](https://modelcontextprotocol.io) - Learn about MCP for LLM integration

## License

MIT License - See [LICENCE](LICENCE) file

## Author

**Lorenzo Cárdenas Cárdenas**
- GitHub: [@lorenzo1285](https://github.com/lorenzo1285)
- LinkedIn: [lorenzocardenas](https://www.linkedin.com/in/lorenzocardenas/)

## Contributing

Contributions are welcome! Here's how you can help:

1. **Report bugs** - Open an issue on [GitHub Issues](https://github.com/lorenzo1285/FinRatioAnalysis/issues)
2. **Suggest features** - Share your ideas for new ratios or metrics
3. **Submit PRs** - Fork the repo, make your changes, and submit a pull request
4. **Improve docs** - Help make the documentation clearer
5. **Add tests** - Expand test coverage for edge cases

### Development Setup

```bash
# Clone the repository
git clone https://github.com/lorenzo1285/FinRatioAnalysis.git
cd FinRatioAnalysis

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[mcp]"
pip install pytest pytest-mock jsonschema

# Run tests
pytest
pytest tests_mcp/  # MCP server tests
```

Please ensure all tests pass before submitting a PR!

## Changelog

### Version 0.2.1 (April 2026) - Current Release

**Major Features:**
- 🆕 **MCP Server Support** - Enable LLM integration with Claude Desktop and other MCP clients
  - 11 financial analysis tools exposed via Model Context Protocol
  - Natural language querying of financial ratios
  - Structured JSON and Markdown response formats
  - See [CHANGELOG.md](CHANGELOG.md) for complete details

**Enhancements:**
- ✨ Added VCG (Value, Quality, Growth) analysis framework
- ✨ New method: `historical_valuation_metrics()` - Time series P/E, EV/EBITDA, FCF Yield
- ✨ Enhanced `return_ratios()` - Added ROIC (Return on Invested Capital)
- ✨ Enhanced `efficiency_ratios()` - Added FCF Margin and Reinvestment Rate
- ✨ Enhanced `valuation_growth_metrics()` - Added EV/EBITDA and FCF Yield
- 🐛 Fixed timezone compatibility issues in historical price lookups
- 📚 Updated documentation with VCG examples and API reference
- 📚 Enhanced example notebook with quarterly/yearly comparisons
- 🧪 Comprehensive test suite: 273 tests (library + MCP server)

For detailed version history, see [CHANGELOG.md](CHANGELOG.md).
