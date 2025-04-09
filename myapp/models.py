from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime, timedelta
import math



class User(AbstractUser):
    watchlist = models.TextField(blank=True, default="")
    
    def get_watchlist(self):
        if self.watchlist:
            return self.watchlist.split("@")[:-1] 
        return []

    def add_to_watchlist(self, tckr):
        if tckr and f"{tckr}@" not in self.watchlist:
            self.watchlist += f"{tckr}@"
            self.save()

    def remove_from_watchlist(self, tckr):
        if tckr and f"{tckr}@" in self.watchlist:
            self.watchlist = self.watchlist.replace(f"{tckr}@", "")
            self.save()

    def __str__(self):
        return self.username


class Stock(models.Model):
    id = models.BigAutoField(primary_key=True)  # Auto-incrementing 64-bit integer
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
    similarassets = models.TextField()

    def needsRefresh(self):
        today = datetime.now().date()
        one_year_ago = today - timedelta(days=365)
        return self.last_updated <= one_year_ago

    def get_similar(self):
        S = self.similarassets.split("@")
        return S
    
    def update_similar(self, new_sim):
        st = ""
        for ticker in new_sim:
            st += (ticker + "@")
        self.similarassets = st
    
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

    def replace_nan(self, value):
        # Check if the value is NaN
        if isinstance(value, float) and math.isnan(value):
            return -1
        return value

    def marketItems(self):
        ret = {
            "Market Capitalization": self.replace_nan(self.moneyForm(self.market_capitalization)),
            "Basic EPS": self.replace_nan(self.basic_eps),
            "Diluted EPS": self.replace_nan(self.diluted_eps),
            "Dividend Yield": self.replace_nan(self.percentForm(self.dividend_yield)),
            "Free Cash Flow": self.replace_nan(self.moneyForm(self.free_cash_flow)),
            "Net_income": self.replace_nan(self.moneyForm(self.net_income)),
            "PE Ratio": self.replace_nan(self.pe_ratio),
            "PS Ratio": self.replace_nan(self.ps_ratio),
            "Profit Margin": self.replace_nan(self.percentForm(self.profit_margin)),
            "Revenues": self.replace_nan(self.moneyForm(self.revenues)),
            "Total Equity": self.replace_nan(self.moneyForm(self.total_equity)),
            "Total Liabilities": self.replace_nan(self.moneyForm(self.total_liabilities)),
        }
        return ret
        
    def data(self):
        return {
            "name": self.name,
            "description": self.description,
            "industry": self.industry,
            "sector": self.sector,
            "djia": self.djia,
            "sp500": self.sp500,
            "last_updated": self.last_updated.strftime("%Y-%m-%d") if self.last_updated else "N/A",
            "market_items": self.marketItems(),
            "similar" : self.similarassets
        }
        
    def updateItem(self, key, value):
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            raise ValueError(f"Invalid field: {key}")
        self.save()