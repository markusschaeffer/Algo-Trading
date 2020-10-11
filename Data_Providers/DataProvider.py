from datetime import datetime
import pytz
from Data_Providers.TDAmeritrade import TDAmeritrade
from Data_Providers.FinnHub import Finnhub
from Data_Providers.Polygon import Polygon
import pprint


class DataProvider(TDAmeritrade, Finnhub, Polygon):
    """
    Class aggregating all methods used of different data providers

    Utilized data providers:
        TDAmeritrade    https://developer.tdameritrade.com/apis
        Finnhub         https://finnhub.io
        Polygon         https://polygon.io
    """

    def __init__(self):
        TDAmeritrade.__init__(self)
        Finnhub.__init__(self)
        Polygon.__init__(self)

    @staticmethod
    def map_finnhub_response(response_finnhub, symbol, frequency):
        """

        Args:
            response_finnhub:
            symbol:
            frequency:

        Returns:

        """
        # check len of all response objects is equal
        assert len(response_finnhub['t']) == len(response_finnhub['o']) == len(response_finnhub['h']) \
               == len(response_finnhub['c']) == len(response_finnhub['v'])

        candles = []
        for i in range(0, len(response_finnhub['t'])):
            candle = {
                "ts": response_finnhub['t'][i],
                "ts_utc": datetime.fromtimestamp(response_finnhub['t'][i], pytz.timezone('UTC')).strftime(
                    '%Y-%m-%d %H:%M:%S'),
                "ts_ny": datetime.fromtimestamp(response_finnhub['t'][i], pytz.timezone('US/Eastern')).strftime(
                    '%Y-%m-%d %H:%M:%S'),
                "ts_zurich": datetime.fromtimestamp(response_finnhub['t'][i], pytz.timezone('Europe/Zurich')).strftime(
                    '%Y-%m-%d %H:%M:%S'),
                "symbol": symbol,
                "frequency": frequency,
                "open": response_finnhub['o'][i],
                "high": response_finnhub['h'][i],
                "close": response_finnhub['c'][i],
                "volume": response_finnhub['v'][i]
            }
            candles.append(candle)
        return candles

    @staticmethod
    def map_tdameritrade_response(response_tdameritrade, symbol, frequency):
        """

        Args:
            response_tdameritrade:
            symbol:
            frequency:

        Returns:

        """
        candles = []
        for element in response_tdameritrade['candles']:
            candle = {
                "ts": element['datetime'],
                "ts_utc": datetime.fromtimestamp(element['datetime'] / 1000, pytz.timezone('UTC')).strftime(
                    '%Y-%m-%d %H:%M:%S'),
                "ts_ny": datetime.fromtimestamp(element['datetime'] / 1000, pytz.timezone('US/Eastern')).strftime(
                    '%Y-%m-%d %H:%M:%S'),
                "ts_zurich": datetime.fromtimestamp(element['datetime'] / 1000,
                                                    pytz.timezone('Europe/Zurich')).strftime(
                    '%Y-%m-%d %H:%M:%S'),
                "symbol": symbol,
                "frequency": frequency,
                "open": element['open'],
                "high": element['high'],
                "close": element['close'],
                "volume": element['volume']
            }
            candles.append(candle)
        return candles
