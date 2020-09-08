from Brokers.Broker import Broker
from Data_Providers.IEXCloud import IEXCloud


class Strategy:

    def __init__(self, broker=Broker(), dataapi=IEXCloud()):
        self.stop_loss_pct = .95  # stop limit to default to
        self.take_profit_pct = 1.05  # take profit to default to
        self.risk_pct = 0.1  # max percentage of the portfolio to allocate to any one position
        self.market_positive_threshold_pct = 0.0  # value in pct at which the market is considered to be positive

        self.broker = broker
        self.data_api = dataapi

        # SPX       --> SPY ETF
        # DJIA      --> DIA ETF
        # NASDAQ    --> QQQ ETF
        self.symbols_market = self.broker.check_symbols(['SPY', 'DIA', 'QQQ'])
        self.symbol_market = self.broker.check_symbols(['SPY'])

        self.cash = 0.0

    def check_change_positive_daily(self, symbol, broker=Broker(), dataapi=IEXCloud()):
        """
        return:
            True if market is positive (compared to previous day and compared to opening price of today)
            False if market is negative

        """
        change_prev_day_pct = self.data_api.get_change_pct_prev_day(symbol)
        quote = self.data_api.get_quote(symbol)
        if (change_prev_day_pct > self.market_positive_threshold_pct) and (quote.latest_price > quote.open):
            return True
        else:
            return False
