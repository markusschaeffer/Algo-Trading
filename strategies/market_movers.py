import logging

from brokers.broker import Broker
from strategies.strategy import Strategy

# https://addisonlynch.github.io/iexfinance/stable/stocks.html#stocks-movers

class Market_Movers(Strategy):

    def __init__(self, broker = Broker()):
        super().__init__()
        self.broker = broker

    def run(self):
        pass