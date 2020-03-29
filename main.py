import logging
import time

from brokers.alpaca import Alpaca
from strategies.market_movers import Market_Movers
from strategies.market import Market

# Setup global logger
logging.basicConfig(filename=time.strftime("%Y-%m-%d") +
                    '.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')


def main():
    strategy = Market(broker = Alpaca())
    strategy.run()

if __name__ == "__main__":
    try:
        logging.info('Starting Application')
        main()
    except Exception as e:
        logging.exception("Exception in main loop")