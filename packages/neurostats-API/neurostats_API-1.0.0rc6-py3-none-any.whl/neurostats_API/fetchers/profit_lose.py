from .base import StatsFetcher, StatsDateTime
import importlib.resources as pkg_resources
import json
import numpy as np
import pandas as pd
from ..utils import StatsDateTime, StatsProcessor, YoY_Calculator
import yaml


class ProfitLoseFetcher(StatsFetcher):
    """
    iFa.ai: 財務分析 -> 損益表
    """

    def __init__(self, ticker, db_client):
        super().__init__(ticker, db_client)

        self.table_settings = StatsProcessor.load_yaml("twse/profit_lose.yaml")

        self.process_function_map = {
            "twse_stats": self.process_data_twse,
            "us_stats": self.process_data_us
        }

        self.return_keys = [
            'profit_lose', 'grand_total_profit_lose', 'revenue', 'grand_total_revenue', 
            'gross_profit', 'grand_total_gross_profit', 'gross_profit_percentage', 
            'grand_total_gross_profit_percentage', 'operating_income', 'grand_total_operating_income', 'operating_income_percentage', 
            'grand_total_operating_income_percentage', 'net_income_before_tax', 'grand_total_net_income_before_tax', 'net_income_before_tax_percentage', 
            'grand_total_net_income_before_tax_percentage', 'net_income', 'grand_total_net_income', 'net_income_percentage', 
            'grand_total_income_percentage', 'EPS', 'EPS_growth', 'grand_total_EPS', 
            'grand_total_EPS_growth', 'profit_lose_all', 'profit_lose_YoY'
        ]

    def prepare_query(self):
        pipeline = super().prepare_query()

        name_map = {"twse_stats": "profit_lose", "us_stats": "income_statement"}

        chart_name = name_map.get(self.collection_name, "income_statement")

        append_pipeline = [
        {
            "$project": {
                "_id": 0,
                "ticker": 1,
                "company_name": 1,
                "seasonal_data": {
                    "$map": {
                        "input": {"$ifNull": ["$seasonal_data", []]},
                        "as": "season",
                        "in": {
                            "year": "$$season.year",
                            "season": "$$season.season",
                            "data": {"$ifNull": [f"$$season.{chart_name}", []]}
                        }
                    }
                }
            }
        }
    ]

        pipeline = pipeline + append_pipeline

        return pipeline

    def collect_data(self):
        return super().collect_data()

    def query_data(self):
        fetched_data = self.collect_data()

        fetched_data = fetched_data[0]

        process_fn = self.process_function_map.get(
            self.collection_name, self.process_data_us
        )
        return process_fn(fetched_data)

    def process_data_twse(self, fetched_data):

        latest_time = StatsDateTime.get_latest_time(
            self.ticker, self.collection
        ).get('last_update_time', {})

        # 取最新時間資料時間，沒取到就預設去年年底
        target_year = latest_time.get('seasonal_data', {}).get(
            'latest_target_year',
            StatsDateTime.get_today().year - 1
        )
        target_season = latest_time.get('seasonal_data',
                                        {}).get('latest_season', 4)

        return_dict = {
            "ticker": self.ticker,
            "company_name": fetched_data['company_name'],
        }

        seasonal_data = fetched_data.get('seasonal_data', [])

        if (not seasonal_data):
            return_dict.update(self._get_empty_structure())
            return return_dict

        profit_lose_dict = {
            f"{data['year']}Q{data['season']}": data['data']
            for data in seasonal_data
        }

        profit_lose_dict = YoY_Calculator.cal_QoQ(profit_lose_dict)
        profit_lose_df = pd.DataFrame.from_dict(profit_lose_dict)
        target_season_col = profit_lose_df.columns.str.endswith(
            f"Q{target_season}"
        )
        profit_lose_df = profit_lose_df.loc[:, target_season_col]

        old_profit_lose_df = StatsProcessor.expand_value_percentage(
            profit_lose_df
        )
        # OLD: 回傳包含value & percentage
        value_col = old_profit_lose_df.columns.str.endswith(f"_value")
        percentage_col = old_profit_lose_df.columns.str.endswith(f"_percentage")
        # OLD: 回傳剔除grand_total
        grand_total_value_col = old_profit_lose_df.columns.str.endswith(
            f"grand_total_value"
        )
        grand_total_percentage_col = old_profit_lose_df.columns.str.endswith(
            f"grand_total_percentage"
        )

        old_profit_lose_df = old_profit_lose_df.loc[:, (
            (value_col & ~grand_total_value_col) |
            (percentage_col & ~grand_total_percentage_col)
        )]

        for time_index, data_dict in profit_lose_dict.items():
            profit_lose_dict[time_index] = self.flatten_dict(
                value_dict=data_dict,
                indexes=list(data_dict.keys()),
                target_keys=[
                    "value", "growth", "percentage", "grand_total",
                    "grand_total_percentage"
                ] + [f"YoY_{i}" for i in [1, 3, 5, 10]] +
                [f"grand_total_YoY_{i}" for i in [1, 3, 5, 10]]
            )

        profit_lose_df = pd.DataFrame.from_dict(profit_lose_dict).T
        # EPS的value用元計算
        eps_index = (
            profit_lose_df.columns.str.endswith("_value")
            & profit_lose_df.columns.str.contains("每股盈餘")
        )
        eps_copy = profit_lose_df.loc[:, eps_index].copy()
        eps_mask_index = eps_copy.columns
        profit_lose_df[eps_mask_index] = profit_lose_df[eps_mask_index].map(
            lambda x: StatsProcessor.cal_non_percentage(x, postfix="元")
        )

        # percentage處理
        percentage_index = profit_lose_df.columns.str.endswith("percentage")
        growth_index = profit_lose_df.columns.str.endswith("growth")
        percentage_mask = (percentage_index | growth_index)
        percentage_copy = profit_lose_df.loc[:, percentage_mask]
        percentage_mask_index = percentage_copy.columns

        profit_lose_df[percentage_mask_index] = profit_lose_df[
            percentage_mask_index].map(
                lambda x: StatsProcessor.
                cal_non_percentage(x, to_str=True, postfix="%")
            )

        # YoY處理: 乘以100
        YoY_index = profit_lose_df.columns.str.contains("YoY")
        YoY_mask = YoY_index
        YoY_copy = profit_lose_df.loc[:, YoY_mask]
        YoY_mask_cols = YoY_copy.columns

        profit_lose_df[YoY_mask_cols] = profit_lose_df[YoY_mask_cols].map(
            lambda x: StatsProcessor.cal_percentage(x)
        )

        # 剩下的處理: 乘以千元
        value_index = ~(
            percentage_index | growth_index | YoY_index | eps_index
        )    # 除了上述以外的 index

        value_col = profit_lose_df.loc[:, value_index].columns
        profit_lose_df[value_col] = profit_lose_df[value_col].map(
            lambda x: StatsProcessor.cal_non_percentage(x, postfix="千元")
        )

        total_table = profit_lose_df.replace("N/A", None).T

        # 取特定季度
        target_season_columns = total_table.columns.str.endswith(
            f"Q{target_season}"
        )
        total_table_YoY = total_table.loc[:, target_season_columns]

        for name, setting in self.table_settings.items():
            target_indexes = setting.get('target_index', [None])
            for target_index in target_indexes:
                try:
                    return_dict[name] = StatsProcessor.slice_table(
                        total_table=total_table_YoY,
                        mode=setting['mode'],
                        target_index=target_index
                    )
                    break
                except Exception as e:
                    continue

        return_dict.update(
            {
                "profit_lose": old_profit_lose_df,
                "profit_lose_all": total_table.copy(),
                "profit_lose_YoY": total_table_YoY
            }
        )
        return return_dict

    def process_data_us(self, fetched_data):

        table_dict = {
            f"{data['year']}Q{data['season']}": data['data']
            for data in fetched_data['seasonal_data']
        }

        table_dict = YoY_Calculator.cal_QoQ(table_dict)
        table_dict = YoY_Calculator.cal_YoY(table_dict)

        for time_index, data_dict in table_dict.items():
            table_dict[time_index] = self.flatten_dict(
                value_dict=data_dict,
                indexes=list(data_dict.keys()),
                target_keys=["value", "growth"] +
                [f"YoY_{i}" for i in [1, 3, 5, 10]]
            )

        # 計算QoQ

        return_dict = {
            "ticker": self.ticker,
            "company_name": fetched_data['company_name'],
            "profit_lose": pd.DataFrame.from_dict(table_dict)
        }

        return return_dict

    def _get_empty_structure(self):
        return {
            key: pd.DataFrame(columns= pd.Index([], name = 'date')) for key in self.return_keys
        }