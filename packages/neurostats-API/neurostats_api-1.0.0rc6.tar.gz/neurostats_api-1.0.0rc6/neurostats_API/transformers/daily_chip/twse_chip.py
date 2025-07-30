from .base import BaseChipTransformer
from datetime import date, datetime
import inspect
import numpy as np
import pandas as pd
from neurostats_API.utils import StatsProcessor


class TWSEChipTransformer(BaseChipTransformer):

    def __init__(self, ticker, company_name, zone):
        super().__init__(ticker, company_name, zone)

    def process_transform(self, tech_data, **fetched_datas):
        """
        fetched_datas:
            {
                "institution_trading": {}
                "margin_trading": {},
                "security_lending: {},
            }
        """
        if not fetched_datas:
            return self._get_empty_structure()    # 若查無資料，回傳空表結構

        return_dict = {
            "ticker": self.ticker,
            "company_name": self.company_name,
            'latest_trading': {},
            'annual_trading': {},
            'price': {}
        }

        for key, fetched_data in fetched_datas.items():

            tech_dict = {data['date']: data for data in tech_data}
            latest_tech = tech_data[-1]
            if (not fetched_data):
                return_dict['latest_trading'].update(
                    self._process_latest({}, latest_tech, key)
                )
                return_dict['annual_trading'].update(
                    self._process_annual({}, tech_dict, key)
                )
                continue

            fetched_dict = {data['date']: data[key] for data in fetched_data}
            latest_data = fetched_data[-1]

            return_dict['latest_trading'].update(
                self._process_latest(latest_data, latest_tech, key)
            )
            return_dict['annual_trading'].update(
                self._process_annual(fetched_dict, tech_dict, key)
            )

        tech_df = pd.DataFrame(tech_data)
        return_dict['price'] = self._process_tech(tech_df)

        return return_dict

    def _process_latest(self, latest_data: dict, latest_tech: dict, key: str):
        latest_trade = latest_data.get(key)
        return {
            "date":
            latest_data.get('date',
                            datetime.today().strftime("%Y-%m-%d")),
            **self._process_latest_trading(latest_trade, latest_tech, key)
        }

    def _process_annual(self, fetched_dict: dict, tech_dict: dict, key: str):
        if (fetched_dict):
            fetched_data = [
                {
                    'date': date,
                    'close': tech_dict.get(date, {}).get('close', 0.0),
                    'volume': tech_dict.get(date, {}).get('volume', 0.0),
                    **trading
                } for date, trading in fetched_dict.items()
            ]
            fetched_df = self._process_annual_trading(fetched_data, key)

        else:
            fetched_data = [
                {
                    'date': date,
                    'close': tech_dict.get(date, {}).get('close', 0.0),
                    'volume': tech_dict.get(date, {}).get('volume', 0.0),
                } for date in tech_dict.keys()
            ]
            fetched_df = pd.DataFrame(fetched_data)

        return {key: fetched_df}

    def _process_latest_trading(self, latest_trading, latest_tech, key):
        FN_MAP = {
            'institution_trading': self._process_latest_institution,
            'margin_trading': self._process_latest_margin,
            'security_lending': self._process_latest_security
        }

        process_fn = FN_MAP.get(key)
        return process_fn(latest_trading, latest_tech)

    def _process_annual_trading(self, fetched_data, key):
        FN_MAP = {
            'institution_trading': self._process_annual_institution,
            'margin_trading': self._process_annual_margin,
            'security_lending': self._process_annual_security
        }

        process_fn = FN_MAP.get(key)
        return process_fn(fetched_data)

    def _process_tech(self, tech_df):
        latest_daily_data = tech_df.iloc[-1]
        yesterday_daily_data = tech_df.iloc[-2]

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

        lowest = pd.to_numeric(tech_df["low"], errors="coerce").min().item()
        highest = pd.to_numeric(tech_df["high"], errors="coerce").max().item()
        price_dict['52weeks_range'] = f"{lowest:.2f} - {highest:.2f}"

        return price_dict

    def _process_latest_institution(self, latest_trading, latest_tech):

        def _default_institution_chart():
            return {
                "buy": {
                    "stock": None,
                    "price": None,
                    "average_price": None,
                    "percentage": None
                },
                "sell": {
                    "stock": None,
                    "price": None,
                    "average_price": None,
                    "percentage": None
                },
                "over_buy_sell": {
                    "stock": None,
                    "price": None,
                    "average_price": None,
                    "percentage": None
                },
            }

        latest_table = {
            "foreign": _default_institution_chart(),
            "mutual": _default_institution_chart(),
            "prop": _default_institution_chart(),
            "institutional_investor": _default_institution_chart(),
        }

        volume = latest_tech['volume']

        if (latest_trading is not None):
            for key in latest_trading.keys():
                if (key.find("外陸資") >= 0 or key.find("外資") >= 0):
                    self._target_institution(
                        latest_trading, latest_table['foreign'], key, volume
                    )
                elif (key.find("自營商") >= 0):
                    self._target_institution(
                        latest_trading, latest_table['prop'], key, volume
                    )
                elif (key.find("投信") >= 0):
                    self._target_institution(
                        latest_trading, latest_table['mutual'], key, volume
                    )
                elif (key.find("三大法人") >= 0):
                    self._target_institution(
                        latest_trading, latest_table['institutional_investor'],
                        key, volume
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

        return {"institution_trading": latest_df}

    def _process_annual_institution(self, trading_datas):

        return pd.DataFrame(trading_datas)

    def _process_annual_margin(self, trading_datas):
        # 融資
        def _process(data):
            if ('現金償還' in data['financing'].keys()):
                data['financing']['現償'] = data['financing'].pop('現金償還')
                data['short_selling']['現償'] = data['short_selling'].pop(
                    '現券償還', data['financing']['現償']
                )
            financing = {
                f"融資_{type_name}": num_of_stocks
                for type_name, num_of_stocks in data['financing'].items()
            }

            short_selling = {
                f"融券_{type_name}": num_of_stocks
                for type_name, num_of_stocks in data['short_selling'].items()
            }

            security_offset = data['資券互抵']

            return {**financing, **short_selling, '資券互抵': security_offset}

        if (trading_datas):
            return_datas = [
                {
                    'date': data['date'],
                    'close': data['close'],
                    'volume': data['volume'],
                    **_process(data)
                } for data in trading_datas
            ]
        else:
            return_datas = []

        # 接起來
        return_datas = pd.DataFrame(return_datas)

        return return_datas

    def _process_annual_security(self, trading_datas):

        def _process(data):
            stock_lendings = {
                f"借券_{type_name}":
                (num_of_stocks /
                 1000) if isinstance(num_of_stocks,
                                     (int, float)) else num_of_stocks
                for type_name, num_of_stocks in data['stock_lending'].items()
            }

            return stock_lendings

        if (trading_datas):
            return_datas = [
                {
                    'date': data['date'],
                    'close': data['close'],
                    'volume': data['volume'],
                    **_process(data)
                } for data in trading_datas
            ]
        else:
            return_datas = []

        # 接起來
        return_datas = pd.DataFrame(return_datas)

        return return_datas

    def _target_institution(self, old_table, new_table, key, volume):
        if (key.find("買進") >= 0):
            self._cal_institution(old_table, new_table['buy'], key, volume)
        elif (key.find("賣出") >= 0):
            self._cal_institution(old_table, new_table['sell'], key, volume)
        elif (key.find("買賣超") >= 0):
            self._cal_institution(
                old_table, new_table['over_buy_sell'], key, volume
            )

    def _cal_institution(self, old_table, new_table, key, volume):
        new_table['stock'] = np.round(old_table[key] / 1000, 2).item()
        new_table['percentage'] = np.round((old_table[key] / volume) * 100,
                                           2).item()

    def _process_latest_margin(self, latest_trading, *args):

        def _default_margin_chart():
            dafault_dict = {"financing": {}, "short_selling": {}}
            return {
                "margin_trading": pd.DataFrame.from_dict(dafault_dict),
                "security_offset": None
            }

        if (latest_trading is None):
            return _default_margin_chart()

        latest_trading['financing']['現償'] = latest_trading['financing'].pop(
            '現金償還'
        )
        latest_trading['short_selling']['現償'] = latest_trading['short_selling'
                                                               ].pop('現券償還')

        latest_trading_df = {
            category: sub_dict
            for category, sub_dict in latest_trading.items()
            if (isinstance(sub_dict, dict))
        }

        latest_margin_trading_df = pd.DataFrame.from_dict(latest_trading_df)

        return {
            "margin_trading": latest_margin_trading_df,
            "security_offset": latest_trading['資券互抵']
        }

    def _process_latest_security(self, latest_trading, *args):

        def _default_margin_chart():
            return {
                "stock_lending":
                pd.DataFrame(
                    index=["當日賣出", "現償", "當日還券", "當日調整", "當日餘額", "次一營業日可限額"]
                )
            }

        if (latest_trading is None):
            return _default_margin_chart()

        latest_stock_lending = latest_trading['stock_lending']

        latest_stock_lending = {
            type_name: StatsProcessor.cal_round_int(value / 1000)
            for type_name, value in latest_stock_lending.items()
        }
        latest_stock_lending.pop("前日餘額")
        latest_stock_lending_df = pd.DataFrame.from_dict(
            latest_stock_lending, orient="index", columns=['stock_lending']
        )

        return latest_stock_lending_df

    def _get_empty_structure(self):
        return_dict = {
            "ticker": self.ticker,
            "company_name": self.company_name,
        }

        return_dict['latest_trading'] = {
            'date': date.today(),
            'institution_trading': pd.DataFrame(),
            'margin_trading': pd.DataFrame(),
            'security_lending': pd.DataFrame()
        }

        return_dict['annual_trading'] = {
            'institution_trading':
            pd.DataFrame(columns=['date', 'close', 'volume']),
            'margin_trading': pd.DataFrame(columns=['date', 'close', 'volume']),
            'security_lending':
            pd.DataFrame(columns=['date', 'close', 'volume']),
        }

        return_dict['price'] = {
            "open": None,
            'close': None,
            'range': None,
            'volume': None,
            'last_open': None,
            'last_close': None,
            'last_range': None,
            'last_volume': None,
            '52weeks_range': None
        }

        return return_dict
