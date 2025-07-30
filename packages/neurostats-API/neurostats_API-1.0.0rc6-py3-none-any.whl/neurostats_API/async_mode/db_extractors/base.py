import abc
from datetime import datetime
from ..db import TWSEDBClient, USDBClient
import json
import pytz
from neurostats_API.utils import StatsDateTime, StatsProcessor, YoY_Calculator, NoCompanyError

class BaseDBExtractor(abc.ABC):
    def __init__(self, ticker, client):
        self.ticker = ticker
        self.client = client
        self.timezone = pytz.timezone("Asia/Taipei")
        self.tw_company_list = StatsProcessor.load_json("company_list/tw.json")
        self.us_company_list = StatsProcessor.load_json("company_list/us.json")

        self.company_name, self.zone = self._set_company_name(self.ticker)

        self.db_client = self._set_db_connection()

    def _set_company_name(self, ticker):
        company_lists = [
            (self.tw_company_list, 'tw'),
            (self.us_company_list, 'us')
        ]

        for company_list, zone in company_lists:
            company_name = company_list.get(ticker, None)
            if (company_name):
                return company_name, zone
        # 沒找到公司名稱
        raise NoCompanyError(f"Ticker-{ticker} not found in any company lists")
    
    def _set_db_connection(self):
        db_map = {
            'tw': TWSEDBClient,
            'us': USDBClient
        }
        db_client = db_map.get(self.zone, TWSEDBClient)
        return db_client(self.client)


    
    async def query_data(self):
        """
        user使用的接口
        """
        return NotImplementedError()

    @abc.abstractmethod
    def _prepare_query(self):
        pass
    
    def get_company_name(self):
        """
        回傳公司
        """
        return self.company_name
    
    def get_zone(self):
        """
        公司區域(TW, US)
        """
        return self.zone
    
    def _get_today(self):
        return datetime.today()