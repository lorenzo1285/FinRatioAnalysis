# FinRatioAnalysis

A comprehensive Python package for financial ratio analysis and fundamental analysis of publicly traded companies using real-time data from Yahoo Finance.

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

For detailed financial ratio formulas and interpretations:
- [Example Notebook](example/example.ipynb) - Complete walkthrough of all features including VCG analysis
- [CFI Financial Ratios Cheat Sheet](https://corporatefinanceinstitute.com/assets/CFI-Financial-Ratios-Cheat-Sheet-eBook.pdf)

## Version History

**Latest Version:**
- Added VCG (Value, Quality, Growth) metrics framework
- New `historical_valuation_metrics()` method
- Enhanced `return_ratios()` with ROIC
- Enhanced `efficiency_ratios()` with FCF Margin and Reinvestment Rate
- Enhanced `valuation_growth_metrics()` with EV/EBITDA and FCF Yield

## License

MIT License - See [LICENCE](LICENCE) file

## Author

**Lorenzo Cárdenas Cárdenas**
- GitHub: [@lorenzo1285](https://github.com/lorenzo1285)
- LinkedIn: [lorenzocardenas](https://www.linkedin.com/in/lorenzocardenas/)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Changelog

### Version 1.x (Latest)
- ✨ Added VCG (Value, Quality, Growth) analysis framework
- ✨ New method: `historical_valuation_metrics()` - Time series P/E, EV/EBITDA, FCF Yield
- ✨ Enhanced `return_ratios()` - Added ROIC (Return on Invested Capital)
- ✨ Enhanced `efficiency_ratios()` - Added FCF Margin and Reinvestment Rate
- ✨ Enhanced `valuation_growth_metrics()` - Added EV/EBITDA and FCF Yield
- 🐛 Fixed timezone compatibility issues in historical price lookups
- 📚 Updated documentation with VCG examples and API reference
- 📚 Enhanced example notebook with quarterly/yearly comparisons
