import config
import time
import datetime
from finnhub import Client
import websocket
import json
import requests


class Finnhub:
    """
    https://finnhub.io/docs/api#introduction

    API Rate Limiting:
        60 API calls/minute
        30 API calls/ second
        Exceed --> status code 429
    """

    def __init__(self, token=config.FINNHUB_TOKEN):
        self.finnhub_token = token
        self.finnhub_client = Client(api_key=self.finnhub_token)

    def get_last_trade(self, symbol):
        """
        last trade (real-time)
        https://finnhub.io/docs/api#websocket-trades
        short-lived one-off send-receive websocket

        Args:
            symbol (str): single symbol/stock

        Returns:
            trade_data (dict):
                p --> price of the last trade
                s --> symbol
                t --> utc timestamp in seconds
                datetime_utc --> datetime representation of the timestamp
                v --> volume of the single trade
        """
        ws = websocket.create_connection("wss://ws.finnhub.io?token=" + self.finnhub_token)
        ws.send(json.dumps({"type": "subscribe", "symbol": symbol}))
        result = json.loads(ws.recv())

        if 'type' in result:
            if result['type'] == 'trade':
                trade_data = result['data'][0]
                trade_data['t'] = trade_data['t'] / 1000  # convert from timestamp in milliseconds to seconds
                datetime_utc = datetime.datetime.fromtimestamp(trade_data['t']).strftime('%Y-%m-%d %H:%M:%S')
                trade_data['datetime_utc'] = datetime_utc
                ws.close()
                return trade_data
        ws.close()
        return None

    def get_quote(self, symbol):
        """
        few min (~1-5min) delayed OHLC + previous close + timestamp + datetime
        https://finnhub.io/docs/api#quote

        Args:
            symbol (str): single symbol/stock

        Returns:
            quote (dict):
                o --> Open price of the day
                h --> High price of the day
                l --> Low price of the day
                c --> Current price
                pc --> Previous close price
                t --> UNIX timestamp.
                datetime_utc --> t in datetime format
        """
        quote = self.finnhub_client.quote(symbol=symbol)
        quote['datetime_utc'] = datetime.datetime.fromtimestamp(quote['t']).strftime('%Y-%m-%d %H:%M:%S')
        return quote

    def get_stock_candles(self, symbol, resolution='D', amount_candles=1):
        """
        https://finnhub.io/docs/api#stock-candles

        Args:
            symbol (str): single symbol/stock
            resolution (str): Supported resolution includes 1, 5, 15, 30, 60, D, W, M .
            amount_candles: amount of candles which should be returned

        Returns:
            candles (dict of list):
                o --> List of open prices for returned candles.
                h --> List of high prices for returned candles.
                l --> List of low prices for returned candles.
                c --> List of close prices for returned candles.
                v --> List of volume data for returned candles.
                t --> List of timestamp for returned candles.
                s --> Status of the response. This field can either be ok or no_data.
        """

        # ToDo
        _from = int(
            datetime.datetime.strptime('2019-09-07', "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc).timestamp())
        _to = int(
            datetime.datetime.strptime('2020-09-09', "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc).timestamp())

        # adjusted price (in case of stock splits etc.)!
        response = self.finnhub_client.stock_candles(symbol=symbol, resolution=resolution, _from=_from, to=_to,
                                                     adjusted=True)
        if response['s'] != 'no_data':
            return response
        else:
            return None

    def get_change_pct_prev_day(self, symbol):
        """

        Args:
            symbol: single symbol/stock

        Returns:
            percentage (float): percentage change to the previous day
        """
        quote = self.get_quote(symbol=symbol)
        return (-1 + (float(quote['c'] / float(quote['pc'])))) * 100

    def get_support_resistance(self, symbol, resolution='D'):
        """
        https://finnhub.io/docs/api#support-resistance

        Args:
            symbol (str): symbol/stock
            resolution (str): Supported resolution includes 1, 5, 15, 30, 60, D, W, M .

        Returns:
            levels (list): Array of support and resistance levels.

        """
        return self.finnhub_client.support_resistance(symbol=symbol, resolution=resolution)

    def get_aggregate_indicators(self, symbol, resolution='D'):
        """
        https://finnhub.io/docs/api#aggregate-indicator

        Args:
            symbol (str): symbol/stock
            resolution (str): Supported resolution includes 1, 5, 15, 30, 60, D, W, M .

        Returns:
            technicalAnalysis: Number of indicator signals strong buy, buy, neutral, sell, strong sell signals.
                count: Number of indicators for each signal
                buy: Number of buy signals
                neutral: Number of neutral signals
                sell: Number of sell signals
            signal: Aggregate Signal
            trend: Whether the market is trending.
                adx: ADX reading
                trending: Whether market is trending or going sideway
        """
        return self.finnhub_client.aggregate_indicator(symbol=symbol, resolution=resolution)

    def get_index_symbols(self, symbol='^NDX'):
        """
        https://finnhub.io/docs/api#indices-constituents

        Args:
            symbol (str): ^GSPC (S&P 500), ^NDX (Nasdaq 100), ^DJI (Dow Jones)

        Returns:
            symbols (dict): all symbols of the specified index
        """
        return self.finnhub_client.indices_const(symbol=symbol)['constituents']
