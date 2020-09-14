import config

from Data_Providers.FinnHub import Finnhub
from Data_Providers.Polygon import Polygon


class DataProvider(Finnhub, Polygon):
    """
    Class aggregating all methods used of different data providers

    Utilized data providers:
        Finnhub     https://finnhub.io
        Polygon     https://polygon.io
    """

    def __init__(self):
        Finnhub.__init__(self)
        Polygon.__init__(self)
