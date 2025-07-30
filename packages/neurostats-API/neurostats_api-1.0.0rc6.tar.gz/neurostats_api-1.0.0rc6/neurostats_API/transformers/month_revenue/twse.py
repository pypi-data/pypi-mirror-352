from .base import BaseMonthRevenueTransformer
from datetime import datetime
from neurostats_API.utils import StatsProcessor, YoY_Calculator
import pandas as pd

class TWSEMonthlyRevenueTransformer(BaseMonthRevenueTransformer):
    def __init__(self, ticker, company_name, zone):
        super().__init__(ticker, company_name, zone)

        self.data_df = None
    def process_transform(self, fetched_data):
        if (not fetched_data):
            return self._get_empty_structure()
        self.data_df = self._process_data(fetched_data)
        target_month = fetched_data[0]['month']

        self._apply_process_unit_pipeline(
            self.data_df,
            postfix_list = [
                'YoY_1',
                'YoY_3',
                "YoY_5",
                "YoY_10",
                "ratio",
                "percentage",
                "increment",
                "revenue"
            ]
        )

        target_month_df = self.data_df[self.data_df['month'] == target_month]
        annual_month_df = self.data_df[self.data_df['month'] == 12]

        month_revenue_df = self.data_df.pivot(
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

        target_month_df = target_month_df.set_index("year").T

        return_dict = {
            "month_revenue": month_revenue_df[sorted(month_revenue_df.columns, reverse=True)],
            "this_month_revenue_over_years": target_month_df.loc[[
                "revenue", "revenue_increment_ratio", "YoY_1", "YoY_3", "YoY_5", "YoY_10"
            ]],
            "grand_total_over_years": target_month_df.loc[[
                "grand_total", "grand_total_increment_ratio", "grand_total_YoY_1", "grand_total_YoY_3", "grand_total_YoY_5", "grand_total_YoY_10"
            ]],
            "recent_month_revenue": self._get_recent_growth(
                fetched_data, 
                grand_total_dict=annual_total_df.to_dict(), 
                interval=12
            )
        }

        return return_dict

    def _get_recent_growth(self, monthly_data, grand_total_dict, interval=12):
        last_month_data = monthly_data[-(interval + 1): ]  + [{}] * max(0, interval - len(monthly_data) + 1)

        MoMs = [
            YoY_Calculator.cal_growth(this.get('revenue'), last.get('revenue'), delta = 1)
            for last, this in zip(last_month_data[:interval], last_month_data[1 :interval + 1])
        ]

        def safe_accum_yoy(data):
            try:
                year = data['year'] - 1
                total = grand_total_dict[year][12]
                grand_total = data.get('grand_total')
                return f"{round(((grand_total - total) / total) * 100, 2)}%"
            except Exception:
                return None

        recent_month_data = {
            "date": [f"{d.get('year', 0)}/{d.get('month', 0)}" for d in last_month_data[:interval]],
            "revenue": [d.get('revenue') for d in last_month_data[:interval]],
            "MoM": [f"{(m * 100):.2f}%" if isinstance(m, float) else None for m in MoMs],
            "YoY": [d.get('revenue_increment_ratio') for d in last_month_data[:interval]],
            "total_YoY": [d.get('grand_total_increment_ratio') for d in last_month_data[:interval]],
            # accum_YoY
            # accum_YoY 為 Davis提出的定義
            # 2024/6的累計YoY(accum_YoY) 為 2024累計到6月為止的總營收/2023年度總營收
            "accum_YoY": [safe_accum_yoy(d) for d in last_month_data[:interval]]
        }

        df = pd.DataFrame(recent_month_data)
        return df[df['date'] != "0/0"].set_index('date').T


    def _get_empty_structure(self):
        """
        Exception 發生時回傳
        """
        target_date = datetime.today()
        target_year, target_month = target_date.year, target_date.month
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