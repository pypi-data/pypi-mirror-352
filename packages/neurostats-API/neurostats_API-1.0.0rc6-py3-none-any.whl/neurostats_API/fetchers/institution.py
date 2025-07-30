from .base import StatsFetcher
from datetime import datetime, timedelta, date
import json
import numpy as np
import pandas as pd
from ..utils import StatsDateTime, StatsProcessor
import importlib.resources as pkg_resources
import yaml


class InstitutionFetcher(StatsFetcher):
    """
    iFa -> 交易資訊 -> 法人買賣

    包括: 
    1. 當日交易
    2. 一年內交易
    """

    def __init__(self, ticker, db_client):
        super().__init__(ticker, db_client)
        self.tej_collection = self.db['TWN/APISHRACT'] # TEJ備援

    def prepare_query(self, start_date, end_date):
        pipeline = super().prepare_query()

        # target_query = {
        #     "date": date,
        #     "institution_trading": "$$target_season_data.institution_trading"
        # }

        pipeline.append(
            {
                "$project": {
                    "_id": 0,
                    "ticker": 1,
                    "company_name": 1,
                    "daily_data": {
                        "$map": {
                            "input": {
                                "$filter": {
                                    "input": "$daily_data",
                                    "as": "daily",
                                    "cond": {
                                        "$and": [
                                            {
                                                "$gte":
                                                ["$$daily.date", start_date]
                                            }, {
                                                "$lte":
                                                ["$$daily.date", end_date]
                                            }
                                        ]
                                    }
                                }
                            },
                            "as": "target_daily_data",
                            "in": "$$target_daily_data"
                        }
                    },
                    "institution_trading": {
                        "$map": {
                            "input": {
                                "$filter": {
                                    "input": "$institution_trading",
                                    "as": "institution",
                                    "cond": {
                                        "$and": [
                                            {
                                                "$gte": [
                                                    "$$institution.date",
                                                    start_date
                                                ]
                                            }, {
                                                "$lte": [
                                                    "$$institution.date",
                                                    end_date
                                                ]
                                            }
                                        ]
                                    }
                                }
                            },
                            "as": "target_institution_data",
                            "in": "$$target_institution_data"
                        },
                    }
                }
            }
        )

        return pipeline

    def collect_data(self, start_date, end_date):
        pipeline = self.prepare_query(start_date, end_date)

        fetched_data = self.collection.aggregate(pipeline).to_list()

        return fetched_data[-1]

    def query_data(self):
        try:
            latest_time = StatsDateTime.get_latest_time(
                self.ticker, self.collection
            )['last_update_time']
            latest_date = latest_time['institution_trading']['latest_date']
            end_date = latest_date.replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        except Exception as e:
            end_date = datetime.now(self.timezone)
            end_date = end_date.replace(
                hour=0, minute=0, second=0, microsecond=0
            )

            if (end_date.hour < 17):    # 拿不到今天的資料
                end_date = end_date - timedelta(days=1)

        start_date = end_date - timedelta(days=365)

        fetched_data = self.collect_data(start_date, end_date)

        fetched_data['daily_data'] = sorted(
            fetched_data.get("daily_data", []), key=lambda x: x['date'], reverse=True
        )

        if (not fetched_data['institution_trading']):
            #  找 TEJ 備援
            fetched_data.update(
                {
                    'institution_trading': self.collect_tej(start_date, end_date)
                }
            )
        
        fetched_data['institution_trading'] = sorted(
            fetched_data.get('institution_trading', []),
            key=lambda x: x['date'],
            reverse=True
        ) if fetched_data['institution_trading'] else None

        table_dict = self.process_data(fetched_data)

        return table_dict

    def process_data(self, fetched_data):
        table_dict = dict()

        daily_datas = fetched_data['daily_data']
        institution_tradings = fetched_data['institution_trading']

        latest_daily_data = daily_datas[0]
        yesterday_daily_data = daily_datas[1]

        # 交易價格與昨天交易
        price_dict = {
            "open": round(latest_daily_data['open'], 2),
            'close': round(latest_daily_data['close'], 2),
            'range':
            f"{latest_daily_data['low']:.2f} - {latest_daily_data['high']:.2f}",
            'volume': round(latest_daily_data['volume'] / 1000, 2),
            'last_open': round(yesterday_daily_data['open'], 2),
            'last_close': round(yesterday_daily_data['close'], 2),
            'last_range':
            f"{yesterday_daily_data['low']:.2f} - {yesterday_daily_data['high']:.2f}",
            'last_volume': round(yesterday_daily_data['volume'] / 1000, 2)
        }
        # 一年範圍
        annual_lows = [data['low'] for data in daily_datas]
        annual_highs = [data['high'] for data in daily_datas]
        lowest = np.min(annual_lows).item()
        highest = np.max(annual_highs).item()

        price_dict['52weeks_range'] = f"{lowest:.2f} - {highest:.2f}"
        table_dict['price'] = price_dict

        # 發行股數 & 市值
        # 沒有實作

        table_dict['latest_trading'] = {
            'date': date.today(),
            'table': pd.DataFrame(
                columns = ['category', 'variable', 'close', 'volume']
            )
        }
        table_dict['annual_trading'] = pd.DataFrame(
            columns = ['date', 'close', 'volume']
        )

        if (not institution_tradings):
            return table_dict

        # 今日法人買賣
        latest_trading = institution_tradings[0] if (institution_tradings) else {
            'date': date.today()
        }
        table_dict['latest_trading'] = {
            "date":
            latest_trading['date'],
            "table":
            self.process_latest_trading(
                latest_trading, latest_daily_data['volume']
            )
        }
        # 一年內法人
        annual_dates = [
            data['date'].strftime("%Y-%m-%d") for data in daily_datas
        ]
        annual_closes = {
            data['date'].strftime("%Y-%m-%d"): data['close']
            for data in daily_datas
            if (data['date'].strftime("%Y-%m-%d") in annual_dates)
        }
        annual_volumes = {
            data['date'].strftime("%Y-%m-%d"): data['volume']
            for data in daily_datas
            if (data['date'].strftime("%Y-%m-%d") in annual_dates)
        }
        annual_trading = {
            data['date'].strftime("%Y-%m-%d"): data
            for data in institution_tradings
        }

        annual_trading_dates = sorted(list(annual_trading.keys()))
        annual_trading_skip = {
            date: {
                "close": annual_closes.get(date, 0.0),
                "volume": annual_volumes.get(date, 0.0),
                **annual_trading[date]
            }
            for date in annual_trading_dates
        }

        table_dict['annual_trading'] = self.process_annual_trading(
            annual_dates, annual_trading_skip
        )

        return table_dict

    def process_latest_trading(self, latest_trading, volume):
        latest_table = {
            "foreign": self.default_institution_chart(),
            "mutual": self.default_institution_chart(),
            "prop": self.default_institution_chart(),
            "institutional_investor": self.default_institution_chart(),
        }

        for key in latest_trading.keys():
            if (key.find("外陸資") >= 0 or key.find("外資") >= 0):
                self.target_institution(
                    latest_trading, latest_table['foreign'], key, volume
                )
            elif (key.find("自營商") >= 0):
                self.target_institution(
                    latest_trading, latest_table['prop'], key, volume
                )
            elif (key.find("投信") >= 0):
                self.target_institution(
                    latest_trading, latest_table['mutual'], key, volume
                )
            elif (key.find("三大法人") >= 0):
                self.target_institution(
                    latest_trading, latest_table['institutional_investor'], key,
                    volume
                )
        # 計算合計
        for unit in ['stock', 'percentage']:
            # 買進總和
            latest_table['institutional_investor']['buy'][unit] = (
                latest_table['foreign']['buy'][unit] +
                latest_table['prop']['buy'][unit] +
                latest_table['mutual']['buy'][unit]
            )
            # 賣出總和
            latest_table['institutional_investor']['sell'][unit] = (
                latest_table['foreign']['sell'][unit] +
                latest_table['prop']['sell'][unit] +
                latest_table['mutual']['sell'][unit]
            )

        frames = []
        for category, trades in latest_table.items():
            temp_df = pd.DataFrame(trades).T
            temp_df['category'] = category
            frames.append(temp_df)

        latest_df = pd.concat(frames)
        latest_df = latest_df.reset_index().rename(columns={'index': 'type'})
        latest_df = latest_df[[
            'type', 'category', 'stock', 'price', 'average_price', 'percentage'
        ]]

        latest_df = pd.melt(
            latest_df,
            id_vars=['type', 'category'],
            var_name='variable',
            value_name='value'
        )

        latest_df = latest_df.pivot_table(
            index=['category', 'variable'],
            columns='type',
            values='value',
            aggfunc='first'
        )

        # 重設列名，去除多層索引
        latest_df.columns.name = None    # 去除列名稱
        latest_df = latest_df.reset_index()

        return latest_df

    def process_annual_trading(self, dates, annual_tradings):
        return pd.DataFrame.from_dict(annual_tradings, orient='index')

    def target_institution(self, old_table, new_table, key, volume):
        if (key.find("買進") >= 0):
            self.cal_institution(old_table, new_table['buy'], key, volume)
        elif (key.find("賣出") >= 0):
            self.cal_institution(old_table, new_table['sell'], key, volume)
        elif (key.find("買賣超") >= 0):
            self.cal_institution(
                old_table, new_table['over_buy_sell'], key, volume
            )

    def cal_institution(self, old_table, new_table, key, volume):
        new_table['stock'] = np.round(old_table[key] / 1000, 2).item()
        new_table['percentage'] = np.round((old_table[key] / volume) * 100,
                                           2).item()

    def default_institution_chart(self):
        return {
            "buy": {
                "stock": 0,
                "price": 0,
                "average_price": 0,
                "percentage": 0
            },
            "sell": {
                "stock": 0,
                "price": 0,
                "average_price": 0,
                "percentage": 0
            },
            "over_buy_sell": {
                "stock": 0,
                "price": 0,
                "average_price": 0,
                "percentage": 0
            },
        }

    def collect_tej(self, start_date, end_date):
        pipeline = self.prepare_tej_query(start_date, end_date)

        result = self.tej_collection.aggregate(pipeline)
        result = result.to_list()

        proj_columns = {
            "mdate": "date",
            "qfii_buy": "外資買進股數",
            "qfii_sell": "外資賣出股數",
            "qfii_ex": "外資買賣超股數",
            "fund_buy" : "投信買進股數",
            "fund_sell" : "投信賣出股數",
            "fund_ex" : "投信買賣超股數",
            "dlrp_buy" : "自營商買賣超股數(自行)",
            "dlrp_sell" : "自營商買進股數(自行)",
            "dlrp_ex" : "自營商賣出股數(自行)",
            "dlrh_buy" : "自營商買進股數(避險)",
            "dlrh_sell" : "自營商賣出股數(避險)",
            "dlrh_ex" : "自營買賣超股數(避險)",
            "tot_ex" : "三大法人買賣超股數"
        }
        
        try:
            result_df = pd.DataFrame(result[0]['filtered_data'])
        except Exception as e:
            result_df = pd.DataFrame(columns = list(proj_columns.keys()))

        target_index = list(proj_columns.keys())[1:]
        result_df.loc[:, target_index] = result_df.loc[:, target_index].map(lambda x : 1000 * x) # TEJ單位為千股

        result_df = result_df.loc[:, list(proj_columns.keys())]
        result_df = result_df.reindex(columns = list(proj_columns.keys()), fill_value = None)
        result_df = result_df.rename(columns = proj_columns)

        return result_df.to_dict(orient = 'records')

    def prepare_tej_query(self, start_date, end_date):
    
        return [
            {
                "$match": {
                    "ticker": { "$eq": self.ticker }
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "ticker": 1,
                    "filtered_data": {
                        "$map": {
                            "input": {
                                "$filter": {
                                    "input": "$data",
                                    "as": "item",
                                    "cond": {
                                        "$and": [
                                            { "$gte": ["$$item.mdate", start_date] },
                                            { "$lte": ["$$item.mdate", end_date] }
                                        ]
                                    }
                                }
                            },
                            "as": "filtered_item",
                            "in": "$$filtered_item"
                        }
                    }
                }
            }
        ]