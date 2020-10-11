from Brokers.Broker import Broker


class Strategy:

    def __init__(self, broker=Broker()):
        self.stop_loss_pct = .95  # stop limit to default to
        self.take_profit_pct = 1.05  # take profit to default to
        self.risk_pct = 0.1  # max percentage of the portfolio to allocate to any one position
        self.market_positive_threshold_pct = 0.0  # value in pct at which the market is considered to be positive

        self.broker = broker

        # SPX       --> SPY ETF
        # DJIA      --> DIA ETF
        # NASDAQ    --> QQQ ETF
        self.symbols_market = self.broker.check_symbols(['SPY', 'DIA', 'QQQ'])
        self.symbol_market = self.broker.check_symbols(['SPY'])

        self.cash = 0.0
