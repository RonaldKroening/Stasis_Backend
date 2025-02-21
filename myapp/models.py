from django.db import models
import bcrypt
class User(models.Model):
    username = models.CharField(max_length=30)
    password = models.CharField(max_length=50)
    watchlist = models.TextField()
    def __str__(self):
        return self.username
    
    def get_watchlist(self):
        W = self.watchlist.split("@")
        W.pop(-1)
        return W
    
    def add_to_watchlist(self, tckr):
        if(tckr not in self.watchlist):
            self.watchlist = self.watchlist+ (tckr+"@")
    
    def remove_from_watchlist(self,tckr):
        self.watchlist = self.watchlist.replace("tckr@","")      
    
    def valid(self, username,password):
        if bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8')) and self.username == username:
            return True
        else:
            return False


class Stock(models.Model):
    id = models.CharField(max_length=20, unique=True, primary_key=True)
    ticker = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    description = models.TextField()
    industry = models.CharField(max_length=100)
    sector = models.CharField(max_length=100)
    djia = models.BooleanField(default=False)
    sp500 = models.BooleanField(default=False)
    market_capitalization = models.BigIntegerField(null=True, blank=True)
    basic_eps = models.FloatField(null=True, blank=True)
    diluted_eps = models.FloatField(null=True, blank=True)
    dividend_yield = models.FloatField(null=True, blank=True)
    free_cash_flow = models.BigIntegerField(null=True, blank=True)
    net_income = models.BigIntegerField(null=True, blank=True)
    pe_ratio = models.FloatField(null=True, blank=True)
    ps_ratio = models.FloatField(null=True, blank=True)
    profit_margin = models.FloatField(null=True, blank=True)
    revenues = models.BigIntegerField(null=True, blank=True)
    total_equity = models.BigIntegerField(null=True, blank=True)
    total_liabilities = models.BigIntegerField(null=True, blank=True)
    last_updated = models.DateField(auto_now=True)
    similar = models.TextField()


    def get_similar(self):
        S = self.similar.split("@")
        return S
    
    def update_similar(self,new_sim):
        st = ""
        for ticker in new_sim:
            st += (ticker+"@")
        self.similar = st
    
    def __str__(self):
        return f"{self.name} ({self.ticker})"

    def moneyForm(self, value):
        if value is None:
            return "N/A"
        return f"{value:,}"

    def percentForm(self, value):
        if value is None:
            return "N/A"
        return f"{value:.2f}%"

    def marketItems(self):
        return {
            "market_capitalization": self.moneyForm(self.market_capitalization),
            "basic_eps": self.basic_eps,
            "diluted_eps": self.diluted_eps,
            "dividend_yield": self.percentForm(self.dividend_yield),
            "free_cash_flow": self.moneyForm(self.free_cash_flow),
            "net_income": self.moneyForm(self.net_income),
            "pe_ratio": self.pe_ratio,
            "ps_ratio": self.ps_ratio,
            "profit_margin": self.percentForm(self.profit_margin),
            "revenues": self.moneyForm(self.revenues),
            "total_equity": self.moneyForm(self.total_equity),
            "total_liabilities": self.moneyForm(self.total_liabilities),
        }
        
    def data(self):
        return {
            "name": self.name,
            "description": self.description,
            "industry": self.industry,
            "sector": self.sector,
            "djia": self.djia,
            "sp500": self.sp500,
            "last_updated": self.last_updated.strftime("%Y-%m-%d") if self.last_updated else "N/A",
            "market_items": self.marketItems()
        }
        
    def updateItem(self, key, value):
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            raise ValueError(f"Invalid field: {key}")
        self.save()