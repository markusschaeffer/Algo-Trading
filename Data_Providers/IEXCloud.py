from iexfinance.stocks import Stock
import config


class IEXCloud:
    """
    https://iexcloud.io/docs/api/

    API Rate Limiting:
        50,000 core messages/month
        https://iexcloud.io/core-data-catalog/

    Further Links/Information:
        https://github.com/addisonlynch/iexfinance
        https://github.com/addisonlynch/iex-examples
        https://iexcloud.io/docs/api/#stocks
        https://addisonlynch.github.io/iexfinance/stable/stocks.html#
    """

    def __init__(self, token=config.IEX_TOKEN):
        self.iexcloud_token = token

    def get_book_for_symbol(self):
        """
        https://iexcloud.io/docs/api/#book
        """
        pass

    def get_market_volume(self):
        """
        https://iexcloud.io/docs/api/#market-volume-u-s
        """
        pass
