import json
import pandas as pd
import yfinance as yf

class YahooWrapper:
    
    def __init__(self,t):
        self.ticker = t
        pass
    
    def formatNumber(self,value):
        try:
            return f"{int(value):,}" if value == int(value) else f"{value:,.2f}"
        except:
            return "N/A"

    def align(self,cols, arr):
        if(len(cols) != len(arr)):
            return None
        
        n = len(cols)
        ret = {}
        for i in range(n):
            key = cols[i]
            val = arr[i]
            ret[key] = val
        return ret

    def update(self,ticker):
        self.ticker = ticker

    def format_df(self, df):
        item_names = []
        

        print(type(df.columns[0])," ",str(type(df.columns[0])))
        print(df.columns)
        years = [str(col).split(" ")[0] for col in df.columns]
        
        data = {}
        try:
            df.index = df.index.strftime('%m/%d/%Y')
            df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
            data_dict = df.to_dict(orient='index')
            json_data = json.dumps(data_dict, indent=4)
            return json_data
        except:
            for i in range(len(df)):
                r = df.iloc[i]
                row_name = r.name
                item_names.append(row_name)

            for i in range(len(item_names)):
                name = item_names[i]
                arr = list(df.iloc[i])
                data[name] = arr

            data["Date"] = years
            item_names.insert(0, "Date")

            new_df = pd.DataFrame(data, columns=item_names)
            
            num_rows = len(new_df)
            
            columns= list(new_df.columns)
            idx = columns.index("Date")
            ret = {}
            columns.pop(idx)
            
            for i in range(num_rows):
                row = new_df.iloc[i].values.tolist()
                date = row.pop(idx)
                rowData = self.align(columns, row)
                ret[date] = rowData
            return ret
            


    def financial_statements(self,stock):
        income_statement = stock.financials
        balance_sheet = stock.balance_sheet
        cash_flow = stock.cashflow

        hm = {
            "Income_Statement": income_statement,
            "Balance_Sheet": balance_sheet,
            "Cash_Flow": cash_flow
        }

        for key, df in hm.items():
            new_df = self.format_df(df)
            hm[key] = new_df
        return hm
        
    def data(self,ticker):
        financial_data = ticker.info
        metrics = {
            "market_capitalization": self.formatNumber(financial_data.get("marketCap", "N/A")),
            "basic_eps": financial_data.get("trailingEps", "N/A"),
            # "debt_to_equity_ratio": f"{financial_data.get('debtToEquity', 0):.2f}",  # Not included due to accuracy issues
            "diluted_eps": financial_data.get("dilutedEps", "N/A"),
            "dividend_yield": f"{(financial_data.get('dividendYield', 0) * 100):.2f}%",
            "free_cash_flow": self.formatNumber(financial_data.get("freeCashflow", "N/A")),
            "net_income": self.formatNumber(financial_data.get("netIncomeToCommon", "N/A")),
            "pe_ratio": f"{financial_data.get('trailingPE', 0):.2f}",
            "ps_ratio": f"{financial_data.get('priceToSalesTrailing12Months', 0):.2f}",
            "profit_margin": f"{(financial_data.get('profitMargins', 0) * 100):.2f}%",
            "revenues": self.formatNumber(financial_data.get("totalRevenue", "N/A")),
            # "sales_per_share": f"{financial_data.get('revenuePerShare', 0):.2f}",  # Not included due to accuracy issues
            "total_equity": self.formatNumber(financial_data.get("totalAssets", "N/A")),
            "total_liabilities": self.formatNumber(financial_data.get("totalLiab", "N/A"))
        }

        md = {
            "name" : financial_data["longName"],
            "industry" : financial_data.get("industry",""),
            "sector" : financial_data.get("sector",""),
            "description" : financial_data["longBusinessSummary"],
            "marketItems":metrics,
            "ticker": self.ticker
        }
        return md

    def chart(self, ticker):
        hd = ticker.history(period="ytd")
        
        data = hd.reset_index().set_index('Date') 
        return data
    
    def refresh(self):
        tckr = self.ticker
        ticker = yf.Ticker(tckr)
        ret = {
            "data" : self.data(ticker),
            "chart" : self.chart(ticker),
            "financial_statements" : self.financial_statements(ticker)
        }
        if(isinstance(ret['chart'], pd.DataFrame)):
            ret['chart'] = self.format_df(ret['chart'])
        
        return ret