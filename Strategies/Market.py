import time
import logging
from math import floor

from Brokers.Broker import Broker
from Strategies.Strategy import Strategy


class Market(Strategy):
    """
        buy if market is positive at 11:00 NY Time
        sell/short if market is negative at 11:00 NY Time
    """

    def __init__(self, broker=Broker()):
        super().__init__()
        self.broker = broker  # override broker
        self.risk_pct = 1.0  # max percentage of the portfolio to allocate to any one position
        self.symbols = self.symbols_market
        self.assets = {
            "SPY": {
                "factor": 0.333,
                "latest_price": 0.0,
                "cash_to_allocate": 0.0,
                "shares_to_order": 0.0
            },
            "DJIA": {
                "factor": 0.333,
                "latest_price": 0.0,
                "cash_to_allocate": 0.0,
                "shares_to_order": 0.0
            },
            "QQQ": {
                "factor": 0.333,
                "latest_price": 0.0,
                "cash_to_allocate": 0.0,
                "shares_to_order": 0.0
            }
        }

    def calc_shares_to_order(self):
        """
        update latest_price, cash_to_allocate, shares_to_order

        cash per asset to allocate = account cash * max risk per trade * factor of asset
        amount of shares to order per asset = floor(cash per asset to allocate / latest price)
        """
        latest_prices = self.data_api.get_latest_price(self.symbols)
        for symbol in self.symbols:
            self.assets[symbol]["latest_price"] = latest_prices[symbol]
            self.assets[symbol]["cash_to_allocate"] = self.cash * \
                                                      self.risk_pct * self.assets[symbol]["factor"]
            self.assets[symbol]["shares_to_order"] = floor(
                self.assets[symbol]["cash_to_allocate"] / self.assets[symbol]["latest_price"])

    def run(self):
        logging.info("run start")
        # self.broker.wait_to_trade()
        # while True:
        #    if self.broker.api.get_clock().is_open == False:
        #        time.sleep(1)
        #    else:
        #        break
        logging.info("time to trade")

        # check if account is able to trade
        tradeable = self.broker.check_account_tradeable()
        if not tradeable:
            logging.critical("account not able to trade")
            return

        # check if anything from the last day is open, terminate if so

        # get amount of cash available
        self.cash = self.broker.get_account_cash()
        print("account_cash: " + str(self.cash))

        # calculate how much shares to order for each asset
        self.calc_shares_to_order()

        # check if market is positive or negative (buy or sell decision)
        market_positive = self.check_change_positive_daily(self.symbol_market)
        if market_positive:
            side = 'buy'
        else:
            side = 'sell'

        # order assets according to strategy
        for key, value in self.assets.items():
            self.broker.order_asset(
                symbol=key, qty=value["shares_to_order"], side=side)
