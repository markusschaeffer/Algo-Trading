import config
import requests
from requests.exceptions import HTTPError
from datetime import date


class Polygon:
    """
    https://polygon.io/docs/#getting-started

    API Rate Limiting:
        1 API Call per Second

    Basic/Free subscription only offers data on a daily basis, i.e. no real-time data

    """

    def __init__(self, token=config.POLYGON_TOKEN, base_url=config.POLYGON_BASE_URL):
        self.polygon_token = token
        self.polygon_base_url = base_url

    def polygon_get_market_status(self, exchange='NASDAQ'):
        """
        Current status of NASDAQ or NYSE
        https://polygon.io/docs/#get_v1_marketstatus_now_anchor

        Args:
            exchange (str): 'NASDAQ' or 'NYSE'

        Returns:
            object (str): string specifying the market status ('open', 'extended-hours', 'closed')
        """
        endpoint = '/v1/marketstatus/now'
        response = requests.get(self.polygon_base_url + endpoint, params={'apiKey': self.polygon_token})
        if response.status_code == 200:
            resp = response.json()
            if exchange == 'NASDAQ':
                return str(resp['exchanges']['nasdaq'])
            if exchange == 'NYSE':
                return str(resp['exchanges']['nyse'])
        else:
            return None

    def polygon_get_us_stocks_candles_for_date(self, _date=date.today().strftime('%Y-%m-%d')):
        """
        https://polygon.io/docs/#get_v2_aggs_grouped_locale__locale__market__market___date__anchor

        Returns:
            response (dict): see url
        """
        endpoint = '/v2/aggs/grouped/locale/US/market/STOCKS/' + _date
        response = requests.get(self.polygon_base_url + endpoint, params={'apiKey': self.polygon_token})
        return response.json()

    def polygon_market_holiday(self, exchange='NASDAQ'):
        """
        Checks if today is a market holiday
        https://polygon.io/docs/#get_v1_marketstatus_upcoming_anchor

        Args:
            exchange (str): 'NASDAQ' or 'NYSE'

        Returns:
            object (bool):
                True if today is a market holiday
                False if today is not a market holiday
        """
        endpoint = '/v1/marketstatus/upcoming'
        response = requests.get(self.polygon_base_url + endpoint, params={'apiKey': self.polygon_token})
        if response.status_code == 200:
            resp = response.json()
            holidays = []
            for element in resp:
                if 'exchange' in element and 'date' in element:
                    if element['exchange'] == exchange:
                        holidays.append(str(element['date']))
            if date.today().strftime('%Y-%m-%d') in holidays:
                return True
            else:
                return False
        else:
            return False
