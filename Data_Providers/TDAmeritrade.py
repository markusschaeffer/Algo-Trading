import config
import logging
import requests
import json
from requests.exceptions import HTTPError
from datetime import datetime
import pytz
from tda import auth
from tda.client import Client as TDA_CLIENT
import os


class TDAmeritrade:
    """
    https://developer.tdameritrade.com/apis

        API Rate Limiting:
        120 API calls/minute
        2 API calls/second

    tda-api wrapper:
        https://github.com/alexgolec/tda-api
        https://tda-api.readthedocs.io/en/stable/

    """

    def __init__(self, api_key=config.TDA_API_KEY, token_path=config.TDA_TOKEN_PATH, redirect=config.TDA_REDIRECT_URI):
        self.tda_apikey = api_key
        self.tda_token_path = token_path
        self.tda_redirect = redirect

        try:
            self.tda_client = auth.client_from_token_file(config.TDA_TOKEN_PATH, self.tda_apikey)
        except FileNotFoundError:
            from selenium import webdriver
            chromedriver_path = os.path.dirname(os.path.abspath(__file__)) + '\..\chromedriver.exe'
            print(chromedriver_path)
            options = webdriver.ChromeOptions()
            with webdriver.Chrome(executable_path=chromedriver_path, chrome_options=options) as driver:
                self.tda_client = auth.client_from_login_flow(webdriver=driver,
                                                              api_key=self.tda_apikey,
                                                              redirect_url=self.tda_redirect,
                                                              token_path=self.tda_token_path)

    @staticmethod
    def tdameritrade_millis_since_epoch(dt):
        """
        returns the milliseconds since epoch based on a given input datetime object.

        :param dt: datetime object
        :return: milliseconds passed since epoch
        """
        epoch = datetime.utcfromtimestamp(0)  # return the UTC datetime corresponding to the POSIX timestamp
        # total_seconds returns the total
        # number of seconds contained in the duration
        millis_passed_since_epoch = int((dt - epoch).total_seconds() * 1000.0)  # seconds --> milliseconds
        return millis_passed_since_epoch

    def tdameritrade_client_get_price_history(self, symbol='AAPL',
                                              period_type=TDA_CLIENT.PriceHistory.PeriodType.DAY,
                                              period=TDA_CLIENT.PriceHistory.Period.ONE_DAY,
                                              frequency_type=TDA_CLIENT.PriceHistory.FrequencyType.MINUTE,
                                              frequency=TDA_CLIENT.PriceHistory.Frequency.EVERY_MINUTE,
                                              startDate=None, endDate=None, need_extended_hours_data=False):
        try:
            response = self.tda_client.get_price_history(symbol=symbol,
                                                         period_type=period_type,
                                                         period=period,
                                                         frequency_type=frequency_type,
                                                         frequency=frequency,
                                                         start_datetime=startDate,
                                                         end_datetime=endDate,
                                                         need_extended_hours_data=need_extended_hours_data)

            response.raise_for_status()
            content = json.loads(response.content)
            if content['empty']:
                logging.warning('TDAmeritrade: no Data for ' + str(startDate))
                return None
            return content
        except HTTPError as http_err:
            logging.warning(f'HTTP error occurred: {http_err}')
            return None

    def tdameritrade_get_price_history(self, symbol='AAPL', periodType='day', period=10, frequencyType='minute',
                                       frequency=1,
                                       startDate=None, endDate=None, extended_hours=False):
        """
        https://developer.tdameritrade.com/price-history/apis/get/marketdata/%7Bsymbol%7D/pricehistory

        :param symbol: symbol ticker
        :param periodType: The type of period to show.
        :param period: The number of periods to show.
        :param frequencyType: The type of frequency with which a new candle is formed.
        :param frequency: The number of the frequencyType to be included in each candle.
        :param startDate : Start date as milliseconds since epoch. Only startDate or period.
        :param endDate: End date as milliseconds since epoch. Only endDate or period.
        :param extended_hours: true to return extended hours data, false for regular market hours only. Default is true


        :return: list of candles with OHCL, volume and time as epoch
            Example response
            {
              "candles": [
                {
                  "close": 0,
                  "datetime": 0,
                  "high": 0,
                  "low": 0,
                  "open": 0,
                  "volume": 0
                }
              ],
              "empty": false,
              "symbol": "string"
            }
        """

        endpoint = 'https://api.tdameritrade.com/v1/marketdata/{symbol}/pricehistory'.format(symbol=symbol)

        params = {
            'apikey': self.tda_apikey,
            'periodType': periodType,
            'period': period,
            'frequencyType': frequencyType,
            'frequency': frequency,
            'startDate': startDate,
            'endDate': endDate,
            'needExtendedHoursData': extended_hours
        }

        try:
            response = requests.get(url=endpoint, params=params)
            response.raise_for_status()
            content = json.loads(response.content)

            if content['empty']:
                logging.warning('TDAmeritrade: no Data for ' + str(startDate))

            # add time related data to response
            for element in content['candles']:
                seconds_since_epoch = element['datetime'] / 1000  # milliseconds to seconds

                # add time related info based on market time (New York)
                ts = datetime.fromtimestamp(seconds_since_epoch, pytz.timezone('US/Eastern'))
                timestamp = ts.strftime('%Y-%m-%d %H:%M:%S')
                element['timestamp'] = timestamp
                day = ts.strftime('%Y-%m-%d')
                element['day'] = day
                time = ts.strftime('%H:%M:%S')
                element['time'] = time

                # add time related info based on local time (Zurich)
                ts_zurich = datetime.fromtimestamp(seconds_since_epoch, pytz.timezone('Europe/Zurich'))
                timestamp_zurich = ts_zurich.strftime('%Y-%m-%d %H:%M:%S')
                element['timestamp_zurich'] = timestamp_zurich
                day_zurich = ts_zurich.strftime('%Y-%m-%d')
                element['day_zurich'] = day_zurich
                time_zurich = ts_zurich.strftime('%H:%M:%S')
                element['time_zurich'] = time_zurich

            return content
        except HTTPError as http_err:
            if response.status_code == 400:
                print('Combination of periodType, period, frequencyType, frequency not supported')
            else:
                print(f'HTTP error occurred: {http_err}')
