from .base import BaseProfitLoseTransformer
from neurostats_API.utils import StatsProcessor, YoY_Calculator
import pandas as pd

class USProfitLoseTransformer(BaseProfitLoseTransformer):
    def __init__(self, ticker, company_name, zone):
        super().__init__(ticker, company_name, zone)
        self.data_df = None
        self.return_keys = ['profit_lose']
    
    def process_transform(self, fetched_data):
        
        data_dict = self._process_us_format(fetched_data).T.to_dict()

        data_dict = YoY_Calculator.cal_QoQ(data_dict)
        data_dict = YoY_Calculator.cal_YoY(data_dict)

        self.data_df = self._process_us_format(data_dict)

        return_dict = {
            "ticker": self.ticker,
            "company_name": self.company_name,
            "profit_lose": self.data_df
        }

        return return_dict
