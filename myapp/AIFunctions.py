from .models import Stock

def find_similar(ticker):
    n = 6
    stocks = Stock.objects.values_list('description', 'sector','industry')
    descriptions = []
    similar = ["AAPL","BE","GOOG","RTX","CHWY"]
    return similar
    