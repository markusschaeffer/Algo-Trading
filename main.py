import logging
import time
from pprint import pprint
from datetime import datetime, timedelta
import csv
import sys, os

from Brokers.Alpaca import Alpaca
from Strategies.Market import Market
from Data_Providers.DataProvider import DataProvider

# Setup global logger
format = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(filename=time.strftime("%Y-%m-%d") + '.log',
                    level=logging.INFO, format=format)
# add
root = logging.getLogger()
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter(format)
handler.setFormatter(formatter)
root.addHandler(handler)


def export_historical_data(data_provider, data_provider_name, symbols, frequencies, _from, _to):
    """

    Args:
        data_provider (Data_Provider object):
        data_provider_name(str):
        symbols (list):
        frequencies (list):
        _to (int):
        _from (int):
    """
    _from_default = _from
    _to_default = _to
    now_finnhub = DataProvider.finnhub_seconds_since_epoch(datetime.now())
    now_tdameritrade = datetime.now()

    for frequency in frequencies:
        for symbol in symbols:
            logging.info("Symbol: " + symbol)
            _from = _from_default
            _to = _to_default
            filename = os.path.dirname(os.path.abspath(__file__)) + \
                       '/Data/' + data_provider_name + '/' + str(frequency) + 'min/' + symbol + '.csv'
            with open(filename, mode='w') as csv_file:
                fieldnames = ['symbol', 'frequency', 'ts', 'ts_utc', 'ts_ny', 'ts_zurich', 'open', 'high', 'close',
                              'volume']
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writeheader()

                # Finnhub
                if data_provider_name == 'Finnhub':
                    while _to < now_finnhub:
                        resp = data_provider.finnhub_get_stock_candles(symbol=symbol, _from=_from, _to=_to,
                                                                       resolution=frequency)
                        if resp is not None:
                            mapped_response = data_provider.map_finnhub_response(resp,
                                                                                 symbol=symbol,
                                                                                 frequency=frequency)
                            logging.info(mapped_response[0]['ts_ny'])
                            for candle in mapped_response:
                                writer.writerow(
                                    {'symbol': symbol,
                                     'frequency': frequency,
                                     'ts': candle['ts'],
                                     'ts_utc': candle['ts_utc'],
                                     'ts_ny': candle['ts_ny'],
                                     'ts_zurich': candle['ts_zurich'],
                                     'open': candle['open'],
                                     'high': candle['high'],
                                     'close': candle['close'],
                                     'volume': candle['volume']
                                     })
                        _from = DataProvider.finnhub_seconds_since_epoch(
                            datetime.fromtimestamp(_from) + timedelta(days=1))
                        _to = DataProvider.finnhub_seconds_since_epoch(datetime.fromtimestamp(_to) + timedelta(days=1))
                        time.sleep(1)

                # TDAmeritrade
                if data_provider_name == 'TDAmeritrade':
                    while _to < now_tdameritrade:
                        if frequency == 1:
                            frequency = data_provider.tda_client.PriceHistory.Frequency.EVERY_MINUTE
                        elif frequency == 5:
                            frequency = data_provider.tda_client.PriceHistory.Frequency.EVERY_FIVE_MINUTES
                        elif frequency == 15:
                            frequency = data_provider.tda_client.PriceHistory.Frequency.EVERY_FIFTEEN_MINUTES
                        elif frequency == 30:
                            frequency = data_provider.tda_client.PriceHistory.Frequency.EVERY_THIRTY_MINUTES
                        else:
                            logging.critical(frequency)
                            raise Exception('Unknown frequency found')

                        resp = data_provider.tdameritrade_client_get_price_history(symbol=symbol,
                                                                                   period_type=None,
                                                                                   period=None,
                                                                                   frequency_type=data_provider.tda_client.PriceHistory.FrequencyType.MINUTE,
                                                                                   startDate=_from,
                                                                                   endDate=_to,
                                                                                   frequency=frequency)

                        if frequency == data_provider.tda_client.PriceHistory.Frequency.EVERY_MINUTE:
                            frequency = 1
                        elif frequency == data_provider.tda_client.PriceHistory.Frequency.EVERY_FIVE_MINUTES:
                            frequency = 5
                        elif frequency == data_provider.tda_client.PriceHistory.Frequency.EVERY_FIFTEEN_MINUTES:
                            frequency = 15
                        elif frequency == data_provider.tda_client.PriceHistory.Frequency.EVERY_THIRTY_MINUTES:
                            frequency = 30
                        else:
                            logging.critical(frequency)
                            raise Exception('Unknown frequency found')

                        if resp is not None:
                            mapped_response = data_provider.map_tdameritrade_response(resp, symbol=symbol,
                                                                                      frequency=frequency)
                            for candle in mapped_response:
                                writer.writerow(
                                    {'symbol': symbol,
                                     'frequency': frequency,
                                     'ts': candle['ts'],
                                     'ts_utc': candle['ts_utc'],
                                     'ts_ny': candle['ts_ny'],
                                     'ts_zurich': candle['ts_zurich'],
                                     'open': candle['open'],
                                     'high': candle['high'],
                                     'close': candle['close'],
                                     'volume': candle['volume']
                                     })

                        _from = _from + timedelta(days=1)
                        _to = _to + timedelta(days=1)
                        time.sleep(0.5)


def main():
    data_provider = DataProvider()

    if True:
        # TDAmeritrade export historical data
        _from = datetime.strptime('2020-09-01 09:30:00', '%Y-%m-%d %H:%M:%S')
        _to = datetime.strptime('2020-09-01 16:00:00', '%Y-%m-%d %H:%M:%S')

        export_historical_data(data_provider=data_provider,
                               data_provider_name='TDAmeritrade',
                               symbols=data_provider.finnhub_get_index_symbols('^NDX'),
                               frequencies=[1, 5, 15, 30],
                               _from=_from,
                               _to=_to)

    if False:
        # Finnhub export historical data
        # 09:30 us_eastern --> 13:30 utc
        # 16:00 us_eastern --> 20:00 utc
        _from = data_provider.finnhub_seconds_since_epoch(datetime.strptime('2019-10-01 13:30:00', '%Y-%m-%d %H:%M:%S'))
        _to = data_provider.finnhub_seconds_since_epoch(datetime.strptime('2019-10-01 20:00:00', '%Y-%m-%d %H:%M:%S'))

        export_historical_data(data_provider=data_provider,
                               data_provider_name='Finnhub',
                               symbols=data_provider.finnhub_get_index_symbols('^NDX'),
                               frequencies=[15],
                               _from=_from,
                               _to=_to)


if __name__ == "__main__":
    try:
        logging.info('Starting Application')
        main()
    except Exception as e:
        logging.exception("Exception in main loop")
