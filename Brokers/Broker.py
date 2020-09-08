import alpaca_trade_api as tradeapi
from datetime import timedelta
import time
import logging

import config

# https://docs.alpaca.markets/api-documentation/api-v2/
# https://github.com/alpacahq/Momentum-Trading-Example/blob/master/algo.py


class Broker:

    def __init__(self):
        self.APCA_API_KEY_ID = config.APCA_API_KEY_ID
        self.APCA_API_SECRET_KEY = config.APCA_API_SECRET_KEY
        self.APCA_API_BASE_URL = config.APCA_API_BASE_URL

        self.alpaca_api = tradeapi.REST(
            self.APCA_API_KEY_ID, self.APCA_API_SECRET_KEY, self.APCA_API_BASE_URL, 'v2')

    def wait_to_trade(self, time_delay_min=90):
        """
        time_delay_min: time to wait in addition to the market_open
                        default = 90 --> market_open 09:30 --> start of trading 11:00
        """
        logging.info("wait_to_trade start")

        # get as timestamps in UTC: current timestamp, is_open, next_open, next_close
        clock = self.alpaca_api.get_clock()
        if clock.is_open:
            logging.info("market is_open")
            logging.info("wait_to_trade end")
            return
        
        # get time to wait before the market opens
        time_to_wait_market_open = clock.next_open - clock.timestamp
        # add some time, do not start trading exactly at market open
        time_to_wait = time_to_wait_market_open + \
            timedelta(minutes=time_delay_min)
        # convert into seconds
        time_to_wait_seconds = int(time_to_wait.total_seconds()) + 1
        # sleep until time to start trading
        logging.info("going to sleep")
        time.sleep(time_to_wait_seconds)

        logging.info("wait_to_trade end")

    def order_asset(self, symbol, qty, side):
        pass

    def check_account_tradeable(self):
        pass

    def get_account_cash(self):
        pass

    def check_symbols(self, param):
        pass
