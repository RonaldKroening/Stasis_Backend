from django.test import TestCase
from .models import Stock, User

class StockModelTests(TestCase):
    def setUp(self):
        self.stock = Stock.objects.create(
            ticker="AAPL",
            name="Apple Inc.",
            description="Apple Inc. designs, manufactures, and markets smartphones...",
            industry="Consumer Electronics",
            sector="Technology",
            djia=True,
            sp500=True,
            market_capitalization=3576343560192,
            basic_eps=6.09,
            diluted_eps=None,
            dividend_yield=0.43,
            free_cash_flow=110846001152,
            net_income=93736001536,
            pe_ratio=39.05,
            ps_ratio=9.15,
            profit_margin=23.97,
            revenues=391034994688,
            total_equity=None,
            total_liabilities=None,
        )

    def test_moneyForm(self):

        self.assertEqual(self.stock.moneyForm(3576343560192), "3,576,343,560,192")
        self.assertEqual(self.stock.moneyForm(None), "N/A")
        self.assertEqual(self.stock.moneyForm(1000), "1,000")

    def test_percentForm(self):
        self.assertEqual(self.stock.percentForm(0.43), "0.43%")
        self.assertEqual(self.stock.percentForm(None), "N/A")
        self.assertEqual(self.stock.percentForm(23.97), "23.97%")

    def test_marketItems(self):

        expected_market_items = {
            "Market Capitalization": "3,576,343,560,192",
            "Basic EPS": 6.09,
            "Diluted EPS": "N/A",
            "Dividend Yield": "0.43%",
            "Free Cash Flow": "110,846,001,152",
            "Net Income": "93,736,001,536",
            "P/E Ratio": 39.05,
            "P/S Ratio": 9.15,
            "Profit Margin": "23.97%",
            "Revenues": "391,034,994,688",
            "Total Equity": "N/A",
            "Total Liabilities": "N/A",
        }
        self.assertEqual(self.stock.marketItems(), expected_market_items)

    def test_update_market_items(self):
        self.stock.update_market_items(
            market_capitalization=4000000000000,
            dividend_yield=0.50,
            net_income=100000000000,
            revenues=400000000000,
        )

        self.assertEqual(self.stock.market_capitalization, 4000000000000)
        self.assertEqual(self.stock.dividend_yield, 0.50)
        self.assertEqual(self.stock.net_income, 100000000000)
        self.assertEqual(self.stock.revenues, 400000000000)

        updated_market_items = self.stock.marketItems()
        self.assertEqual(updated_market_items["Market Capitalization"], "4,000,000,000,000")
        self.assertEqual(updated_market_items["Dividend Yield"], "0.50%")
        self.assertEqual(updated_market_items["Net Income"], "100,000,000,000")
        self.assertEqual(updated_market_items["Revenues"], "400,000,000,000")

    def test_update_market_items_invalid_field(self):

        with self.assertRaises(ValueError):
            self.stock.update_market_items(invalid_field=12345)
            

class UserModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="testname",
            password="pass",
            watchlist="GOOG@TSLA@MSFT@"
        )
        
    def test_login(self):
        testpass1 = "notpass"
        testpass2 = "pass"
        self.assertEqual((testpass1 == self.user.password),False)
        self.assertEqual((testpass2 == self.user.password),True)
    
    def test_watchlist(self):
        w = self.user.get_watchlist()
        self.assertEqual(len(w),3)
        self.assertEqual(w, ["GOOG","TSLA","MSFT"])
        
        self.user.add_to_watchlist("AAPL")
        self.assertEqual(self.user.get_watchlist,["GOOG","TSLA","MSFT","AAPL"])
        
        self.user.remove_from_watchlist("TSLA")
        self.assertEqual(self.user.get_watchlist,["GOOG","MSFT","AAPL"])