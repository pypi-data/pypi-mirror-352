from .base import StatsFetcher, StatsDateTime
import json
import numpy as np
import pandas as pd
from ..utils import StatsDateTime, StatsProcessor
import importlib.resources as pkg_resources
import yaml

class CashFlowFetcher(StatsFetcher):
    def __init__(self, ticker, db_client):
        super().__init__(ticker, db_client)

        self.cash_flow_dict = StatsProcessor.load_yaml(
            "twse/cash_flow_percentage.yaml"
        )  # 計算子表格用

        self.process_function_map = {
            "twse_stats": self.process_data_twse,
            "us_stats": self.process_data_us
        }

        self.return_keys = ['cash_flow', 'CASHO', 'CASHI', 'CASHF', 'cash_flow_all', 'cash_flow_YoY']
    
    def prepare_query(self):
        pipeline = super().prepare_query()

        name_map = {
            "twse_stats": "cash_flow",
            "us_stats": "cash_flow"
        }


        chart_name = name_map.get(self.collection_name, "cash_flow")

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

        process_fn = self.process_function_map.get(self.collection_name, self.process_data_us)
        return process_fn(fetched_data)
    
    def process_data_twse(self, fetched_data):
        """
        處理現金流量表頁面的所有表格
        金流表本身沒有比例 但是Ifa有算，
        項目所屬的情況也不一(分別所屬營業,投資,籌資三個活動)
        所以這裡選擇不用slicing處理
        """

        index_names = []
        column_names = []

        table_dict = {}
        CASHO_dict = {}
        CASHI_dict = {}
        CASHF_dict = {}

        # 處理cash_flow 比例
        checkpoints = ["營業活動之現金流量－間接法", "投資活動之現金流量", "籌資活動之現金流量", "匯率變動對現金及約當現金之影響"]
        main_cash_flows = [
            "營業活動之淨現金流入（流出）", "投資活動之淨現金流入（流出）", "籌資活動之淨現金流入（流出）", "其他"
        ] # 主要的比例對象
        partial_cash_flows = [CASHO_dict, CASHI_dict, CASHF_dict, dict()] 

        # 作法: dictionary中也有checkpoints，如果出現了就換下一個index去計算

        return_dict = {
            "ticker": self.ticker,
            "company_name": fetched_data['company_name']
        }
        seasonal_data = fetched_data.get('seasonal_data')
        if not seasonal_data:
            return_dict.update(self._get_empty_structure())
            return return_dict

        for data in seasonal_data:
            year, season, cash_flow = data['year'], data['season'], data['data']

            time_index = f"{year}Q{season}"

            main_cash_flow_name = ""
            partial_cash_flow = {}
            next_checkpoint = 0

            temp_dict = {}

            for index_name, cash_flow_value in cash_flow.items():
                if (next_checkpoint < 3
                        and index_name == checkpoints[next_checkpoint]): # 找到了主要的變動點
                    main_cash_flow_name = main_cash_flows[next_checkpoint]
                    partial_cash_flow = partial_cash_flows[next_checkpoint]
                    partial_cash_flow[time_index] = {}
                    next_checkpoint += 1

                if main_cash_flow_name: # 有取得cash flow name再進行接下來的計算percentage
                    if (isinstance(cash_flow_value, dict)):
                        value = cash_flow_value.get('value', None) 
                    else:
                        value = cash_flow_value
                    
                    # 處理cashflow percentage部分(取2位 + 接%)
                    main_value = cash_flow.get(main_cash_flow_name, None)
                    if (isinstance(main_value, dict)):
                        main_value = main_value.get('value', None)
                    else:
                        pass

                    try:
                        ratio = np.round(
                            (value / main_value) * 100, 2
                        )
                        ratio = f"{ratio}%"
                    except:
                        ratio = None
                    
                    value = StatsProcessor.cal_non_percentage(value, postfix="千元")
                    temp_dict[index_name] = {
                        "value" : value,
                        "percentage": ratio
                    }
                    partial_cash_flow[time_index][index_name] = temp_dict[index_name]

            table_dict[time_index] = temp_dict
            index_names += list(cash_flow.keys())

        # 轉成dictionary keys
        index_names = list(dict.fromkeys(index_names))

        cash_flow_table = pd.DataFrame(table_dict)
        cash_flow_table_stats = StatsProcessor.expand_value_percentage(cash_flow_table)

        CASHO_table = pd.DataFrame(CASHO_dict)
        CASHO_table = StatsProcessor.expand_value_percentage(CASHO_table)

        CASHI_table = pd.DataFrame(CASHI_dict)
        CASHI_table = StatsProcessor.expand_value_percentage(CASHI_table)

        CASHF_table = pd.DataFrame(CASHF_dict)
        CASHF_table = StatsProcessor.expand_value_percentage(CASHF_table)

        # 回傳歷來格式
        target_season = seasonal_data[0]['season']

        cash_flow_flatten, cash_flow_flatten_YoY = self.flatten_twse(
            table_dict, target_season, index_names
        )

        return_dict.update({
            "cash_flow": cash_flow_table_stats,
            "CASHO": CASHO_table,
            "CASHI": CASHI_table,
            "CASHF": CASHF_table,
            "cash_flow_all": cash_flow_flatten,
            "cash_flow_YoY": cash_flow_flatten_YoY
        })
        return return_dict
    
    def flatten_twse(self, data_dict: dict, target_season: int, index_names: list):
        for time_index in data_dict.keys():
            data_dict[time_index] = self.flatten_dict(data_dict[time_index], index_names, target_keys=['value', 'percentage'])
        cash_flow_flatten = pd.DataFrame.from_dict(data_dict)

        target_season_column = cash_flow_flatten.columns.str.endswith(f"Q{target_season}")

        return cash_flow_flatten, cash_flow_flatten.loc[:, target_season_column]

    def process_data_us(self, fetched_data):

        table_dict = {
            f"{data['year']}Q{data['season']}": data['data'] 
            for data in fetched_data['seasonal_data']
        }

        cash_flow_df = pd.DataFrame.from_dict(table_dict)

        latest_season = fetched_data['seasonal_data'][0]['season']
        target_season_columns = cash_flow_df.columns.str.endswith(
            f"Q{latest_season}"
        )
        cash_flow_df_YoY = cash_flow_df.loc[:, target_season_columns]

        return_dict = {
            "ticker": self.ticker,
            "company_name": fetched_data['company_name'],
            "cash_flow": cash_flow_df,
            "cash_flow_YoY": cash_flow_df_YoY
        }
        return return_dict

    def _get_empty_structure(self):
        return {
            key: pd.DataFrame(columns= pd.Index([], name = 'date')) for key in self.return_keys
        }