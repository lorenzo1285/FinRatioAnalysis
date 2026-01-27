"""
Sample mock data for testing FinRatioAnalysis
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_mock_company_info():
    """Mock company info data from yfinance."""
    return {
        'symbol': 'AAPL',
        'marketCap': 3000000000000,  # 3 trillion
        'beta': 1.2,
    }

def get_mock_balance_sheet():
    """Mock balance sheet data."""
    dates = [datetime(2023, 9, 30), datetime(2022, 9, 30), datetime(2021, 9, 30)]
    
    data = {
        'CurrentAssets': [143566000000, 135405000000, 134836000000],
        'TotalAssets': [352755000000, 352583000000, 351002000000],
        'CurrentLiabilities': [145308000000, 153982000000, 125481000000],
        'TotalDebt': [111088000000, 120069000000, 124719000000],
        'StockholdersEquity': [62146000000, 50672000000, 63090000000],
        'RetainedEarnings': [1408000000, -3068000000, 5562000000],
        'TotalLiabilitiesNetMinorityInterest': [290609000000, 301911000000, 287912000000],
        'CashAndCashEquivalents': [29965000000, 23646000000, 34940000000],
        'AccountsReceivable': [60932000000, 60932000000, 51506000000],
        'Receivables': [60932000000, 60932000000, 51506000000],
        'Inventory': [6331000000, 4946000000, 6580000000],
        'AccountsPayable': [62611000000, 64115000000, 54763000000],
    }
    
    df = pd.DataFrame(data, index=dates).T
    df.index.name = 'Breakdown'
    return df

def get_mock_income_stmt():
    """Mock income statement data."""
    dates = [datetime(2023, 9, 30), datetime(2022, 9, 30), datetime(2021, 9, 30)]
    
    data = {
        'TotalRevenue': [383285000000, 394328000000, 365817000000],
        'CostOfRevenue': [214137000000, 223546000000, 212981000000],
        'GrossProfit': [169148000000, 170782000000, 152836000000],
        'OperatingExpense': [54735000000, 51345000000, 49048000000],
        'EBIT': [114413000000, 119437000000, 108949000000],
        'InterestExpense': [3933000000, 2931000000, 2645000000],
        'NetIncome': [96995000000, 99803000000, 94680000000],
        'TaxProvision': [16741000000, 19300000000, 14527000000],
    }
    
    df = pd.DataFrame(data, index=dates).T
    df.index.name = 'Breakdown'
    return df

def get_mock_cash_flow():
    """Mock cash flow statement data."""
    dates = [datetime(2023, 9, 30), datetime(2022, 9, 30), datetime(2021, 9, 30)]
    
    data = {
        'OperatingCashFlow': [110543000000, 122151000000, 104038000000],
        'CashFlowFromContinuingOperatingActivities': [110543000000, 122151000000, 104038000000],
        'CapitalExpenditure': [-10959000000, -10708000000, -11085000000],
        'DepreciationAndAmortization': [11519000000, 11104000000, 11284000000],
    }
    
    df = pd.DataFrame(data, index=dates).T
    df.index.name = 'Breakdown'
    return df

def get_mock_price_history(days=2520):
    """Mock price history for CAPM calculations (10 years)."""
    # Use fixed date to ensure consistent indexing across mock data
    end_date = datetime(2026, 1, 26)
    start_date = end_date - timedelta(days=days)
    date_range = pd.date_range(start=start_date, end=end_date, freq='B')  # Business days
    
    # Generate realistic price movements
    np.random.seed(42)
    prices = 100 * np.exp(np.cumsum(np.random.randn(len(date_range)) * 0.02))
    
    df = pd.DataFrame({
        'Close': prices,
        'Open': prices * 0.99,
        'High': prices * 1.01,
        'Low': prices * 0.98,
        'Volume': np.random.randint(50000000, 150000000, len(date_range), dtype=np.int64)
    }, index=date_range)
    
    return df

def get_mock_market_history(days=2520):
    """Mock S&P 500 price history."""
    # Use fixed date to ensure consistent indexing across mock data
    end_date = datetime(2026, 1, 26)
    start_date = end_date - timedelta(days=days)
    date_range = pd.date_range(start=start_date, end=end_date, freq='B')
    
    # Generate realistic market movements
    np.random.seed(43)
    prices = 3000 * np.exp(np.cumsum(np.random.randn(len(date_range)) * 0.015))
    
    df = pd.DataFrame({
        'Close': prices,
        'Open': prices * 0.995,
        'High': prices * 1.005,
        'Low': prices * 0.99,
        'Volume': np.random.randint(1000000000, 5000000000, len(date_range), dtype=np.int64)
    }, index=date_range)
    
    return df

def get_mock_treasury_rate():
    """Mock 10-year Treasury rate data."""
    # Use fixed date to ensure consistent indexing
    dates = pd.date_range(end=datetime(2026, 1, 26), periods=100, freq='D')
    
    # Treasury rate around 4%
    rates = 4.0 + np.random.randn(100) * 0.1
    
    df = pd.DataFrame(rates, index=dates, columns=['GS10'])
    return df
