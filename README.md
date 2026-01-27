# FinRatioAnalysis (Package Under maintenance)

A comprehensive Python package for financial ratio analysis and fundamental analysis of publicly traded companies using real-time data from Yahoo Finance.

## Features

**Profitability & Return Metrics:**
- Return on Equity (ROE)
- Return on Assets (ROA)
- Return on Capital Employed (ROCE)
- Gross Margin, Operating Margin, Net Profit Margin

**Leverage & Solvency:**
- Debt-to-Equity Ratio
- Equity Ratio, Debt Ratio
- Interest Coverage Ratios

**Efficiency Ratios:**
- Asset Turnover
- Receivables Turnover
- Inventory Turnover
- Fixed Asset Turnover

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
- ✅ Supports both tech companies and financial institutions (banks)
- ✅ Automatic fallback logic for missing financial data
- ✅ Quarterly and yearly data frequency
- ✅ Interactive Z-Score visualization with Plotly
- ✅ 108 comprehensive unit and integration tests

## Installation

```bash
pip install FinRatioAnalysis
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

# Calculate profitability ratios
returns = apple.return_ratios()
print(returns)  # ROE, ROA, ROCE, Gross Margin, Operating Margin, Net Profit

# Calculate leverage ratios
leverage = apple.leverage_ratios()
print(leverage)  # Debt-to-Equity, Equity Ratio, Debt Ratio

# Calculate efficiency ratios
efficiency = apple.efficiency_ratios()
print(efficiency)  # Asset Turnover, Receivables Turnover, etc.

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
capm = apple.capm(market_ticker='^GSPC')  # S&P 500 as market
print(capm)  # Beta, Expected Return, Sharpe Ratio

# Weighted Average Cost of Capital
wacc = apple.wacc(market_ticker='^GSPC')
print(wacc)  # WACC percentage
```

## Example: Analyzing Multiple Companies

```python
from FinRatioAnalysis import FinRatioAnalysis
import pandas as pd

tickers = ['AAPL', 'MSFT', 'GOOGL', 'JPM']  # Tech + Bank
results = {}

for ticker in tickers:
    analyzer = FinRatioAnalysis(ticker, freq='yearly')
    results[ticker] = {
        'ROE': analyzer.return_ratios()['ROE'].iloc[0],
        'Debt/Equity': analyzer.leverage_ratios()['DebtEquityRatio'].iloc[0],
        'Z-Score': analyzer.z_score()['Z-score'].iloc[0],
        'WACC': analyzer.wacc()['WACC'].iloc[0]
    }

df = pd.DataFrame(results).T
print(df)
```

## Supported Company Types

The package intelligently handles different types of companies:

**Tech/Manufacturing Companies:** Full metrics including ROCE, Gross Margin, Operating Margin

**Financial Institutions (Banks):** Automatically adapts metrics - uses alternative calculations when standard fields (like GrossProfit, CurrentLiabilities) are unavailable

## Documentation

For detailed financial ratio formulas and interpretations:
- [CFI Financial Ratios Cheat Sheet](https://corporatefinanceinstitute.com/assets/CFI-Financial-Ratios-Cheat-Sheet-eBook.pdf)

## Testing

The package includes 108 comprehensive tests:

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/test_return_ratios.py
pytest tests/test_integration_real_data.py
pytest -m integration  # Real data tests only
```

## License

MIT License - See [LICENCE](LICENCE) file

## Author

**Lorenzo Cárdenas Cárdenas**
- GitHub: [@lorenzo1285](https://github.com/lorenzo1285)
- LinkedIn: [lorenzocardenas](https://www.linkedin.com/in/lorenzocardenas/)

## Contributing

<<<<<<< Updated upstream
[![linkedin](https://www.linkedin.com/in/lorenzocardenas/)](https://www.linkedin.com/in/lorenzocardenas/)


  
## Installation

Install FinanceAnalysis, yahoo finance, pandas-datareader and plotly  with pip

```bash
  pip install yfinance
  pip install FinRatioAnalysis
  pip install pandas-datareader
  pip install plotly
```
=======
Contributions are welcome! Please feel free to submit a Pull Request.
>>>>>>> Stashed changes
