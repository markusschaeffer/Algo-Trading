import logging

from Brokers.Broker import Broker
from Strategies.Strategy import Strategy


# https://addisonlynch.github.io/iexfinance/stable/stocks.html#stocks-movers

class Market_Movers(Strategy):

    def __init__(self, broker=Broker()):
        super().__init__()
        self.broker = broker

    def run(self):
        pass
