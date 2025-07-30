from .base import BaseCashFlowTransformer
from neurostats_API.utils import StatsProcessor, YoY_Calculator
import pandas as pd

class USCashFlowTransformer(BaseCashFlowTransformer):
    def __init__(self, ticker, company_name, zone):
        super().__init__(ticker, company_name, zone)
        self.data_df = None
        self.return_keys = ['cash_flow', 'cash_flow_YoY']
    def process_transform(self, fetched_data):
        if (not fetched_data):
            return self._get_empty_structure()

        self.data_df = self._process_us_format(fetched_data)
        target_season = fetched_data[0]['season']

        return_dict = {
            "ticker": self.ticker,
            "company_name": self.company_name,
            "cash_flow": self.data_df,
            "cash_flow_YoY": self._slice_target_season(self.data_df, target_season)
        }

        return return_dict
    
    def process_QoQ(self, fetched_data):
        if (not fetched_data):
            return self._get_empty_structure()
        
        data_df = self._process_twse_to_tej_format(fetched_data)
        target_season = fetched_data[0]['season']

        data_df_YoY = self._slice_target_season(data_df, target_season)

        return {
            "cash_flow_all": data_df,
            "cash_flow_YoY": data_df_YoY
        }