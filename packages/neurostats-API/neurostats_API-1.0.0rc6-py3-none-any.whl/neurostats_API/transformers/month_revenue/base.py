import abc
from  ..base import BaseTransformer
from neurostats_API.utils import StatsProcessor
import pandas as pd

class BaseMonthRevenueTransformer(BaseTransformer):
    def __init__(self, ticker, company_name, zone):
        self.ticker = ticker
        self.company_name = company_name,
        self.zone = zone

        self.return_keys = []
    
    @abc.abstractmethod
    def process_transform(self):
        pass

    @staticmethod
    def _process_unit(data_df, postfix):

        lambda_map = {
            "revenue":  lambda x: StatsProcessor.cal_non_percentage(x, postfix="千元"),
            "increment": lambda x : StatsProcessor.cal_non_percentage(x, postfix="千元"),
            "ratio": lambda x : StatsProcessor.cal_non_percentage(x, to_str=True, postfix="%"),
            'percentage': lambda x : StatsProcessor.cal_non_percentage(x, to_str=True, postfix="%"),
            "YoY_1": StatsProcessor.cal_percentage,
            "YoY_3": StatsProcessor.cal_percentage,
            "YoY_5": StatsProcessor.cal_percentage,
            "YoY_10": StatsProcessor.cal_percentage
        }

        process_fn = lambda_map.get(postfix)
        postfix_cols = data_df.columns.str.endswith(postfix)
        postfix_cols = data_df.loc[:, postfix_cols].columns

        data_df[postfix_cols] = (
            data_df[postfix_cols].map(
               process_fn
            )
        )

        return data_df
    
    def _apply_process_unit_pipeline(
        self,
        data_df,
        postfix_list = ['revenue', 'increment']
    ):
        return super()._apply_process_unit_pipeline(
            data_df,
            postfix_list
        )

    def _process_data(self, fetched_data):
        for data in fetched_data:
            data.pop("ticker")
            data.pop("company_name")
            data.pop("memo")
        
        return pd.DataFrame(fetched_data)