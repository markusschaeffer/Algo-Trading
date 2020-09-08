from Data_Providers.DataProvider import DataProvider
import config


class Finnhub(DataProvider):

    def __init__(self):
        self.TOKEN = config.FINNHUB_TOKEN
