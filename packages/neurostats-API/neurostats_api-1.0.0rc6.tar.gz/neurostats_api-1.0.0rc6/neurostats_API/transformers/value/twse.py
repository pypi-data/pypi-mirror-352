from .base import BaseValueTransformer
import pandas as pd

class TWSEValueTransformer(BaseValueTransformer):
    def __init__(self, ticker, company_name, zone):
        super().__init__(ticker, company_name, zone)
    
    def process_transform(self, fetched_data):
        pass

class TWSEAnnualValueTransformer(TWSEValueTransformer):
    def __init__(self, ticker, company_name, zone):
        super().__init__(ticker, company_name, zone)
    
    def process_transform(self, annual_data):
        annual_df = pd.DataFrame(annual_data)

        return annual_df

class TWSEHistoryValueTransformer(TWSEValueTransformer):
    def __init__(self, ticker, company_name, zone):
        super().__init__(ticker, company_name, zone)
        self.column = [
            "P_E", "P_FCF", "P_B", "P_S",
            "EV_OPI", "EV_EBIT", "EV_EBITDA", "EV_S", "close"
        ]
    
    def process_transform(self, daily_data):
        history_df = pd.DataFrame(daily_data).set_index("date")
        return_dict = {}

        for key in self.column:
            return_dict[key] = history_df.loc[:, [key]]
        
        return return_dict
    
    def process_latest(self, daily_data):
        if (not daily_data):
            return self._get_empty_structure()

        daily_data = daily_data[-1]

        return daily_data
    
    def _get_empty_structure(self):
        return {
            key: None for key in self.column
        }