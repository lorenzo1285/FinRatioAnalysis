## FinRatioAnalysis (Package Under maintenance) 

Finacial Ratio Analysis Project: 

-Return Analysis

-Margin Analysis

-Leverage Analysis

-Efficiency Analysis

-Liquidity Analysis

-Cash Convertion Cicle (CCC)

-Altman Z Score

-Capital Asset Pricing Model (CAPM)

-Weighted Average Cost of Capital (WACC)

## Documentation

[Documentation](https://corporatefinanceinstitute.com/assets/CFI-Financial-Ratios-Cheat-Sheet-eBook.pdf)

Quick Start.
```bash
  #Packages:
    pip install yfinanc
    pip install FinRatioAnalysis
    pip install pandas-datareader
    pip install plotly

  #Import:
    import yfinance as yf
    import pandas as pd 
    import numpy as np
    import pandas_datareader as pdr
    import plotly.graph_objects as go
    import datetime as dt 
    from FinRatioAnalysis import FinRatioAnalysis

  #Create an Objet:

  AAPL = FinRatioAnalysis('AAPL', 'yearly') # Frequency most be 'quarterly' or 'yearly'

  #Available methods:

  AAPL.ReturnRatios()
  AAPL.LeverageRatios()
  AAPL.EfficiencyRatios()
  AAPL.LiquidityRatios()
  AAPL.CCC()
  AAPL.z_score()
  AAPL.z_score_plot()
  AAPL.CAPM()
  AAPL.WACC()
```

## Authors

- [@lorenzo1285](https://github.com/lorenzo1285)


  
## 🚀 About Me
I'm a Economist...

  
## 🔗 Links

[![linkedin](https://www.linkedin.com/in/lorenzocardenas/)](https://www.linkedin.com/in/lorenzocardenas/)


  
## Installation

Install FinanceAnalysis, yahoo finance, pandas-datareader and plotly  with pip

```bash
  pip install yfinance
  pip install FinRatioAnalysis
  pip install pandas-datareader
  pip install plotly
```
