from  ..base import BaseTransformer
import pandas as pd

class BaseBalanceSheetTransformer(BaseTransformer):
    def __init__(self, ticker, company_name, zone):
        super().__init__(ticker, company_name, zone)

    def _process_twse_to_stats_format(self, fetched_data):
        table_dict = {}
        for data in fetched_data:
            year, season, balance_sheet = data['year'], data['season'], data['balance_sheet']

            time_index = f"{year}Q{season}"
            table_dict[time_index] = balance_sheet

        stats_df = pd.DataFrame(table_dict)

        return stats_df
    
    def _process_twse_to_tej_format(self, fetched_data):
        """
        new_df 迎合 TEJ格式, 用於 report_generator
        """
        table_dict = {}
        for data in fetched_data:
            year, season, balance_sheet = data['year'], data['season'], data['balance_sheet']
            time_index = f"{year}Q{season}"

            new_balance_sheet = self.flatten_dict(
                balance_sheet,
                target_keys=["value", "percentage"]
            )

            table_dict[time_index] = new_balance_sheet
        
        stats_df = pd.DataFrame.from_dict(table_dict)
        return stats_df.T
    
    def _process_us_format(self, fetched_data):
        """
        主要用於report generator
        """
        table_dict = {}
        for data in fetched_data:
            year, season, balance_sheet = data['year'], data['season'], data['balance_sheet']
            time_index = f"{year}Q{season}"

            table_dict[time_index] = balance_sheet
        
        stats_df = pd.DataFrame.from_dict(table_dict)
        return stats_df.T
