import yfinance as yf
import pandas as pd 
import numpy as np
import plotly.graph_objects as go
import datetime as dt
import requests
from io import StringIO

# Constants
TRADING_DAYS_PER_YEAR = 252
DAYS_PER_YEAR = 365
ALTMAN_Z_DISTRESS_THRESHOLD = 1.8
ALTMAN_Z_SAFE_THRESHOLD = 3.0

class FinRatioAnalysis:

    def __init__(self, ticker: str, freq: str = 'yearly'):
        """
        Initialize financial ratio analysis for a given ticker.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
            freq: Data frequency - 'quarterly' or 'yearly' (default: 'yearly')
            
        Raises:
            ValueError: If ticker is invalid or data cannot be fetched
            ValueError: If freq is not 'quarterly' or 'yearly'
        """
        # Validate inputs
        if not ticker or not isinstance(ticker, str):
            raise ValueError("Ticker must be a non-empty string")
        
        if freq not in ['quarterly', 'yearly']:
            raise ValueError("Frequency must be 'quarterly' or 'yearly'")
        
        self.freq = freq
        
        try:
            # Initialize ticker and fetch basic info
            self.company = yf.Ticker(ticker)
            company_info = self.company.get_info()
            
            # Validate ticker exists
            if not company_info or 'symbol' not in company_info:
                raise ValueError(f"Invalid ticker symbol: {ticker}")
            
            self.symbol = company_info.get('symbol', ticker)
            self.marketCap = company_info.get('marketCap')
            self.beta = company_info.get('beta')
            
            if self.marketCap is None:
                raise ValueError(f"Market cap data not available for {ticker}")
            
        except Exception as e:
            raise ValueError(f"Failed to fetch company info for {ticker}: {str(e)}")
        
        try:
            # Fetch financial statements
            self.balance_sheet = self.company.get_balance_sheet(freq=self.freq)
            self.income_stmt = self.company.get_income_stmt(freq=self.freq)
            self.cash_flow = self.company.get_cash_flow(freq=self.freq)
            
            # Validate data availability
            if self.balance_sheet.empty:
                raise ValueError(f"No balance sheet data available for {ticker}")
            if self.income_stmt.empty:
                raise ValueError(f"No income statement data available for {ticker}")
            if self.cash_flow.empty:
                raise ValueError(f"No cash flow data available for {ticker}")
                
        except Exception as e:
            raise ValueError(f"Failed to fetch financial statements for {ticker}: {str(e)}")
        
        try:
            # Fetch market data
            self.tday = dt.date.today()
            self.tdelta = dt.timedelta(days=TRADING_DAYS_PER_YEAR * 10)
            self.ytday_10 = self.tday - self.tdelta
            
            self.market = yf.Ticker('^GSPC')
            market_history = self.market.history(start=self.ytday_10)
            if market_history.empty:
                raise ValueError("Failed to fetch S&P 500 market data")
            self.market_close = market_history['Close']
            
            company_history = self.company.history(start=self.ytday_10)
            if company_history.empty:
                raise ValueError(f"No price history available for {ticker}")
            self.close = company_history['Close']
            
        except Exception as e:
            raise ValueError(f"Failed to fetch market/price data: {str(e)}")
        
        try:
            # Fetch risk-free rate (10-year Treasury) from FRED
            # Using direct FRED API CSV endpoint (no API key required for public data)
            fred_url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=GS10"
            response = requests.get(fred_url)
            response.raise_for_status()
            self.rate_10 = pd.read_csv(StringIO(response.text), index_col=0, parse_dates=True)
            if self.rate_10.empty:
                raise ValueError("Failed to fetch 10-year Treasury rate data")
        except Exception as e:
            raise ValueError(f"Failed to fetch risk-free rate data: {str(e)}")

    def _get_ebit(self) -> pd.Series:
        """
        Get EBIT with fallback logic for companies that don't report it directly.
        
        Returns:
            pd.Series: EBIT values across periods
            
        Note:
            - First tries to use 'EBIT' field if available
            - Falls back to calculating: PretaxIncome + InterestExpense
            - For financial institutions without EBIT, uses OperatingIncome if available
        """
        # Try direct EBIT field first
        if 'EBIT' in self.income_stmt.index:
            return self.income_stmt.loc['EBIT', :]
        
        # Try OperatingIncome (common alternative)
        if 'OperatingIncome' in self.income_stmt.index:
            return self.income_stmt.loc['OperatingIncome', :]
        
        # Calculate EBIT from PretaxIncome + InterestExpense
        # Note: InterestExpense is negative in yfinance, so we use abs()
        if 'PretaxIncome' in self.income_stmt.index and 'InterestExpense' in self.income_stmt.index:
            return self.income_stmt.loc['PretaxIncome', :] + abs(self.income_stmt.loc['InterestExpense', :])
        
        # For financial institutions, try NetInterestIncome
        if 'NetInterestIncome' in self.income_stmt.index:
            return self.income_stmt.loc['NetInterestIncome', :]
        
        # Last resort: use PretaxIncome
        if 'PretaxIncome' in self.income_stmt.index:
            return self.income_stmt.loc['PretaxIncome', :]
        
        raise KeyError("Could not find or calculate EBIT from available income statement fields")

    def _get_first_valid_value(self, series: pd.Series, field_name: str) -> float:
        """
        Get the first non-NaN value from a pandas Series.
        
        Args:
            series: pandas Series to search
            field_name: Name of the field (for error messages)
            
        Returns:
            float: First non-NaN value
            
        Raises:
            ValueError: If all values are NaN
        """
        # Drop NaN values and get the first valid one
        valid_values = series.dropna()
        
        if valid_values.empty:
            raise ValueError(f"All values for {field_name} are NaN - cannot calculate")
        
        return valid_values.iloc[0]
              
    def return_ratios(self) -> pd.DataFrame:
        """
        Calculate return and profitability ratios.
        
        Returns:
            pd.DataFrame: DataFrame containing:
                - ROE (Return on Equity): Net Income / Stockholders Equity
                - ROA (Return on Assets): Net Income / Total Assets
                - ROCE (Return on Capital Employed): EBIT / (Total Assets - Current Liabilities)
                - ROIC (Return on Invested Capital): NOPAT / (Debt + Equity - Cash)
                - GrossMargin: Gross Profit / Total Revenue
                - OperatingMargin: EBIT / Total Revenue
                - NetProfit: Net Income / Total Revenue
                - GrossProfitToAssets: Gross Profit / Total Assets (Novy-Marx 2013 quality factor)
                
        Raises:
            KeyError: If required financial statement items are missing
        """
        ROE = np.divide(self.income_stmt.loc['NetIncome',:], 
                        self.balance_sheet.loc['StockholdersEquity',:]).to_frame(name = 'ROE')

        ROA = np.divide(self.income_stmt.loc['NetIncome',:],
                        self.balance_sheet.loc['TotalAssets',:]).to_frame(name = 'ROA')

        # ROCE calculation - skip if CurrentLiabilities doesn't exist (e.g., for financial institutions)
        if 'CurrentLiabilities' in self.balance_sheet.index:
            ROCE = np.divide(
                            self._get_ebit(),
                            (np.subtract(self.balance_sheet.loc['TotalAssets',:],
                                        self.balance_sheet.loc['CurrentLiabilities',:]))
                            ).to_frame(name = 'ROCE')
        else:
            # For financial institutions (banks), CurrentLiabilities doesn't exist
            # ROCE is not a standard metric for these companies - set to NaN
            ROCE = pd.DataFrame(
                {name: np.nan for name in self.balance_sheet.columns},
                index=[0]
            ).T
            ROCE.columns = ['ROCE']
        
        # GrossMargin calculation - skip if GrossProfit doesn't exist (e.g., for financial institutions)
        if 'GrossProfit' in self.income_stmt.index:
            GrossMargin = np.divide(self.income_stmt.loc['GrossProfit',:],
                                    self.income_stmt.loc['TotalRevenue',:]).to_frame(name = 'GrossMargin')
            # GrossProfitToAssets: Novy-Marx (2013) quality signal — GP / Total Assets
            # Cleaner than ROE/ROA because gross profit precedes all managerial discretion items
            GrossProfitToAssets = np.divide(self.income_stmt.loc['GrossProfit',:],
                                            self.balance_sheet.loc['TotalAssets',:]).to_frame(name='GrossProfitToAssets')
        else:
            # For financial institutions (banks), GrossProfit doesn't exist
            # Gross margin is not applicable for these companies - set to NaN
            GrossMargin = pd.DataFrame(
                {name: np.nan for name in self.income_stmt.columns},
                index=[0]
            ).T
            GrossMargin.columns = ['GrossMargin']
            GrossProfitToAssets = pd.DataFrame(
                {name: np.nan for name in self.income_stmt.columns},
                index=[0]
            ).T
            GrossProfitToAssets.columns = ['GrossProfitToAssets']

        OperatingMargin = np.divide(self._get_ebit(),
                                    self.income_stmt.loc['TotalRevenue',:]).to_frame(name = 'OperatingMargin')  

        NetProfit = np.divide(self.income_stmt.loc['NetIncome',:],
                                self.income_stmt.loc['TotalRevenue',:]).to_frame(name = 'NetProfit') 
        
        # ROIC (Return on Invested Capital) - Quality metric
        # Formula: NOPAT / Invested Capital where NOPAT = EBIT * (1 - Tax Rate)
        try:
            # Calculate effective tax rate from financial statements
            if 'TaxProvision' in self.income_stmt.index and 'PretaxIncome' in self.income_stmt.index:
                pretax = self.income_stmt.loc['PretaxIncome',:]
                tax_prov = self.income_stmt.loc['TaxProvision',:]
                tax_rate = np.divide(tax_prov, pretax)
                # Replace invalid values with default 21%
                tax_rate = tax_rate.fillna(0.21).replace([np.inf, -np.inf], 0.21)
            else:
                tax_rate = 0.21
            
            # NOPAT = EBIT * (1 - tax_rate)
            ebit = self._get_ebit()
            nopat = ebit * (1 - tax_rate)
            
            # Invested Capital = Total Debt + Stockholders Equity - Cash
            invested_capital = (self.balance_sheet.loc['TotalDebt',:] + 
                              self.balance_sheet.loc['StockholdersEquity',:] - 
                              self.balance_sheet.loc['CashAndCashEquivalents',:])
            # Replace zero or negative invested capital with NaN to avoid absurd ROIC values
            invested_capital = invested_capital.replace(0, np.nan)
            invested_capital = invested_capital.mask(invested_capital <= 0, np.nan)
            
            ROIC = np.divide(nopat, invested_capital).to_frame(name='ROIC')
        except (KeyError, ZeroDivisionError, ValueError):
            # Set to NaN if calculation fails
            ROIC = pd.DataFrame(
                {name: np.nan for name in self.balance_sheet.columns},
                index=[0]
            ).T
            ROIC.columns = ['ROIC']
                                
        df = pd.concat([ROE, ROA, ROCE, ROIC, GrossMargin, OperatingMargin, NetProfit, GrossProfitToAssets], axis=1)

        return df

    def valuation_growth_metrics(self) -> pd.DataFrame:
        """
        Calculate hybrid valuation and growth metrics for asset allocation.
        
        Combines real-time market valuation metrics with historical growth rates to
        help classify companies by investment profile (Conservative/Moderate/Aggressive).
        
        Returns:
            pd.DataFrame: Single-row DataFrame containing:
                Conservative Profile (Income):
                    - dividend_yield: Annual dividend as % of stock price
                    - payout_ratio: % of earnings paid as dividends
                Moderate Profile (Value/GARP):
                    - pe_ratio: Price-to-Earnings (trailing)
                    - forward_pe: Forward P/E estimate
                    - ev_ebitda: Enterprise Value / EBITDA
                    - fcf_yield: Free Cash Flow / Market Cap
                Aggressive Profile (Growth):
                    - ps_ratio: Price-to-Sales ratio
                    - beta: Volatility vs market
                Growth Metrics:
                    - revenue_cagr_3y: 3-year revenue Compound Annual Growth Rate
                    - net_income_cagr_3y: 3-year net income CAGR
        """
        
        # --- PART 1: Market Valuation (Source: yfinance .info) ---
        # We use .info because metrics like Dividend Yield depend on daily price.
        try:
            info = self.company.info
            if info is None: 
                info = {}
        except Exception as e:
            # In case of connection failure or blocking, use empty dict
            print(f"Warning: Could not fetch info from yfinance for {self.symbol}: {e}")
            info = {}

        # Helper to avoid 'None' values that break math calculations
        def safe_get(key):
            val = info.get(key)
            return float(val) if val is not None else 0.0

        metrics = {
            # --- Conservative Profile (Income) ---
            "dividend_yield": safe_get('dividendYield'), 
            "payout_ratio": safe_get('payoutRatio'),     
            
            # --- Moderate Profile (Value/GARP) ---
            "pe_ratio": safe_get('trailingPE'),          
            "forward_pe": safe_get('forwardPE'),         
            
            # --- Aggressive Profile (Growth) ---
            "ps_ratio": safe_get('priceToSalesTrailing12Months'), 
            "beta": self.beta if self.beta is not None else 1.0 
        }
        
        # --- VCG Value Metrics: EV/EBITDA and FCF Yield ---
        # EV/EBITDA - Enterprise Value to EBITDA ratio
        try:
            total_debt = self._get_first_valid_value(self.balance_sheet.loc['TotalDebt',:], 'TotalDebt')
            cash = self._get_first_valid_value(self.balance_sheet.loc['CashAndCashEquivalents',:], 'Cash')
            enterprise_value = self.marketCap + total_debt - cash
            
            # Calculate EBITDA = EBIT + Depreciation & Amortization
            ebit = self._get_first_valid_value(self._get_ebit(), 'EBIT')
            if 'DepreciationAndAmortization' in self.cash_flow.index:
                depreciation = self._get_first_valid_value(self.cash_flow.loc['DepreciationAndAmortization',:], 'D&A')
                ebitda = ebit + abs(depreciation)
            else:
                ebitda = ebit
            
            metrics['ev_ebitda'] = enterprise_value / ebitda if ebitda > 0 else np.nan
        except (KeyError, ValueError, ZeroDivisionError):
            metrics['ev_ebitda'] = np.nan
        
        # FCF Yield - Free Cash Flow Yield
        try:
            # Get Operating Cash Flow
            if 'CashFlowFromContinuingOperatingActivities' in self.cash_flow.index:
                operating_cf = self._get_first_valid_value(
                    self.cash_flow.loc['CashFlowFromContinuingOperatingActivities',:], 'Operating CF'
                )
            else:
                operating_cf = self._get_first_valid_value(
                    self.cash_flow.loc['OperatingCashFlow',:], 'Operating CF'
                )
            
            capex = self._get_first_valid_value(self.cash_flow.loc['CapitalExpenditure',:], 'CapEx')
            free_cash_flow = operating_cf + capex  # capex is negative in yfinance
            
            metrics['fcf_yield'] = free_cash_flow / self.marketCap if self.marketCap > 0 else np.nan
        except (KeyError, ValueError, ZeroDivisionError):
            metrics['fcf_yield'] = np.nan

        # --- PART 2: Structural Growth (Source: Own Historical Calculation) ---
        # We calculate the CAGR (Compound Annual Growth Rate) for 3 years.
        # This tells us if the company is truly "Growth" in the long term.
        
        # Helper function to calculate CAGR using numpy
        def calculate_cagr(data: pd.Series, periods: int = 3) -> float:
            """
            Calculate Compound Annual Growth Rate using numpy for performance.
            
            Args:
                data: Time series of values (newest to oldest)
                periods: Number of periods for CAGR calculation
                
            Returns:
                CAGR as decimal (e.g., 0.15 for 15% growth)
            """
            if len(data) < periods + 1:
                return 0.0
            
            current = float(data.iloc[0])
            past = float(data.iloc[periods])
            
            # Use numpy for faster calculation
            # CAGR = (Current/Past)^(1/periods) - 1
            if past > 0 and current > 0:
                return float(np.power(np.divide(current, past), 1/periods) - 1)
            return 0.0
        
        try:
            # Revenue CAGR - using numpy for calculation
            if 'TotalRevenue' in self.income_stmt.index:
                revenues = self.income_stmt.loc['TotalRevenue']
                metrics['revenue_cagr_3y'] = calculate_cagr(revenues, periods=3)
            else:
                metrics['revenue_cagr_3y'] = 0.0

            # Net Income CAGR - using numpy for calculation
            if 'NetIncome' in self.income_stmt.index:
                income = self.income_stmt.loc['NetIncome']
                metrics['net_income_cagr_3y'] = calculate_cagr(income, periods=3)
            else:
                metrics['net_income_cagr_3y'] = 0.0

        except Exception as e:
            print(f"Warning: Error calculating growth metrics for {self.symbol}: {e}")
            metrics['revenue_cagr_3y'] = 0.0
            metrics['net_income_cagr_3y'] = 0.0

        return pd.DataFrame([metrics])

    def historical_valuation_metrics(self) -> pd.DataFrame:
        """
        Calculate historical valuation metrics using period-end stock prices.
        
        Unlike valuation_growth_metrics() which returns current market values,
        this method calculates P/E, EV/EBITDA, and FCF Yield for each historical
        period using the stock price at each fiscal period-end date.
        
        Returns:
            pd.DataFrame: DataFrame with dates as index containing:
                - PE_Ratio: (Price × Shares Outstanding) / Net Income
                - EV_EBITDA: (Market Cap + Debt - Cash) / EBITDA
                - FCF_Yield: Free Cash Flow / Market Cap
                - Market_Cap: Historical market capitalization
                
        Raises:
            KeyError: If required financial statement items are missing
        """
        # Get fiscal period-end dates from financial statements
        period_dates = self.balance_sheet.columns
        
        # Initialize lists to store results
        pe_ratios = []
        ev_ebitdas = []
        fcf_yields = []
        market_caps = []
        
        for date in period_dates:
            try:
                # Get stock price closest to fiscal period end
                # Convert timestamp to datetime for comparison
                period_end = pd.Timestamp(date).tz_localize(None)  # Remove timezone
                
                # Ensure close index is also timezone-naive
                close_index = self.close.index.tz_localize(None) if self.close.index.tz is not None else self.close.index
                
                # Find closest trading day to period end
                price_data = self.close[close_index <= period_end]
                if price_data.empty:
                    # If no data before period end, try after
                    price_data = self.close[close_index >= period_end]
                
                if price_data.empty:
                    market_caps.append(np.nan)
                    pe_ratios.append(np.nan)
                    ev_ebitdas.append(np.nan)
                    fcf_yields.append(np.nan)
                    continue
                
                # Get price closest to period end
                stock_price = price_data.iloc[-1] if close_index[0] < period_end else price_data.iloc[0]
                
                # Get shares outstanding for this period
                if 'ShareIssued' in self.balance_sheet.index:
                    shares_outstanding = self.balance_sheet.loc['ShareIssued', date]
                elif 'OrdinarySharesNumber' in self.balance_sheet.index:
                    shares_outstanding = self.balance_sheet.loc['OrdinarySharesNumber', date]
                else:
                    # Fallback: use current market cap and current price to estimate shares
                    shares_outstanding = self.marketCap / self.close.iloc[-1]
                
                # Calculate all values first (atomic pattern to avoid partial appends)
                # Calculate historical market cap
                market_cap = stock_price * shares_outstanding
                
                # P/E Ratio = Market Cap / Net Income
                net_income = self.income_stmt.loc['NetIncome', date]
                pe_ratio = market_cap / net_income if net_income > 0 else np.nan
                
                # EV/EBITDA = (Market Cap + Debt - Cash) / EBITDA
                total_debt = self.balance_sheet.loc['TotalDebt', date]
                cash = self.balance_sheet.loc['CashAndCashEquivalents', date]
                enterprise_value = market_cap + total_debt - cash
                
                # Calculate EBITDA
                ebit = self._get_ebit()[date]
                if 'DepreciationAndAmortization' in self.cash_flow.index:
                    depreciation = self.cash_flow.loc['DepreciationAndAmortization', date]
                    ebitda = ebit + abs(depreciation)
                else:
                    ebitda = ebit
                
                ev_ebitda = enterprise_value / ebitda if ebitda > 0 else np.nan
                
                # FCF Yield = Free Cash Flow / Market Cap
                if 'CashFlowFromContinuingOperatingActivities' in self.cash_flow.index:
                    operating_cf = self.cash_flow.loc['CashFlowFromContinuingOperatingActivities', date]
                else:
                    operating_cf = self.cash_flow.loc['OperatingCashFlow', date]
                
                capex = self.cash_flow.loc['CapitalExpenditure', date]
                free_cash_flow = operating_cf + capex  # capex is negative
                
                fcf_yield = free_cash_flow / market_cap if market_cap > 0 else np.nan
                
                # Append all values together (all-or-nothing)
                market_caps.append(market_cap)
                pe_ratios.append(pe_ratio)
                ev_ebitdas.append(ev_ebitda)
                fcf_yields.append(fcf_yield)
                
            except (KeyError, ZeroDivisionError, ValueError, IndexError) as e:
                # If any calculation fails for this period, set to NaN
                market_caps.append(np.nan)
                pe_ratios.append(np.nan)
                ev_ebitdas.append(np.nan)
                fcf_yields.append(np.nan)
        
        # Create DataFrame with dates as index
        df = pd.DataFrame({
            'Market_Cap': market_caps,
            'PE_Ratio': pe_ratios,
            'EV_EBITDA': ev_ebitdas,
            'FCF_Yield': fcf_yields
        }, index=period_dates)
        
        return df

    def leverage_ratios(self) -> pd.DataFrame:
        """
        Calculate leverage and solvency ratios.
        
        Returns:
            pd.DataFrame: DataFrame containing:
                - DebtEquityRatio: Total Debt / Stockholders Equity
                - EquityRatio: Stockholders Equity / Total Assets
                - DebtRatio: Total Debt / Total Assets
                
        Raises:
            KeyError: If required financial statement items are missing
        """
        DebtEquityRatio = np.divide(self.balance_sheet.loc['TotalDebt',:],
                                    self.balance_sheet.loc['StockholdersEquity',:]).to_frame(name = 'DebtEquityRatio')

        EquityRatio = np.divide(self.balance_sheet.loc['StockholdersEquity',:],
                                self.balance_sheet.loc['TotalAssets',:]).to_frame(name = 'EquityRatio')

        DebtRatio = np.divide(self.balance_sheet.loc['TotalDebt',:],
                              self.balance_sheet.loc['TotalAssets',:]).to_frame(name = 'DebtRatio')

        df = pd.concat([DebtEquityRatio, EquityRatio, DebtRatio], axis=1)

        return df

    def efficiency_ratios(self) -> pd.DataFrame:
        """
        Calculate efficiency and activity ratios.
        
        Returns:
            pd.DataFrame: DataFrame containing:
                - AssetTurnover: Total Revenue / Total Assets
                - ReceivableTurnover: Total Revenue / Receivables
                - InventoryTurnover: Cost of Revenue / Inventory
                - FixedAssetTurnover: Total Revenue / Fixed Assets
                - FCF_Margin: Free Cash Flow / Total Revenue
                - ReinvestmentRate: (CapEx - Depreciation) / Net Income
                
        Raises:
            KeyError: If required financial statement items are missing
        """
        # Try to get Receivables from different possible field names
        try:
            Receivables = self.balance_sheet.loc['Receivables',:] 
        except KeyError:
            try:
                Receivables = self.balance_sheet.loc['GrossAccountsReceivable',:]
            except KeyError:
                # If Receivables data doesn't exist, set to NaN
                Receivables = pd.Series(
                    {name: np.nan for name in self.balance_sheet.columns},
                    index=self.balance_sheet.columns
                )
        
        AssetTurnover = np.divide(self.income_stmt.loc['TotalRevenue',:],
                                  self.balance_sheet.loc['TotalAssets',:]).to_frame(name = 'AssetTurnover')

        ReceivableTurnover = np.divide(self.income_stmt.loc['TotalRevenue',:],
                                       Receivables).to_frame(name = 'ReceivableTurnover')

        # Try to get Inventory, handle missing data
        try:
            Inventory = self.balance_sheet.loc['Inventory',:]
        except KeyError:
            Inventory = pd.Series(
                {name: np.nan for name in self.balance_sheet.columns},
                index=self.balance_sheet.columns
            )
        
        InventoryTurnover = np.divide(self.income_stmt.loc['CostOfRevenue',:],
                                        Inventory).to_frame(name = 'InventoryTurnover')
                                        
        FixedAssetTurnover = np.divide(
                                        self.income_stmt.loc['TotalRevenue',:],
                                        
                                        np.subtract(self.balance_sheet.loc['TotalAssets',:],
                                                    self.balance_sheet.loc['CurrentAssets',:])
                                        ).to_frame(name = 'FixedAssetTurnover')
        
        # FCF Margin - Free Cash Flow Margin (Quality metric)
        # Measures efficiency in converting revenue to free cash flow
        try:
            if 'CashFlowFromContinuingOperatingActivities' in self.cash_flow.index:
                operating_cf = self.cash_flow.loc['CashFlowFromContinuingOperatingActivities',:]
            else:
                operating_cf = self.cash_flow.loc['OperatingCashFlow',:]
            
            capex = self.cash_flow.loc['CapitalExpenditure',:]
            free_cash_flow = operating_cf + capex  # capex is negative
            
            FCF_Margin = np.divide(free_cash_flow,
                                  self.income_stmt.loc['TotalRevenue',:]).to_frame(name='FCF_Margin')
        except (KeyError, ZeroDivisionError):
            FCF_Margin = pd.DataFrame(
                {name: np.nan for name in self.income_stmt.columns},
                index=[0]
            ).T
            FCF_Margin.columns = ['FCF_Margin']
        
        # Reinvestment Rate - Net CapEx / NOPAT (Growth metric)
        # Institutional formula: measures capital reinvestment relative to operating profits
        # This avoids distortion from companies with temporary losses or small net income
        try:
            capex = self.cash_flow.loc['CapitalExpenditure',:]
            depreciation = self.cash_flow.loc['DepreciationAndAmortization',:]
            
            # Net CapEx = CapEx + Depreciation (capex is negative in yfinance)
            net_capex = capex + abs(depreciation)
            
            # Calculate NOPAT = EBIT * (1 - Tax Rate) for more stable denominator
            if 'TaxProvision' in self.income_stmt.index and 'PretaxIncome' in self.income_stmt.index:
                pretax = self.income_stmt.loc['PretaxIncome',:]
                tax_prov = self.income_stmt.loc['TaxProvision',:]
                tax_rate = np.divide(tax_prov, pretax)
                tax_rate = tax_rate.fillna(0.21).replace([np.inf, -np.inf], 0.21)
            else:
                tax_rate = 0.21
            
            ebit = self._get_ebit()
            nopat = ebit * (1 - tax_rate)
            
            # Use np.where to handle cases where NOPAT <= 0 (set to NaN)
            # This prevents absurd ratios from temporary losses
            reinvestment_rate = np.divide(abs(net_capex), nopat)
            reinvestment_rate = np.where(nopat > 0, reinvestment_rate, np.nan)
            
            ReinvestmentRate = pd.Series(reinvestment_rate, index=nopat.index).to_frame(name='ReinvestmentRate')
        except (KeyError, ZeroDivisionError, ValueError):
            ReinvestmentRate = pd.DataFrame(
                {name: np.nan for name in self.income_stmt.columns},
                index=[0]
            ).T
            ReinvestmentRate.columns = ['ReinvestmentRate']

        df = pd.concat([AssetTurnover, ReceivableTurnover, InventoryTurnover, FixedAssetTurnover,
                       FCF_Margin, ReinvestmentRate], axis=1)

        return df

    def liquidity_ratios(self) -> pd.DataFrame:
        """
        Calculate liquidity and cash flow ratios.
        
        Returns:
            pd.DataFrame: DataFrame containing:
                - CurrentRatio: Current Assets / Current Liabilities
                - QuickRatio: (Cash + Receivables) / Current Liabilities
                - CashRatio: Cash / Current Liabilities
                - DIR (Defensive Interval Ratio): Current Assets / Daily Expenses
                - TIE (Times Interest Earned): EBIT / Interest Expense
                - TIE_CB (Cash-Based TIE): Operating Cash Flow / Interest Expense
                - CAPEX_OpCash: Operating Cash Flow / Capital Expenditure
                - OpCashFlow: Operating Cash Flow / Current Liabilities
                
        Raises:
            KeyError: If required financial statement items are missing
        """
        try:
            continue_cf = self.cash_flow.loc['CashFlowFromContinuingOperatingActivities',:]
        except KeyError:
            continue_cf = self.cash_flow.loc['OperatingCashFlow',:]


        CurrentRatio = np.divide(self.balance_sheet.loc['CurrentAssets',:],
                                 self.balance_sheet.loc['CurrentLiabilities',:]).to_frame(name = 'CurrentRatios')

        QuickRatio = np.divide(
                                np.add(self.balance_sheet.loc['CashAndCashEquivalents',:],
                                       self.balance_sheet.loc['AccountsReceivable',:]), 
                                
                                       self.balance_sheet.loc['CurrentLiabilities',:]).to_frame(name = 'QuickRatio')
                                
        CashRatio = np.divide(self.balance_sheet.loc['CashAndCashEquivalents',:],
                              self.balance_sheet.loc['CurrentLiabilities',:]).to_frame(name = 'CashRatio')

        COGS = self.income_stmt.loc['CostOfRevenue',:]
        
        DailyExpense = np.divide(np.subtract(COGS + self.income_stmt.loc['OperatingExpense',:],   
                                                self.cash_flow.loc['DepreciationAndAmortization',:]), DAYS_PER_YEAR)    

        DIR = np.divide(self.balance_sheet.loc['CurrentAssets',:], DailyExpense
                                 ).to_frame(name = 'DIR')

        # TIE = EBIT / Interest Expense (use abs since InterestExpense is negative in yfinance)
        TIE = np.divide(self._get_ebit(), 
                        abs(self.income_stmt.loc['InterestExpense',:])).to_frame(name = 'TIE')

        # TIE Cash Basis = Operating Cash Flow / Interest Expense
        TIE_CB = np.divide(self.cash_flow.loc['OperatingCashFlow',:], 
                           abs(self.income_stmt.loc['InterestExpense',:])).to_frame(name = 'TIE_CB')

        CAPEX_OpCash = np.divide(continue_cf,
                                    abs(self.cash_flow.loc['CapitalExpenditure',:])).to_frame(name = 'CAPEX_OpCash')

        OpCashFlow = np.divide(continue_cf,
                                self.balance_sheet.loc['CurrentLiabilities',:]).to_frame(name = 'OpCashFlow')

        df = pd.concat([CurrentRatio, QuickRatio, CashRatio, DIR, TIE, 
                        TIE_CB, CAPEX_OpCash, OpCashFlow], axis=1)

        return df

    def ccc(self) -> pd.DataFrame:
        """
        Calculate Cash Conversion Cycle (CCC) and its components.
        
        The CCC measures how long it takes to convert inventory and receivables
        into cash, minus the time to pay suppliers.
        
        Returns:
            pd.DataFrame: DataFrame containing:
                - DIO (Days Inventory Outstanding): Average time to sell inventory
                - DSO (Days Sales Outstanding): Average time to collect receivables
                - DPO (Days Payables Outstanding): Average time to pay suppliers
                - CCC: DIO + DSO - DPO (in days)
                
        Raises:
            KeyError: If required financial statement items are missing
        """
        avg_inventory = self.balance_sheet.loc['Inventory',:].mean()

        avg_AccountsReceivable = self.balance_sheet.loc['AccountsReceivable',:].mean()

        avg_AccountsPayable = self.balance_sheet.loc['AccountsPayable',:].mean()
        
        DIO = (np.divide(avg_inventory,
                        self.income_stmt.loc['CostOfRevenue',:])*DAYS_PER_YEAR).to_frame(name='DIO')

        DSO = (np.divide(avg_AccountsReceivable,
                        self.income_stmt.loc['TotalRevenue',:])*DAYS_PER_YEAR).to_frame(name='DSO')

        DPO = (np.divide(avg_AccountsPayable,
                        self.income_stmt.loc['CostOfRevenue',:])*DAYS_PER_YEAR).to_frame(name='DPO')
        # Cash Convertion Cycle
        df = pd.concat([DIO, DSO, DPO], axis=1)

        df['CCC'] = df['DIO'] + df['DSO'] - df['DPO']

        return df

    def _calculate_z_score(self) -> tuple[float, str]:
        """
        Private method to calculate Altman Z-Score and determine zone.
        
        Returns:
            tuple[float, str]: (Z-Score value, Zone classification)
        """
        X_1 = np.divide(self.balance_sheet.loc['CurrentAssets',:].iloc[0],
                        self.balance_sheet.loc['TotalAssets',:].iloc[0])

        X_2 = np.divide(self.balance_sheet.loc['RetainedEarnings',:].iloc[0],
                        self.balance_sheet.loc['TotalAssets',:].iloc[0])

        ebit_series = self._get_ebit()
        X_3 = np.divide(ebit_series.iloc[0],
                        self.balance_sheet.loc['TotalAssets',:].iloc[0])

        X_4 = np.divide(self.marketCap, self.balance_sheet.loc['TotalLiabilitiesNetMinorityInterest',:].iloc[0])

        X_5 = np.divide(self.income_stmt.loc['TotalRevenue',:].iloc[0],
                        self.balance_sheet.loc['TotalAssets',:].iloc[0])

        Z_score = 1.2*X_1 + 1.4*X_2 + 3.3*X_3 + .6*X_4 + .99*X_5

        if Z_score <= ALTMAN_Z_DISTRESS_THRESHOLD:
            zone = 'Distress Zone'   
        elif Z_score >= ALTMAN_Z_SAFE_THRESHOLD:
            zone = 'Safe Zone'
        else:
            zone = 'Grey Zone'
            
        return Z_score, zone

    def z_score(self) -> pd.DataFrame:
        """
        Calculate Altman Z-Score for bankruptcy prediction.
        
        The Z-Score uses five financial ratios weighted to predict probability
        of bankruptcy within 2 years:
        - Z < 1.8: Distress Zone (high bankruptcy risk)
        - 1.8 <= Z < 3.0: Grey Zone (moderate risk)
        - Z >= 3.0: Safe Zone (low risk)
        
        Returns:
            pd.DataFrame: DataFrame containing Symbol, Z Score, and Zone
                
        Raises:
            KeyError: If required financial statement items are missing
        """
        Z_score, zone = self._calculate_z_score()

        data = {
            'Symbol': self.symbol,
            'Z Score' : round(Z_score, 3),
            'Zone' : zone
        }

        df = pd.DataFrame([data])

        return df

    def z_score_plot(self) -> None:
        """
        Display interactive gauge visualization of Altman Z-Score.
        
        Shows a Plotly gauge chart with color-coded zones:
        - Red zone (0-1.8): Distress Zone
        - Grey zone (1.8-3.0): Grey Zone
        - Green zone (3.0+): Safe Zone
                
        Raises:
            KeyError: If required financial statement items are missing
        """
        Z_score, zone = self._calculate_z_score()

        fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = Z_score.round(3),
        title = {'text': f"{self.symbol}: {zone}",
                 'font':{
                    'size': 25
                 }},
        domain = {'x': [0, 1], 'y': [0, 1]},
        number = {'font_size':50},

        gauge = { 'shape' : 'angular',
             'steps' : [
                        {'range': [0, ALTMAN_Z_DISTRESS_THRESHOLD], 'color': 'red'},
                        {'range': [ALTMAN_Z_DISTRESS_THRESHOLD, ALTMAN_Z_SAFE_THRESHOLD], 'color': 'grey'},
                        {'range': [ALTMAN_Z_SAFE_THRESHOLD, 20], 'color': 'green'}
                        ],
             'bar' : {'color': 'black', 'thickness':.5}}
        ))

        fig.show()

    def capm(self) -> pd.DataFrame:
        """
        Calculate Capital Asset Pricing Model (CAPM) expected return and Sharpe ratio.
        
        CAPM formula: Expected Return = Risk-Free Rate + Beta * (Market Return - Risk-Free Rate)
        Sharpe Ratio: (Expected Return - Risk-Free Rate) / Standard Deviation
        
        Uses:
        - 10-year Treasury rate as risk-free rate
        - S&P 500 (^GSPC) as market proxy
        - 10 years of daily price data
        - 252 trading days per year
        
        Returns:
            pd.DataFrame: DataFrame containing:
                - Symbol: Stock ticker
                - CAPM: Expected annual return (decimal)
                - Sharpe: Sharpe ratio (risk-adjusted return)
                
        Raises:
            KeyError: If price history or risk-free rate data is missing
        """
        company_log_return = np.log(1+self.close.pct_change())

        market_log_return = np.log(1+self.market_close.pct_change())

        df = pd.concat([company_log_return, market_log_return], axis=1)
        df.columns = ['Company', 'Market']  # Ensure unique column names for proper covariance calculation
        
        cov = df.cov()*TRADING_DAYS_PER_YEAR

        market_cov = cov.iloc[0,1]

        market_var = (market_log_return.var()*TRADING_DAYS_PER_YEAR)

        beta = np.divide(market_cov, market_var)

        risk_free = np.divide(self.rate_10.iloc[-1],100)

        risk_premium = np.subtract((market_log_return.mean()*TRADING_DAYS_PER_YEAR), risk_free)

        capm = (risk_free + beta * risk_premium)

        sharpe = np.divide(
                            (capm-risk_free),
                            (np.std(company_log_return)*np.sqrt(TRADING_DAYS_PER_YEAR)))

        data = {
            'Symbol': self.symbol,
            'CAPM': capm.iloc[0].round(4),
            'Sharpe': sharpe.iloc[0].round(4)
        }

        df_1 = pd.DataFrame([data])
    
        return df_1 

    def wacc(self) -> pd.DataFrame:
        """
        Calculate Weighted Average Cost of Capital (WACC).
        
        WACC = (E/V * Cost of Equity) + (D/V * Cost of Debt * (1 - Tax Rate))
        where:
        - E = Market value of equity (market cap)
        - D = Book value of total debt
        - V = E + D (total value)
        - Cost of Equity = CAPM expected return
        - Cost of Debt = Interest Expense / Average Total Debt
        - Tax Rate = Tax Provision / Net Income
        
        Returns:
            pd.DataFrame: DataFrame containing Symbol and WACC (decimal)
                
        Raises:
            KeyError: If required financial statement items are missing
        """
        E = self.marketCap
        
        D = self._get_first_valid_value(self.balance_sheet.loc['TotalDebt'], 'TotalDebt')
        
        V = np.add(E,D)
        
        capm = self.capm()
        costEquity = capm['CAPM'].values
        
        # Use first non-NaN interest expense value (current period may be NaN)
        # InterestExpense is negative in yfinance, so we use abs()
        interest_expense = self._get_first_valid_value(
            abs(self.income_stmt.loc['InterestExpense']), 
            'InterestExpense'
        )
        costDebt = np.divide(interest_expense, self.balance_sheet.loc['TotalDebt'][:2].mean())
        
        # Use first non-NaN tax provision and net income
        tax_provision = self._get_first_valid_value(
            self.income_stmt.loc['TaxProvision'],
            'TaxProvision'
        )
        net_income = self._get_first_valid_value(
            self.income_stmt.loc['NetIncome'],
            'NetIncome'
        )
        tax_rate = np.divide(tax_provision, net_income)

        WACC = ((E/V)*costEquity)+(((D/V)*costDebt)*(1-tax_rate))

        data = {
            'Symbol': self.symbol,
            'WACC':WACC}

        return pd.DataFrame(data)
    
    def momentum(self) -> pd.DataFrame:
        """
        Calculate 12-1 month cross-sectional price momentum.

        Skips the most recent 21 trading days (1 month) to avoid the well-documented
        short-term reversal effect. This is the standard Jegadeesh-Titman (1993)
        momentum factor construction used by AQR, MSCI, and most factor indices.

        Formula: (close[t-22] / close[t-273]) - 1
            where t-22 ≈ 1 month ago and t-273 ≈ 13 months ago,
            giving a 12-month window ending 1 month before today.

        Returns:
            pd.DataFrame: Single-row DataFrame containing:
                - Symbol: Stock ticker
                - momentum_12_1: 12-1 month return (decimal, e.g. 0.25 = 25%)

        Notes:
            Returns NaN for momentum_12_1 if fewer than 273 trading days of
            price history are available.
        """
        SKIP = 21     # 1 month in trading days
        LOOKBACK = 252  # 12 months in trading days
        MIN_DAYS = LOOKBACK + SKIP + 1

        close = self.close
        if len(close) < MIN_DAYS:
            return pd.DataFrame([{'Symbol': self.symbol, 'momentum_12_1': np.nan}])

        price_end = float(close.iloc[-(SKIP + 1)])
        price_start = float(close.iloc[-(LOOKBACK + SKIP + 1)])

        mom = round((price_end / price_start) - 1, 4)
        return pd.DataFrame([{'Symbol': self.symbol, 'momentum_12_1': mom}])

    # Backward compatibility aliases (deprecated - use snake_case methods)
    def ReturnRatios(self) -> pd.DataFrame:
        """Deprecated: Use return_ratios() instead."""
        return self.return_ratios()
    
    def LeverageRatios(self) -> pd.DataFrame:
        """Deprecated: Use leverage_ratios() instead."""
        return self.leverage_ratios()
    
    def EfficiencyRatios(self) -> pd.DataFrame:
        """Deprecated: Use efficiency_ratios() instead."""
        return self.efficiency_ratios()
    
    def LiquidityRatios(self) -> pd.DataFrame:
        """Deprecated: Use liquidity_ratios() instead."""
        return self.liquidity_ratios()
    
    def CCC(self) -> pd.DataFrame:
        """Deprecated: Use ccc() instead."""
        return self.ccc()
    
    def CAPM(self) -> pd.DataFrame:
        """Deprecated: Use capm() instead."""
        return self.capm()
    
    def WACC(self) -> pd.DataFrame:
        """Deprecated: Use wacc() instead."""
        return self.wacc()