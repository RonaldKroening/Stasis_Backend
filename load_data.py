import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')


import django
django.setup()
import json
from myapp.models import Stock 
from myapp.views import upload_json_to_s3 
from myapp.mm import MongoMigrator
import os
import yfinance as yf
from myapp.YahooWrapper import YahooWrapper
# M = MongoMigrator()
# M.migrate()

# i = 0
# for stock in M.stocks:
#     stock_data = stock['data']
#     stock_chart = stock['chart']
#     stock_statements = stock['statements']
#     os.chdir("to_s3_bucket")
#     print(os.getcwd())
#     ticker = stock_data['ticker']
            
#     with open(ticker + "_Chart.json", 'w') as f:
#         f.write(stock_chart)
            
#     with open(ticker+"_FS.json", 'w') as f:
#         f.write(stock_statements)
#     stock_data["id"] = i
#     Stock.objects.create(**stock_data)
#     os.chdir("..")
#     i+=1
# print("Success!")

def load_json(path):
    try:
        with open(path, 'r') as file:
            data = json.load(file)
            return data
    except:
        return None
    
def write_json(path, data):
    with open(path, 'w') as file:
        json.dump(data, file, indent=4)
        
        
path = "to_s3_bucket/ICCT_Chart.json"

with open(path, 'r') as file:
    json_string = file.read()

data = json.loads(json_string)

with open(path, 'w') as file:
    file.write(data)


tickers = []
for file in os.listdir("to_s3_bucket"):
    ticker = file.split("_")[0]
    if(ticker not in tickers):
        tickers.append(ticker)

Y = YahooWrapper("")
for ticker in tickers:
    chart_path = f"to_s3_bucket/{ticker}_Chart.json"
    fs_path = f"to_s3_bucket/{ticker}_FS.json"
    print(chart_path)
    chart_data = load_json(chart_path)
    o = None
    fs_data = load_json(fs_path)
    
    if(chart_data == {} or chart_data == None):
        print(f"{ticker} has no chart")
        Y.update(ticker)
        obj = Y.refresh()
        chart_data = obj['chart']
        write_json(chart_path, chart_data)
        o = obj
    
    
    if(fs_data == {} or fs_data == None):
        print(f"{ticker} has no financial statements")
        fs_data = None
        if(o == None):
            Y.update(ticker)
            obj = Y.refresh()
            fs_data = obj['financial_statements']
        else:
            fs_data = o['financial_statements']
        
        write_json(fs_path, fs_data)
        
print("All Data Accouted For")