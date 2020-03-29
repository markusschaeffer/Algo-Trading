from brokers.broker import Broker
from data.data import Data
from watchlist import Watchlist

class Strategy:

    def __init__(self, broker = Broker(), dataapi = Data()):
        self.stop_loss_pct = .95  # stop limit to default to
        self.take_profit_pct = 1.05 # take profit to default to
        self.risk_pct = 0.1 # max percentage of the portfolio to allocate to any one position
        self.market_positiv_threshold_pct = 0.0  # value in pct at which the market is considered to be positive

        self.broker = broker
        self.dataapi = dataapi

        self.wl = Watchlist()
        # get symbols from own watchlist
        self.symbols_watchlist = self.wl.getSymbols(
            filterExpression='#trading = :true',
            expressionAttributeValues={':true': True},
            expressionAttributeNames={'#name': 'name', '#trading': 'trading'})
        self.symbols_watchlist.remove('GOOG') # only use GOOGL

        # SPX       --> SPY ETF
        # DJIA      --> DIA ETF
        # NASDAQ    --> QQQ ETF
        self.symbols_market = self.broker.check_symbols(['SPY', 'DIA', 'QQQ'])
        self.symbol_market = self.broker.check_symbols(['SPY'])

        self.cash = 0.0

    def check_change_positive_daily(self, symbol, broker = Broker(), dataapi = Data()):
        """
        @return:
            True if market is positiv (compared to previous day and compared to opening price of today)
            False if market is negative
        """
        change_prev_day_pct = self.dataapi.get_change_pct_prev_day(symbol)
        quote = self.dataapi.get_quote(symbol)
        if (change_prev_day_pct > self.market_positiv_threshold_pct) and (quote.latest_price > quote.open):
            return True
        else:
            return False