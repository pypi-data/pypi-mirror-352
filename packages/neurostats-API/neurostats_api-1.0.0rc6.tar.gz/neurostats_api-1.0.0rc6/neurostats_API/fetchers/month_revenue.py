from .base import StatsFetcher, StatsDateTime
import json
import pandas as pd
from ..utils import StatsDateTime, StatsProcessor, YoY_Calculator
import importlib.resources as pkg_resources
import yaml
import traceback
import logging


class MonthRevenueFetcher(StatsFetcher):
    """
        iFa.ai: 財務分析 -> 每月營收
    """

    def __init__(self, ticker, db_client, logger = None):
        super().__init__(ticker, db_client)
        self.logger = logger or logging.getLogger(__name__)

    def _prepare_query(self, target_year, target_month):
        pipeline = super().prepare_query()

        pipeline.append(
            {
                "$project": {
                    "_id": 0,
                    "ticker": 1,
                    "company_name": 1,
                    "monthly_data": {
                        "$sortArray": {
                            "input": "$monthly_data",
                            "sortBy": {
                                "year": -1,
                                "month": -1
                            }
                        }
                    },
                }
            }
        )

        return pipeline

    def collect_data(self, target_year, target_month):
        pipeline = self._prepare_query(target_year, target_month)
        fetched_data = self.collection.aggregate(pipeline)
        fetched_data = fetched_data.to_list()

        return fetched_data

    def query_data(self):
        target_year, target_month = self._get_target_year_and_month()

        # Query data
        fetched_data = self.collect_data(target_year, target_month)

        try:
            return self._process_data(fetched_data[-1])
        except Exception:
            recent_date = []
            for _ in range(12):
                recent_date.append(f"{target_year}/{target_month}")
                target_year, target_month = (
                    target_year - 1, 12
                ) if target_month == 1 else (target_year, target_month - 1)

            # logging.warning(f"{self.ticker}: No monthly revenue data in TWSE mongoDB", exc_info=True)
            return self._get_empty_structure(target_year, target_month)

    def _process_data(self, fetched_data):

        monthly_data = fetched_data.get('monthly_data', [])
        if not monthly_data:
            raise ValueError("monthly_data is empty or missing")

        for data in monthly_data:
            for key, value in data.items():
                if "YoY" in key:
                    data[key] = StatsProcessor.cal_percentage(value)
                elif "ratio" in key or "percentage" in key:
                    data[key] = StatsProcessor.cal_non_percentage(value, to_str=True, postfix="%")
                elif key not in ('year', 'month'):
                    data[key] = StatsProcessor.cal_non_percentage(value, postfix="千元")

        monthly_df = pd.DataFrame(monthly_data)
        target_month = monthly_data[0]['month']
        target_month_df = monthly_df[monthly_df['month'] == target_month]
        annual_month_df = monthly_df[monthly_df['month'] == 12]

        
        month_revenue_df = monthly_df.pivot(
            index='month', columns='year', values='revenue'
        )
        month_revenue_df = month_revenue_df.sort_index(ascending=False)

        grand_total_df = target_month_df.pivot(
            index='month', columns='year', values='grand_total'
        )
        grand_total_df.rename(
            index={target_month: f"grand_total"}, inplace=True
        )
        month_revenue_df = pd.concat([grand_total_df, month_revenue_df], axis=0)

        annual_total_df = annual_month_df.pivot(
            index='month', columns='year', values='grand_total'
        )

        fetched_data.update(
            {
                "month_revenue": month_revenue_df[sorted(month_revenue_df.columns, reverse=True)],
                "this_month_revenue_over_years": target_month_df.set_index("year")[[
                    "revenue", "revenue_increment_ratio", "YoY_1", "YoY_3", "YoY_5", "YoY_10"
                ]].T,
                "grand_total_over_years": target_month_df.set_index("year")[[
                    "grand_total", "grand_total_increment_ratio", "grand_total_YoY_1", "grand_total_YoY_3", "grand_total_YoY_5", "grand_total_YoY_10"
                ]].T,
                "recent_month_revenue": self._get_recent_growth(monthly_data, grand_total_dict=annual_total_df.to_dict(), interval=12)
            }
        )

        fetched_data.pop("monthly_data")
        return fetched_data

    def _get_recent_growth(self, monthly_data, grand_total_dict, interval=12):
        last_month_data = monthly_data[1:interval + 1] + [{}] * max(0, interval - len(monthly_data) + 1)

        MoMs = [
            YoY_Calculator.cal_growth(this.get('revenue'), last.get('revenue'), delta = 1)
            for this, last in zip(monthly_data[:interval], last_month_data[:interval])
        ]

        def safe_accum_yoy(data):
            try:
                year = data['year'] - 1
                total = grand_total_dict[year][12]
                grand_total = data.get('grand_total')
                return f"{round(((grand_total - total) / total) * 100, 2)}%"
            except Exception:
                self.logger.debug(f"accum_YoY calc failed for year={data.get('year')} / ticker={self.ticker}", exc_info=True)
                return None

        recent_month_data = {
            "date": [f"{d.get('year', 0)}/{d.get('month', 0)}" for d in monthly_data[:interval]],
            "revenue": [d.get('revenue') for d in monthly_data[:interval]],
            "MoM": [f"{(m * 100):.2f}%" if isinstance(m, float) else None for m in MoMs],
            "YoY": [d.get('revenue_increment_ratio') for d in monthly_data[:interval]],
            "total_YoY": [d.get('grand_total_increment_ratio') for d in monthly_data[:interval]],
            # accum_YoY
            # accum_YoY 為 Davis提出的定義
            # 2024/6的累計YoY(accum_YoY) 為 2024累計到6月為止的總營收/2023年度總營收
            "accum_YoY": [safe_accum_yoy(d) for d in monthly_data[:interval]]
        }

        df = pd.DataFrame(recent_month_data)
        return df[df['date'] != "0/0"].set_index('date').T


    def _get_empty_structure(self, target_year, target_month):
        """
        Exception 發生時回傳
        """
        recent_date = [f"{target_year}/{target_month}"]
        for _ in range(11):
            target_year, target_month = (target_year - 1, 12) if target_month == 1 else (target_year, target_month - 1)
            recent_date.append(f"{target_year}/{target_month}")

        def empty_df(index, columns):
            return pd.DataFrame(index=index, columns=columns)

        return {
            "month_revenue": empty_df(
                index=pd.Index(['grand_total', 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1], dtype='object', name='month'),
                columns=pd.Index([f"{target_year - i}" for i in range(10)], dtype=object, name='year')
            ),
            "this_month_revenue_over_years": empty_df(
                index=pd.Index(['revenue', 'revenue_increment_ratio', 'YoY_1', 'YoY_3', 'YoY_5', 'YoY_10'], dtype='object'),
                columns=pd.Index([f"{target_year - i}" for i in range(10)], dtype='int64', name='year')
            ),
            "grand_total_over_years": empty_df(
                index=pd.Index(['grand_total', 'grand_total_increment_ratio', 'grand_total_YoY_1', 'grand_total_YoY_3', 'grand_total_YoY_5', 'grand_total_YoY_10'], dtype='object'),
                columns=pd.Index([f"{target_year - i}" for i in range(10)], dtype='int64', name='year')
            ),
            "recent_month_revenue": empty_df(
                index=pd.Index(['revenue', 'MoM', 'YoY', 'total_YoY', 'accum_YoY'], dtype='object'),
                columns=pd.Index([], dtype = 'object', name = 'date')
            )
        }
    
    def _get_target_year_and_month(self):
        try:
            latest_time = StatsDateTime.get_latest_time(self.ticker, self.collection)['last_update_time']
            return latest_time['monthly_data']['latest_year'], latest_time['monthly_data']['latest_month']
        except Exception:
            today = StatsDateTime.get_today()
            return today.year, today.month