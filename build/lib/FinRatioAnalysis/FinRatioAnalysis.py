# %% [markdown]
# # Package imports

# %%
import yfinance as yf
import pandas as pd 
import numpy as np
import pandas_datareader as pdr
import plotly.graph_objects as go
import datetime as dt 

# %% [markdown]
# # FinRatioAnalysis

# %%
class FinRatioAnalysis():

    def __init__(self, ticker = str, freq = str): # Frequency most be 'quarterly' or 'yearly'
        
        self.tday = dt.date.today()
        self.tdelta = dt.timedelta(days=252*10)
        self.ytday_10 = self.tday - self.tdelta
        self.company = yf.Ticker(ticker)
        self.market = yf.Ticker('^GSPC')
        self.market_close = self.market.history(start=self.ytday_10)['Close']
        self.freq = freq
        self.balance_sheet = self.company.get_balance_sheet(freq=self.freq)  
        self.income_stmt = self.company.get_income_stmt(freq=self.freq)
        self.cash_flow = self.company.get_cash_flow(freq=self.freq)
        self.rate_10 = pdr.get_data_fred('GS10')
        self.marketCap = self.company.get_info()['marketCap']
        self.symbol = self.company.get_info()['symbol']
        self.beta = self.company.get_info()['beta']
        self.close =  self.company.history(start=self.ytday_10)['Close']

              
    def ReturnRatios(self):

        ROE = np.divide(self.income_stmt.loc['NetIncome',:], 
                        self.balance_sheet.loc['StockholdersEquity',:]).to_frame(name = 'ROE')

        ROA = np.divide(self.income_stmt.loc['NetIncome',:],
                        self.balance_sheet.loc['TotalAssets',:]).to_frame(name = 'ROA')

        ROCE = np.divide(
                        self.income_stmt.loc['EBIT',:],
                        (np.subtract(self.balance_sheet.loc['TotalAssets',:],
                                    self.balance_sheet.loc['CurrentLiabilities',:]))
                        ).to_frame(name = 'ROCE')
        
        GrossMargin = np.divide(self.income_stmt.loc['GrossProfit',:],
                                self.income_stmt.loc['TotalRevenue',:]).to_frame(name = 'GrossMargin') 

        OperatingMargin = np.divide(self.income_stmt.loc['EBIT',:],
                                    self.income_stmt.loc['TotalRevenue',:]).to_frame(name = 'OperatingMargin')  

        NetProfit = np.divide(self.income_stmt.loc['NetIncome',:],
                                self.income_stmt.loc['TotalRevenue',:]).to_frame(name = 'NetProfit') 
                                
        df = pd.concat([ROE, ROA, ROCE, GrossMargin, OperatingMargin, NetProfit], axis=1)

        return df

    def LeverageRatios(self):

        DebtEquityRatio = np.divide(self.balance_sheet.loc['TotalDebt',:],
                                    self.balance_sheet.loc['StockholdersEquity',:]).to_frame(name = 'DebtEquityRatio')

        EquityRatio = np.divide(self.balance_sheet.loc['StockholdersEquity',:],
                                self.balance_sheet.loc['TotalAssets',:]).to_frame(name = 'EquityRatio')

        DebtRatio = np.divide(self.balance_sheet.loc['TotalDebt',:],
                              self.balance_sheet.loc['TotalAssets',:]).to_frame(name = 'DebtRatio')

        df = pd.concat([DebtEquityRatio, EquityRatio, DebtRatio], axis=1)

        return df

    def EfficiencyRatios(self):

        try:
            Receivables = self.balance_sheet.loc['Receivables',:] 
        except KeyError:
            Receivables = self.balance_sheet.loc['GrossAccountsReceivable',:]
        
        AssetTurnover = np.divide(self.income_stmt.loc['TotalRevenue',:],
                                  self.balance_sheet.loc['TotalAssets',:]).to_frame(name = 'AssetTurnover')

        ReceivableTurnover = np.divide(self.income_stmt.loc['TotalRevenue',:],
                                       Receivables).to_frame(name = 'ReceivableTurnover')

        InventoryTurnover = np.divide(self.income_stmt.loc['CostOfRevenue',:],
                                        self.balance_sheet.loc['Inventory',:]).to_frame(name = 'InventoryTurnover')
                                        
        FixedAssetTurnover = np.divide(
                                        self.income_stmt.loc['TotalRevenue',:],
                                        
                                        np.subtract(self.balance_sheet.loc['TotalAssets',:],
                                                    self.balance_sheet.loc['CurrentAssets',:])
                                        ).to_frame(name = 'FixedAssetTurnover')

        df = pd.concat([AssetTurnover, ReceivableTurnover, InventoryTurnover, FixedAssetTurnover], axis=1)

        return df

    def LiquidityRatios(self):

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
                                                self.cash_flow.loc['DepreciationAndAmortization',:]), 365)    

        DIR = np.divide(self.balance_sheet.loc['CurrentAssets',:], DailyExpense
                                 ).to_frame(name = 'DIR')

        TIE = np.divide(self.income_stmt.loc['EBIT',:], 
                        self.income_stmt.loc['InterestExpense',:]).to_frame(name = 'TIE')

        TIE_CB = np.divide(self.cash_flow.loc['OperatingCashFlow',:], 
                           self.income_stmt.loc['InterestExpense',:]).to_frame(name = 'TIE_CB')

        CAPEX_OpCash = np.divide(continue_cf,
                                    abs(self.cash_flow.loc['CapitalExpenditure',:])).to_frame(name = 'CAPEX_OpCash')

        OpCashFlow = np.divide(continue_cf,
                                self.balance_sheet.loc['CurrentLiabilities',:]).to_frame(name = 'OpCashFlow')

        df = pd.concat([CurrentRatio, QuickRatio, CashRatio, DIR, TIE, 
                        TIE_CB, CAPEX_OpCash, OpCashFlow], axis=1)

        return df

    def CCC(self):

        avg_inventory = self.balance_sheet.loc['Inventory',:].mean()

        avg_AccountsReceivable = self.balance_sheet.loc['AccountsReceivable',:].mean()

        avg_AccountsPayable = self.balance_sheet.loc['AccountsPayable',:].mean()
        
        DIO = (np.divide(avg_inventory,
                        self.income_stmt.loc['CostOfRevenue',:])*365).to_frame(name='DIO')

        DSO = (np.divide(avg_AccountsReceivable,
                        self.income_stmt.loc['TotalRevenue',:])*365).to_frame(name='DSO')

        DPO = (np.divide(avg_AccountsPayable,
                        self.income_stmt.loc['CostOfRevenue',:])*365).to_frame(name='DPO')
        # Cash Convertion Cycle
        df = pd.concat([DIO, DSO, DPO], axis=1)

        df['CCC'] = df['DIO'] + df['DSO'] - df['DPO']

        return df

    def z_score(self):

        X_1 = np.divide(self.balance_sheet.loc['CurrentAssets',:][0],
                        self.balance_sheet.loc['TotalAssets',:][0])

        X_2 = np.divide(self.balance_sheet.loc['RetainedEarnings',:][0],
                        self.balance_sheet.loc['TotalAssets',:][0])

        X_3 = np.divide(self.income_stmt.loc['EBIT',:][0],
                        self.balance_sheet.loc['TotalAssets',:][0])

        X_4 = np.divide(self.marketCap, self.balance_sheet.loc['TotalLiabilitiesNetMinorityInterest',:][0])

        X_5 = np.divide(self.income_stmt.loc['TotalRevenue',:][0],
                        self.balance_sheet.loc['TotalAssets',:][0])

        Z_score = 1.2*X_1 + 1.4*X_2 + 3.3*X_3 + .6*X_4 + .99*X_5

        if Z_score <= 1.8:
            zone = 'Distress Zone'   
        elif Z_score >= 3:
            zone = 'Safe Zone'
        else:
            zone = 'Grey Zone'

        data = {
            'Symbol': self.symbol,
            'Z Score' : Z_score.round(3),
            'Zone' : zone
        }

        df = pd.DataFrame([data])

        return df

    def z_score_plot(self):

        X_1 = np.divide(self.balance_sheet.loc['CurrentAssets',:][0],
                        self.balance_sheet.loc['TotalAssets',:][0])

        X_2 = np.divide(self.balance_sheet.loc['RetainedEarnings',:][0],
                        self.balance_sheet.loc['TotalAssets',:][0])

        X_3 = np.divide(self.income_stmt.loc['EBIT',:][0],
                        self.balance_sheet.loc['TotalAssets',:][0])

        X_4 = np.divide(self.marketCap, self.balance_sheet.loc['TotalLiabilitiesNetMinorityInterest',:][0])

        X_5 = np.divide(self.income_stmt.loc['TotalRevenue',:][0],
                        self.balance_sheet.loc['TotalAssets',:][0])

        Z_score = 1.2*X_1 + 1.4*X_2 + 3.3*X_3 + .6*X_4 + .99*X_5
       
        if Z_score <= 1.8:
            zone = 'Distress Zone'   
        elif Z_score >= 3:
            zone = 'Safe Zone'
        else:
            zone = 'Grey Zone'

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
                        {'range': [0, 1.8], 'color': 'red'},
                        {'range': [1.8, 3], 'color': 'grey'},
                        {'range': [3,20], 'color': 'green'}
                        ],
             'bar' : {'color': 'black', 'thickness':.5}}
        ))

        fig.show()

    def CAPM(self):

        company_log_return = np.log(1+self.close.pct_change())

        market_log_return = np.log(1+self.market_close.pct_change())

        df = pd.concat([company_log_return, market_log_return], axis=1)
        
        cov = df.cov()*252

        market_cov = cov.iloc[0,1]

        market_var = (market_log_return.var()*252)

        beta = np.divide(market_cov, market_var)

        risk_free = np.divide(self.rate_10.iloc[-1],100)

        risk_premium = np.subtract((market_log_return.mean()*252), risk_free)

        capm = (risk_free + beta * risk_premium)

        sharpe = np.divide(
                            (capm-risk_free),
                            (np.std(company_log_return)*252**.05))

        data = {
            'Symbol': self.symbol,
            'CAPM': capm[0].round(4),
            'Sharpe': sharpe[0].round(4)
        }

        df_1 = pd.DataFrame([data])
    
        return df_1 

    def WACC(self):

        E = self.marketCap
        
        D = self.balance_sheet.loc['TotalDebt'][0]
        
        V = np.add(E,D)
        
        capm = self.CAPM()
        costEquity = capm['CAPM'].values
        
        costDebt = np.divide(self.income_stmt.loc['InterestExpense'][0],
                                self.balance_sheet.loc['TotalDebt'][:2].mean())
        
        tax_rate = np.divide(self.income_stmt.loc['TaxProvision'][0],
                                self.income_stmt.loc['NetIncome'][0])

        WACC = ((E/V)*costEquity)+(((D/V)*costDebt)*(1-tax_rate))

        data = {
            'Symbol': self.symbol,
            'WACC':WACC}

        return pd.DataFrame(data)