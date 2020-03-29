import alpaca_trade_api as tradeapi
import time
import logging

from brokers.broker import Broker
from strategies.strategy import Strategy
import config

# https://docs.alpaca.markets/api-documentation/api-v2/
# https://github.com/alpacahq/Momentum-Trading-Example/blob/master/algo.py


class Alpaca(Broker):

    def __init__(self, strategy=Strategy()):
        super().__init__()
        self.api = self.alpaca_api

    def check_symbols(self, symbols=[]):
        """
        input: 
            A list of stock symbols

        return:
            A list with valid symbols for the brocker
        """

        for symbol in symbols:
            try:
                asset = self.api.get_asset(symbol)
                # print(asset)
            except Exception as e:
                symbols.remove(symbol)
                logging.warning(e)

        return symbols

    def order_asset(self, symbol, qty, latest_price, take_profit_pct, side='buy', type='market', time_in_force='day'):
        """
        https://docs.alpaca.markets/api-documentation/api-v2/orders/

        https://docs.alpaca.markets/trading-on-alpaca/orders/#bracket-orders

        TODO take_profit
        TODO stop_loss
        
        account shorting_enabled: true --> side = 'sell' possible
        """

        try:
            #check if symbol is available
            asset = self.api.get_asset(symbol)
            if asset.tradable != True:
                raise Exception("asset is not tradeable " + symbol)
        except Exception as e:
            logging.warning(e)
            return None

        if side == 'buy':
            response = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type=type,
                time_in_force=time_in_force,
                order_class='bracket',
                take_profit=dict(
                    limit_price=latest_price * take_profit_pct,
                ),
                stop_loss=dict(
                    stop_price='295.5',
                    limit_price='295.5',
                )
            )
        elif side == 'sell':
            response = None
        else:
            response = None

        return response

    def check_account_tradeable(self):
        """
        https://docs.alpaca.markets/api-documentation/api-v2/account/

        return:
            True if account is okay, i.e. able to trade
            False if something is not okay, i.e. not able to trade
        """
        account = self.api.get_account()
        if account.status == 'ACTIVE' and account.account_blocked == False and account.trading_blocked == False:
            return True
        else:
            logging.critical(
                "account not active, account blocked or trading blocked!")
            return False

    def get_account_cash(self):
        """
        https://docs.alpaca.markets/api-documentation/api-v2/account/

        Cash balance
        """
        return float(self.api.get_account().cash)

    def get_account_portfolio_value(self):
        """
        https://docs.alpaca.markets/api-documentation/api-v2/account/

        Cash + long_market_value + short_market_value
        """
        return float(self.api.get_account().equity)

    def check_asset_shortable(self, asset):
        """
        @return: 
            True if asset can be shorted
            False if not
        """
