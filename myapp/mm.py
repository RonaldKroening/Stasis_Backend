import json
from pymongo import MongoClient

class MongoMigrator:
    
    newMappings = {
        "Market Capitalization": "market_capitalization",
        "Basic EPS": "basic_eps",
        "Diluted EPS": "diluted_eps",
        "Dividend Yield": "dividend_yield",
        "Free Cash Flow": "free_cash_flow",
        "Net Income": "net_income",
        "P/E Ratio": "pe_ratio",
        "P/S Ratio": "ps_ratio",
        "Profit Margin": "profit_margin",
        "Revenues": "revenues",
        "Total Equity": "total_equity",
        "Total Liabilities": "total_liabilities",
        "LastUpdated": "last_updated",
    }


    def __init__(self):
        self.client = MongoClient("mongodb+srv://ronald_kroening_64:tcZ5WSsJnu5W5aeX@cluster0.0qo2iwi.mongodb.net/")
    
    def get_all_metadata(self):
        coll = self.client['FinancialData']['MetaData']
        
        documents = coll.find()
        md = []
        for document in documents:
            json_string = json.dumps(document, default=str, indent=4)
            json_object = json.loads(json_string)
            if('marketItems' in json_object):
                kv = {
                    "name" : "NAME",
                    "ticker" : "TCKR",
                    "description" : "DESC",
                    "industry" : "INDUSTRY",
                    "sector" : "SECTOR"
                }
                new_dict = {}
                for key in kv:
                    
                    if(key in json_object):
                        new_dict[key] = json_object[key]
                    elif(kv[key] in json_object):
                        new_dict[key] = json_object[kv[key]]

                for obj in json_object['marketItems']:
                    for key, value in obj.items():
                        if(key in self.newMappings):
                            new_val = str(value)
                            if(',' in new_val):
                                new_val = new_val.replace(",","")
                            if("%" in new_val):
                                new_val = new_val.replace("%","")
                            if("$" in new_val):
                                new_val = new_val.replace("$","")
                            if(new_val == "N/A"):
                                new_val = "-1"
                            
                            
                            new_dict[self.newMappings[key]] = float(new_val)
                if("ticker" in new_dict):
                    md.append(new_dict)
        return md
    
    def get_all_charts_and_statements(self) -> dict:
        coll = self.client['FinancialData']['AllStocks']
        charts_and_statements = {}

        for document in coll.find():
            symbol = document.get("Symbol")
            charts_and_statements[symbol] = {
                "chart": json.dumps(document.get("TimeSeries", {}),default=str),
                "statements": json.dumps(document.get("Financial_Statements", {}),default=str)
            }

        return charts_and_statements
        
    def migrate(self):
        metadata = self.get_all_metadata()
        charts_and_statements = self.get_all_charts_and_statements()
        r = []
        for item in metadata:
            if(item["ticker"] in charts_and_statements):
                obj = charts_and_statements[item['ticker']]
                chart = obj['chart']
                statements = obj['statements']
                block = {
                    "data" : item,
                    "chart" : chart,
                    "statements": statements
                }
                r.append(block)
        self.stocks = r
            
        