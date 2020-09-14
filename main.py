import logging
import time
import sys

from Brokers.Alpaca import Alpaca
from Strategies.Market import Market
from Data_Providers.DataProvider import DataProvider

# Setup global logger
format='%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(filename=time.strftime("%Y-%m-%d") + '.log',
                    level=logging.INFO, format=format)
# add
root = logging.getLogger()
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter(format)
handler.setFormatter(formatter)
root.addHandler(handler)

def main():
    # strategy = Market(broker=Alpaca())
    # strategy.run()

    data_provider = DataProvider()
    # print(data_provider.get_market_status())
    # print(data_provider.market_holiday())
    # print(data_provider.get_index_symbols())

    # print(data_provider.get_quote(symbol='AAPL'))
    # print(data_provider.get_change_pct_prev_day(symbol='AAPL'))
    # print(data_provider.get_last_trade(symbol='AAPL'))
    print(data_provider.get_stock_candles(symbol='AAPL'))

    # print(data_provider.get_support_resistance(symbol='AAPL'))
    # print(data_provider.get_aggregate_indicators(symbol='AAPL'))


if __name__ == "__main__":
    try:
        logging.info('Starting Application')
        main()
    except Exception as e:
        logging.exception("Exception in main loop")
