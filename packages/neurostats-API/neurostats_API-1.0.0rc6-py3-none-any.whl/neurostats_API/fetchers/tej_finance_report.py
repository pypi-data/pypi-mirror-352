from .base import BaseTEJFetcher
from datetime import datetime
from enum import Enum
import numpy as np
import pandas as pd
from pymongo import MongoClient
from .tech import TechProcessor
from ..utils import StatsProcessor, YoY_Calculator
import warnings
import yaml


class FinanceReportFetcher(BaseTEJFetcher):

    class FetchMode(Enum):
        YOY = 1
        QOQ = 2
        YOY_NOCAL = 3
        QOQ_NOCAL = 4

    def __init__(
        self, mongo_uri, db_name="company", collection_name="TWN/AINVFQ1"
    ):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

        index_files = [
            "tej_db/tej_db_index.yaml", "tej_db/tej_db_thousand_index.yaml",
            "tej_db/tej_db_percent_index.yaml"
        ]

        self.index_dict, self.thousand_dict, self.percent_dict = [
            StatsProcessor.load_yaml(file) for file in index_files
        ]

        self.check_index = set(self.index_dict.get(collection_name, []))
        self.skip_index = set(self.percent_dict.get(collection_name, []))
        self.thousand_index_list = list(
            self.thousand_dict.get(collection_name, [])
        )
        self.percent_index_list = list(
            self.percent_dict.get(collection_name, [])
        )

    def get(
        self,
        ticker,
        fetch_mode: FetchMode = FetchMode.QOQ_NOCAL,
        start_date: str = None,
        end_date: str = None,
        report_type: str = "Q",
        indexes: list = []
    ):
        """
        基礎的query function
        ticker(str): 股票代碼
        start_date(str):  開頭日期範圍
        end_date(str):  = 結束日期範圍
        report_type(str): 報告型態 {"A", "Q", "TTM"}  
        fetch_mode(class FetchMode): 
           YoY : 起始日期到結束日期範圍內，特定該季的資料
           QoQ : 起始日期到結束日期內，每季的資料(與上一季成長率)
        indexes(List): 指定的index
        """
        # 確認indexes中是否有錯誤的index，有的話回傳warning
        if indexes and self.check_index:
            invalid_indexes = set(indexes) - self.check_index
            if invalid_indexes:
                warnings.warn(
                    f"{list(invalid_indexes)} 不存在，請確認欄位名稱", UserWarning
                )

        start_date = datetime.strptime(
            start_date, "%Y-%m-%d"
        ) if start_date else datetime(2005, 1, 1)

        if fetch_mode in {self.FetchMode.QOQ, self.FetchMode.QOQ_NOCAL}:
            end_date = datetime.strptime(end_date, "%Y-%m-%d"
                                         ) if end_date else datetime.today()
            assert start_date <= end_date
            start_year, end_year = start_date.year, end_date.year
            return self.get_QoQ_data(
                ticker=ticker,
                start_date=start_date,
                end_date=end_date,
                report_type=report_type,
                indexes=indexes,
                use_cal=(fetch_mode == self.FetchMode.QOQ)
            )

        elif fetch_mode in {self.FetchMode.YOY, self.FetchMode.YOY_NOCAL}:
            end_date = self.get_latest_data_time(ticker) or datetime.today()
            start_year, end_year = start_date.year, end_date.year
            end_season = (end_date.month - 1) // 4 + 1
            return self.get_YoY_data(
                ticker=ticker,
                start_year=start_year,
                end_year=end_year,
                season=end_season,
                report_type=report_type,
                indexes=indexes,
                use_cal=(fetch_mode == self.FetchMode.YOY)
            )

    def get_QoQ_data(
        self,
        ticker,
        start_date,
        end_date,
        report_type="Q",
        indexes=[],
        use_cal=False
    ):
        """
            取得時間範圍內每季資料
        """
        start_year, start_season = start_date.year, (
            start_date.month - 1
        ) // 4 + 1
        end_year, end_season = end_date.year, (end_date.month - 1) // 4 + 1
        lower_bound_year, lower_bound_season = (
            start_year - 1, 4
        ) if start_season == 1 else (start_year, start_season - 1)

        pipeline = self.build_pipeline(
            ticker, start_year, start_season, end_year, end_season,
            lower_bound_year, lower_bound_season, report_type, indexes
        )
        fetched_data = self.collection.aggregate(pipeline).to_list()
        fetched_data = fetched_data[0]
        fetched_data = fetched_data.get('data', []) if isinstance(fetched_data, dict) else []

        data_dict = self.transform_value(
            StatsProcessor.list_of_dict_to_dict(
                data_list=fetched_data,
                keys=["year", "season"],
                delimeter="Q",
                data_key=report_type
            )
        )

        return self.calculate_and_format(data_dict, use_cal, self.cal_QoQ)

    def get_YoY_data(
        self,
        ticker,
        start_year,
        end_year,
        season,
        report_type="Q",
        indexes=[],
        use_cal=False
    ):
        """
        取得某季歷年資料
        """
        select_year = sorted(
            {year
             for year in range(start_year, end_year + 1)} | {
                 y
                 for year in range(start_year, end_year + 1)
                 for y in {year, year - 1, year - 3, year - 5, year - 10}
             }
        ) if use_cal else list(range(start_year, end_year + 1))

        pipeline = self.build_pipeline(
            ticker,
            select_year,
            season,
            None,
            None,
            None,
            None,
            report_type,
            indexes,
            year_based=True
        )
        fetched_data = self.collection.aggregate(pipeline).to_list()
        fetched_data = fetched_data[0]
        fetched_data = fetched_data.get('data', []) if isinstance(fetched_data, dict) else []

        data_dict = self.transform_value(
            StatsProcessor.list_of_dict_to_dict(
                data_list=fetched_data,
                keys=["year", "season"],
                delimeter="Q",
                data_key=report_type
            )
        )

        return self.calculate_and_format(
            data_dict, use_cal,
            lambda x: self.cal_YoY(x, start_year, end_year, season)
        )

    def transform_value(self, data_dict):
        """
        處理千元, %等單位
        """

        data_df = pd.DataFrame.from_dict(data_dict)
        for category, postfix in [(self.thousand_index_list, "千元"),
                                  (self.percent_index_list, "%")]:
            process_list = list(set(data_df.index) & set(category))
            if postfix == "%":
                data_df = data_df.T
                data_df[process_list] = data_df[process_list].map(lambda x: f"{x}%") # if (not np.isnan(x)) else None)
                data_df = data_df.T
            else:
                data_df.loc[process_list] = data_df.loc[process_list].map(
                    lambda x: StatsProcessor.
                    cal_non_percentage(x, postfix=postfix)
                )
        return data_df.to_dict()

    def build_pipeline(
        self,
        ticker,
        start_year,
        start_season,
        end_year,
        end_season,
        lower_bound_year,
        lower_bound_season,
        report_type,
        indexes,
        year_based=False
    ):

        if year_based:
            filter_cond = {
                "$and": [
                    { "$in": ["$$item.year", start_year] },
                    { "$eq": ["$$item.season", start_season] }
                ]
            }
        else:
            filter_cond = {
                "$or": [
                    {
                        "$and": [
                            { "$gt": ["$$item.year", start_year] },
                            { "$lt": ["$$item.year", end_year] }
                        ]
                    },
                    {
                        "$and": [
                            { "$eq": ["$$item.year", start_year] },
                            { "$gte": ["$$item.season", start_season] }
                        ]
                    },
                    {
                        "$and": [
                            { "$eq": ["$$item.year", end_year] },
                            { "$lte": ["$$item.season", end_season] }
                        ]
                    },
                    {
                        "$and": [
                            { "$eq": ["$$item.year", lower_bound_year] },
                            { "$eq": ["$$item.season", lower_bound_season] }
                        ]
                    }
                ]
            }

        # 每個 filtered item 要輸出哪些欄位
        item_fields = {
            "year": "$$item.year",
            "season": "$$item.season"
        }

        if indexes:
            for idx in indexes:
                item_fields[idx] = f"$$item.{report_type}.{idx}"
        else:
            item_fields[report_type] = f"$$item.{report_type}"
        
        return [
            {
                "$match": {
                    "ticker": ticker
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "ticker": 1,
                    "data": {
                        "$map": {
                            "input": {
                                "$filter": {
                                    "input": "$data",
                                    "as": "item",
                                    "cond": filter_cond
                                }
                            },
                            "as": "item",
                            "in": item_fields
                        }
                    }
                }
            }
        ]

    def calculate_and_format(self, data_dict, use_cal, calc_function):
        data_df = pd.DataFrame.from_dict(
            calc_function(data_dict) if use_cal else data_dict
        ).iloc[:, ::-1]
        return data_df if not use_cal else self.get_dict_of_df(
            data_df.T.to_dict()
        )


class TEJStockPriceFetcher(BaseTEJFetcher):

    def __init__(
        self, mongo_uri, db_name: str = "company", collection_name: str = None
    ):
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self.collection_name = collection_name

        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.db_name]
        self.collection = self.db[self.collection_name]

        self.check_period = [
            '1d', '7d', '1m', '3m', '1y', '3y', '5y', '10y', 'all'
        ]

    def get(
        self,
        ticker: str = "2330",
        start_date: str = "2024-10-01",
        period: str = None
    ):
        """
        取得開高低收資料
        start_date: str: 起始的日期
        period: 指定日期範圍(E.g. 1天, 7天...etc)
        如果宣告period, 以period為優先
        """

        assert (
            period is None or period in self.check_period
        ), f"period should be None or {','.join(self.check_period)}"

        if (period is not None):
            latest_date = self.get_latest_data_time(ticker)
            if (latest_date):
                start_date = self.set_time_shift(date=latest_date, period=period)
            else:
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
        else:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")

        pipeline = [
            {
                "$match": {
                    "ticker": ticker
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "ticker": 1,
                    "data": {
                        "$filter": {
                            "input": "$data",
                            "as": "item",
                            "cond": {
                                "$gte": ["$$item.mdate", start_date]
                            }
                        }
                    }
                }
            }
        ]
        datas = self.collection.aggregate(pipeline).to_list()
        datas = datas[0]
        datas = datas.get('data', [])
        elements = [element for element in datas]
        try:
            data_df = pd.DataFrame(elements).set_index('mdate')
        except:
            column_names = [
                "coid", "mdate", "mkt", "open_d", "high_d", "low_d", "close_d",
                "adjfac", "vol", "amt", "trn", "bid", "offer", "avgprc", "roi",
                "hmlpct", "turnover", "shares", "mktcap", "mktcap_pct",
                "amt_pct", "per", "pbr", "div_yid", "cdiv_yid"
            ]
            data_df = pd.DataFrame(columns = column_names)

        return data_df
