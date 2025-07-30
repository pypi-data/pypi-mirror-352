from  ..base import BaseTransformer
import pandas as pd

class BaseProfitLoseTransformer(BaseTransformer):
    def __init__(self, ticker, company_name, zone):
        super().__init__(ticker, company_name, zone)

    def _process_twse_to_stats_format(self, fetched_data):
        table_dict = {}
        for data in fetched_data:
            year, season, profit_lose = data['year'], data['season'], data['profit_lose']

            time_index = f"{year}Q{season}"
            table_dict[time_index] = profit_lose

        stats_df = pd.DataFrame(table_dict)

        return stats_df
    
    def _process_twse_to_tej_format(self, fetched_data):
        """
        new_df 迎合 TEJ格式, 用於 report_generator
        """
        if (isinstance(fetched_data, list)):
            table_dict = {}
            for data in fetched_data:
                year, season, profit_lose = data['year'], data['season'], data['profit_lose']
                time_index = f"{year}Q{season}"

                new_profit_lose = self.flatten_dict(
                    profit_lose,
                    target_keys=[
                        "value", "growth", 
                        "percentage", "grand_total_percentage"
                    ] + [f"YoY_{i}" for i in [1, 3, 5, 10]]
                    + [f"grand_total_YoY_{i}" for i in [1, 3, 5, 10]]
                )

                table_dict[time_index] = new_profit_lose
            
            stats_df = pd.DataFrame.from_dict(table_dict)
            return stats_df.T
        
        elif (isinstance(fetched_data, dict)):
            for time_index, profit_lose in fetched_data.items():
                fetched_data[time_index] = self.flatten_dict(
                    value_dict=profit_lose,
                    target_keys=[
                        "value", "growth", "percentage", "grand_total",
                        "grand_total_percentage"
                    ] + [f"YoY_{i}" for i in [1, 3, 5, 10]] +
                    [f"grand_total_YoY_{i}" for i in [1, 3, 5, 10]]
                )

            stats_df = pd.DataFrame.from_dict(fetched_data)
            return stats_df.T
        
    def _process_us_format(self, fetched_data):
        """
        主要用於report generator
        """
        if (isinstance(fetched_data, list)):
            table_dict = {}
            for data in fetched_data:
                year, season, income_statement = data['year'], data['season'], data['income_statement']
                time_index = f"{year}Q{season}"

                table_dict[time_index] = income_statement
            
            stats_df = pd.DataFrame.from_dict(table_dict)
            return stats_df.T

        elif (isinstance(fetched_data, dict)):
            for time_index, income_statement in fetched_data.items():
                fetched_data[time_index] = self.flatten_dict(
                    value_dict=income_statement,
                    target_keys=["value", "growth"] +
                    [f"YoY_{i}" for i in [1, 3, 5, 10]]
                )
            stats_df = pd.DataFrame.from_dict(fetched_data)
            return stats_df.T

