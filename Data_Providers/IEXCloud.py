from iexfinance.stocks import Stock
from Data_Providers.DataProvider import DataProvider
import config


# https://github.com/addisonlynch/iexfinance
# https://github.com/addisonlynch/iex-examples


# https://iexcloud.io/docs/api/#stocks
# https://addisonlynch.github.io/iexfinance/stable/stocks.html#

class IEXCloud(DataProvider):

    def __init__(self):
        self.token = config.IEX_TOKEN

    def get_quote(self, symbol, display_percent=True):
        """
        https://iexcloud.io/docs/api/#quote
        """
        return Stock(symbol, token=self.token).get_quote(displayPercent=display_percent)

    def get_latest_price(self, symbol):
        """
        @symbol: a string or list of string

        @return: latestPrice
            Refers to the latest relevant price of the security which is derived from multiple sources. 
            We first look for an IEX real time price. If an IEX real time price is older than 15 minutes,
            15 minute delayed market price is used.
            If a 15 minute delayed price is not available, we will use the current day close price. 
            If a current day close price is not available, we will use the last available closing price
            (listed below as previousClose)
            IEX real time price represents trades on IEX only. 
            Trades occur across over a dozen exchanges, so the last IEX price can be used to indicate
            the overall market price.
            15 minute delayed prices are from all markets using the Consolidated Tape.
            This will not included pre or post market prices.
        """
        return float(Stock(symbol, token=self.token).get_price())

    def get_change_pct_prev_day(self, symbol):
        """
        changePercent:
            Refers to the percent change in price between latestPrice and previousClose (previous day). 

        @return:
            float representing the change in %, e.g. 5 for a 5% change
        """
        return float(self.get_quote(symbol).changePercent)
