from ..base import BaseTransformer
from datetime import datetime
import holidays
from neurostats_API.utils import StatsProcessor
import numpy as np
import pandas as pd
import pytz


class BaseFinanceOverviewTransformer(BaseTransformer):

    def __init__(self, ticker, company_name, zone):
        super().__init__(ticker, company_name, zone)
        self.tw_company_list = StatsProcessor.load_json(
            "company_list/ticker_index_industry_map.json"
        )
        self.us_company_list = StatsProcessor.load_json(
            "company_list/us_TradingView_list.json"
        )

    def _get_latest_date(self, tech_data):
        latest_date = tech_data.iloc[-1]['date']
        if (latest_date is None):
            str_date = datetime.today().strftime("%Y-%m-%d")
        if (isinstance(latest_date, datetime)):
            str_date = latest_date.strftime("%Y-%m-%d")
        elif (isinstance(latest_date, str)):
            str_date = latest_date

        return f"{str_date} [GMT+8]"

    def _get_latest_close(self, tech_data):
        latest_close = tech_data.iloc[-1]['close']
        latest_close = str(round(latest_close, 2))
        return latest_close

    def _get_latest_offset(self, tech_data):
        latest_close = tech_data.iloc[-1]['close']
        previous = tech_data.iloc[-2]['close']

        offset = latest_close - previous
        percentage = offset / previous

        offset = str(np.round(offset, 2))

        return {'value': offset, "percentage": f"{percentage:.2f}%"}

    def _get_category(self):

        def tw_category(ticker):
            return self.tw_company_list.get(ticker, {}).get('industry')

        def us_category(ticker):
            return self.us_company_list.get(ticker, {}).get('en_industry')

        fn_map = {'tw': tw_category, 'us': us_category}

        get_fn = fn_map.get(self.zone)
        return get_fn(self.ticker)

    def _get_latest_volume(self, tech_data):
        try:
            volume = round(tech_data[-1]['volume'], 2)
            return str(volume)
        except Exception as e:
            return "Error"

    def _get_TTM_data(self, datas):
        dfs = pd.DataFrame(datas)
        TTM_data = dfs.mean()

        return TTM_data

    def _process_TTM_tw(self, datas):
        return datas

    def _get_latest_average_volume(self, tech_data, length=30):
        try:
            tech_data = pd.DataFrame(tech_data).tail(length)

            value = tech_data['volume'].mean().item()
            value = round(value, 2)

            return str(value)

        except Exception as e:
            return "Error"

    def _get_market_capitalization(self, daily_data, seasonal_data):
        try:
            latest_close = float(self._get_latest_close(daily_data))
            latest_common_share = seasonal_data[-1]['Common Stock']

            percentage = round((latest_close * latest_common_share), 2)

            return str(percentage)

        except Exception as e:
            return "Error"

    def _get_PE(self, daily_data, TTM_data):
        try:
            latest_close = float(self._get_latest_close(daily_data))
            TTM_EPS = TTM_data['Diluted EPS']

            value = round((latest_close / TTM_EPS), 2)

            return str(value)

        except Exception as e:
            return "Error"

    def _get_PS(self, daily_data, TTM_data, seasonal_data):
        try:
            market_capitalzation = self._get_market_capitalization(
                daily_data, seasonal_data
            )
            market_capitalzation = float(market_capitalzation)
            TTM_revenue = TTM_data['Total Revenue']

            value = round((market_capitalzation / TTM_revenue), 2)

            return str(value)
        except Exception as e:
            return "Error"

    def _is_us_market_open(self):

        taiwan_dt = datetime.now(pytz.timezone('Asia/Taipei'))

        # 轉成美東時間（會自動處理夏令時間）
        eastern = pytz.timezone('US/Eastern')
        us_dt = taiwan_dt.astimezone(eastern)

        # 假日判斷
        us_holidays = holidays.NYSE(years=us_dt.year)
        if us_dt.date() in us_holidays:
            return False

        # 週末
        if us_dt.weekday() >= 5:    # 5 = Saturday, 6 = Sunday
            return False

        # 判斷是否在開盤時間
        market_open = us_dt.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = us_dt.replace(hour=16, minute=0, second=0, microsecond=0)

        return market_open <= us_dt <= market_close

    def _process_us_format(self, fetched_data):
        """
        主要用於report generator
        """
        table_dict = {}
        for data in fetched_data:
            year, season, balance_sheet = data['year'], data['season'], data[
                'balance_sheet']
            time_index = f"{year}Q{season}"

            table_dict[time_index] = balance_sheet

        stats_df = pd.DataFrame.from_dict(table_dict)
        return stats_df.T


class FinanceOverviewProcessor(StatsProcessor):

    @classmethod
    def process_rate(cls, finance_dict):
        for key in finance_dict:
            if ('YoY' in key):
                finance_dict[key] = StatsProcessor.cal_percentage(
                    finance_dict[key]
                )
            elif ("rate" in key or 'ratio' in key):
                finance_dict[key] = StatsProcessor.cal_non_percentage(
                    finance_dict[key], to_str=True, postfix='%'
                )
            else:
                finance_dict[key] = StatsProcessor.cal_non_percentage(
                    finance_dict[key]
                )

    @classmethod
    def process_thousand_dollar(cls, finance_dict):
        process_index = [
            "revenue", "gross_profit", "operating_income", "net_income",
            "operating_cash_flow", "invest_cash_flow", "financing_cash_flow",
            "fcf", 'current_assets', 'current_liabilities',
            'non_current_assets', 'non_current_liabilities', 'total_assets',
            "total_liabilities", "equity"
        ]

        for index in process_index:
            try:
                finance_dict[index] = StatsProcessor.cal_non_percentage(
                    finance_dict[index], postfix="千元"
                )
            except Exception as e:
                finance_dict[index] = None

    @classmethod
    def process_all(cls, finance_dict):
        methods = [
            cls.cal_EBIT,
            cls.cal_share_outstanding,
            cls.cal_fcf,
            cls.cal_interest_bearing_debt,
            cls.cal_revenue_per_share,
            cls.cal_gross_per_share,
            cls.cal_operating_income_per_share,
            cls.cal_operating_cash_flow_per_share,
            cls.fcf_per_share,
            cls.cal_roa,
            cls.cal_roe,
            cls.cal_gross_over_asset,
            cls.cal_roce,
            cls.cal_gross_profit_marginal,
            cls.cal_operation_profit_rate,
            cls.cal_operating_cash_flow_profit_rate,
            cls.cal_dso,
            cls.cal_account_receive_over_revenue,
            cls.cal_dpo,
            cls.cal_inventories_cycle_ratio,
            cls.cal_dio,
            cls.cal_inventories_revenue_ratio,
            cls.cal_cash_of_conversion_cycle,
            cls.cal_asset_turnover,
            cls.cal_application_turnover,
            cls.cal_current_ratio,
            cls.cal_quick_ratio,
            cls.cal_debt_to_equity_ratio,
            cls.cal_net_debt_to_equity_ratio,
            cls.cal_interest_coverage_ratio,
            cls.cal_debt_to_operating_cash_flow,
            cls.cal_debt_to_free_cash_flow,
            cls.cal_cash_flow_ratio,
        ]

        for method in methods:
            method(finance_dict)

    @classmethod
    def cal_EBIT(cls, finance_dict):
        """
        計算EBIT
        EBIT = 營業收入 - 營業成本 - 營業費用 - 所得稅費用
        """
        try:
            EBIT = (
                finance_dict['revenue'] - finance_dict['operating_cost'] -
                finance_dict['operating_expenses'] - finance_dict['tax_fee']
            )
            finance_dict['EBIT'] = StatsProcessor.cal_non_percentage(EBIT)
        except (KeyError, ZeroDivisionError, TypeError) as e:
            finance_dict['EBIT'] = None
            # print(f"Error calculating EBIT: {e}")

    @classmethod
    def cal_fcf(cls, finance_dict):
        """
        計算自由現金流(FCF):
        自由現金流 =  營業現金流 + 投資現金流
        """
        try:
            fcf = (
                finance_dict["operating_cash_flow"] +
                finance_dict["financing_cash_flow"]
            )
            finance_dict["fcf"] = StatsProcessor.cal_non_percentage(fcf)
        except (KeyError, ZeroDivisionError, TypeError) as e:
            finance_dict['fcf'] = None
            # print(f"Error calculating FCF: {e}")

    @classmethod
    def cal_interest_bearing_debt(cls, finance_dict):
        """
        計算有息負債
        短期借款+長期借款
        """
        finance_dict['interest_bearing_debt'] = 0.0

        try:
            finance_dict['interest_bearing_debt'] += finance_dict[
                'short_term_liabilities']
        except (KeyError, ZeroDivisionError, TypeError) as e:
            finance_dict['interest_bearing_debt'] += 0.0
        try:
            finance_dict['interest_bearing_debt'] += finance_dict[
                'long_term_liabilities']
        except (KeyError, ZeroDivisionError, TypeError) as e:
            finance_dict['interest_bearing_debt'] += 0.0

    @classmethod
    def cal_share_outstanding(cls, finance_dict):
        """
        計算流通股數
        流通股數 = 本期淨利 ÷ 基本每股盈餘
        """
        try:
            finance_dict["share_outstanding"] = (
                finance_dict['net_income'] / finance_dict['eps']
            )
        except (KeyError, ZeroDivisionError, TypeError) as e:
            finance_dict['share_outstanding'] = None
            # print(f"share_outstanding failed because of {str(e)}")

    @classmethod
    def cal_revenue_per_share(cls, finance_dict):
        """
        計算每股營收
        每股營收 = 營業收入 / 在外流通股數
        """
        try:
            revenue_per_share = (
                finance_dict['revenue'] / finance_dict['share_outstanding']
            )
            finance_dict['revenue_per_share'
                         ] = StatsProcessor.cal_non_percentage(
                             revenue_per_share, False
                         )
        except (KeyError, ZeroDivisionError, TypeError) as e:
            finance_dict['revenue_per_share'] = None
            # print(f"revenue_per_share failed because of {str(e)}")

    @classmethod
    def cal_gross_per_share(cls, finance_dict):
        """
        計算每股毛利
        = （當期營業毛利）÷（當期在外流通股數）
        """
        if ('gross_profit' not in finance_dict.keys()):
            try:
                finance_dict['gross_profit'] = (
                    finance_dict['revenue'] - finance_dict['operating_cost']
                )
            except:
                finance_dict['gross_profit'] = None
        try:
            gross_per_share = (
                finance_dict['gross_profit'] / finance_dict['share_outstanding']
            )
            finance_dict['gross_per_share'] = StatsProcessor.cal_non_percentage(
                gross_per_share, False
            )

        except (KeyError, ZeroDivisionError, TypeError) as e:
            finance_dict['gross_per_share'] = None
            # print(f"gross_per_share failed because of {str(e)}")

    @classmethod
    def cal_operating_income_per_share(cls, finance_dict):
        """
        計算每股營業利益
        每股營業利益= （當期營業利益）÷（當期在外流通股數）
        """
        try:
            operating_income_per_share = (
                finance_dict['operating_income'] /
                finance_dict['share_outstanding']
            )
            finance_dict['operating_income_per_share'
                         ] = StatsProcessor.cal_non_percentage(
                             operating_income_per_share
                         )
        except (KeyError, ZeroDivisionError, TypeError) as e:
            finance_dict['operating_income_per_share'] = None
            # print(f"operating_income_per_share failed because of {str(e)}")

    @classmethod
    def cal_operating_cash_flow_per_share(cls, finance_dict):
        """
        計算每股營業現金流
        = (當期營業現金流) ÷（當期在外流通股數）
        """
        try:
            operating_cash_flow_per_share = (
                finance_dict["operating_cash_flow"] /
                finance_dict['share_outstanding']
            )
            finance_dict["operating_cash_flow_per_share"
                         ] = StatsProcessor.cal_non_percentage(
                             operating_cash_flow_per_share
                         )
        except (KeyError, ZeroDivisionError, TypeError) as e:
            finance_dict['operating_cash_flow_per_share'] = None
            # print(f'operating_cash_flow_per_share because of {str(e)}')

    @classmethod
    def fcf_per_share(cls, finance_dict):
        """
        計算每股自由現金流
        每股自由現金流 = (當期自由現金流) ÷（當期在外流通股數）
        """
        try:
            fcf_per_share = (
                finance_dict['fcf'] / finance_dict['share_outstanding']
            )
            finance_dict['fcf_per_share'] = StatsProcessor.cal_non_percentage(
                fcf_per_share
            )
        except (KeyError, ZeroDivisionError, TypeError) as e:
            finance_dict['fcf_per_share'] = None
            # print(f"fcf_per_share failed because of {str(e)}")

# 盈利能力

    @classmethod
    def cal_roa(cls, finance_dict):
        """
        計算資產報酬率(ROA)
        ROA = [ 本期淨利 + 利息費用 × (1-有效稅率) ] ÷（資產總額）
        """
        try:
            roa = (
                finance_dict['net_income'] + finance_dict['interest'] +
                (1 * 0.1)    # 有效稅率需要改，這裡先設0.1
            ) / finance_dict['inventories']

            finance_dict["roa"] = StatsProcessor.cal_percentage(roa)
        except Exception as e:
            finance_dict["roa"] = None

    @classmethod
    def cal_roe(cls, finance_dict):
        """
        計算股東權益報酬率(ROE)
        ROE = (本期淨利) ÷（權益總額）
        """
        try:
            roe = (finance_dict['net_income'] / finance_dict['equity'])
            finance_dict['roe'] = StatsProcessor.cal_percentage(roe)
        except Exception as e:
            finance_dict['roe'] = None

    @classmethod
    def cal_gross_over_asset(cls, finance_dict):
        """
        計算營業毛利/總資產
        """
        try:
            gross_over_asset = (
                finance_dict['gross_profit'] / finance_dict['total_assets']
            )
            finance_dict['gross_over_asset'] = StatsProcessor.cal_percentage(
                gross_over_asset
            )
        except (KeyError, ZeroDivisionError, TypeError) as e:
            finance_dict['gross_over_asset'] = None
            # print(f"營業毛利/總資產 failed because of {str(e)}")

    @classmethod
    def cal_roce(cls, finance_dict):
        """
        計算資本運用報酬率(ROCE):
        ROCE = (稅前淨利＋利息費用) / (資產總額－流動負債)
        """
        try:
            roce = (
                (
                    finance_dict['net_income_before_tax'] +
                    finance_dict['interest']
                ) / (
                    finance_dict['total_assets'] -
                    finance_dict['current_liabilities']
                )
            )
            finance_dict['roce'] = StatsProcessor.cal_percentage(roce)

        except (KeyError, ZeroDivisionError, TypeError) as e:
            finance_dict['roce'] = None
            # print(f"ROCE failed because of {str(e)}")

    @classmethod
    def cal_gross_profit_marginal(cls, finance_dict):
        """
        計算營業毛利率(gross profit margin)
        營業毛利率 = 營業毛利 ÷ 營業收入
        """
        try:
            gross_profit_margin = (
                finance_dict['gross_profit'] / finance_dict['revenue']
            )
            finance_dict['gross_profit_margin'] = StatsProcessor.cal_percentage(
                gross_profit_margin
            )
        except Exception as e:
            finance_dict['gross_profit_margin'] = None
            # print(f"gross_profit_margin failed because of {str(e)}")

    @classmethod
    def cal_operation_profit_rate(cls, finance_dict):
        """
        計算營業利益率
        營業利益率 = ( 營業收入－營業成本－營業費用）÷ 營業收入
        """
        try:
            operation_profit_rate = (
                finance_dict['revenue'] - finance_dict['operating_cost'] -
                finance_dict['operating_expenses']
            ) / finance_dict['revenue']
            finance_dict["operation_profit_rate"
                         ] = StatsProcessor.cal_percentage(
                             operation_profit_rate
                         )
        except (KeyError, ZeroDivisionError, TypeError) as e:
            finance_dict["operation_profit_rate"] = None
            # print(f"operation_profit failed because of {str(e)}")

    @classmethod
    def cal_operating_cash_flow_profit_rate(cls, finance_dict):
        """
        計算營業現金流利潤率
        營業現金流利潤率 = 營業活動現金流 ÷ 營業收入
        """
        try:
            operating_cash_flow_profit_rate = (
                finance_dict["operating_cash_flow"] / finance_dict["revenue"]
            )
            finance_dict["operating_cash_flow_profit_rate"
                         ] = StatsProcessor.cal_percentage(
                             operating_cash_flow_profit_rate
                         )
        except (KeyError, ZeroDivisionError, TypeError) as e:
            finance_dict["operating_cash_flow_profit_rate"] = None
            # print(
            #     f"operating_cash_flow_profit_rate failed because of {str(e)}")


# 成長動能

    """
    前四個已經有了 revenue_YoY, gross_prof_YoY, operating_income_YoY, net_income_YoY:
    後四個在金流，還需要處理
    """
    # 營運指標

    @classmethod
    def cal_dso(cls, finance_dict):
        """
        計算應收帳款收現天數(DSO)
        DSO = 365 × (應收帳款平均餘額 ÷ 營業收入)
        """
        try:
            dso = (
                365 * (finance_dict['account_pay'] / finance_dict['revenue'])
            )
            finance_dict['dso'] = StatsProcessor.cal_non_percentage(
                dso, to_str=True, postfix="日"
            )
        except Exception as e:
            finance_dict['dso'] = None
            # print(f"Error calculating 應收帳款收現天數 because of {str(e)}")

    @classmethod
    def cal_account_receive_over_revenue(cls, finance_dict):
        """
        計算應收帳款佔營收比率
        = 應收帳款平均餘額 ÷ 營業收入
        """
        try:
            account_receive_over_revenue = (
                finance_dict['account_receive'] / finance_dict['revenue']
            )
            finance_dict["account_receive_over_revenue"
                         ] = StatsProcessor.cal_percentage(
                             account_receive_over_revenue
                         )
        except Exception as e:
            finance_dict["account_receive_over_revenue"] = None

    @classmethod
    def cal_dpo(cls, finance_dict):
        """
        計算應付帳款週轉天數
        DPO = 365天 ÷ (銷貨成本÷平均應付帳款)
        """
        try:
            dpo = (
                365 *
                (finance_dict['account_pay'] / finance_dict['operating_cost'])
            )
            finance_dict["dpo"] = StatsProcessor.cal_non_percentage(
                dpo, to_str=True, postfix="日"
            )
        except (KeyError, ZeroDivisionError, TypeError) as e:
            finance_dict["dpo"] = None
            # print(f"應付帳款週轉天數 failed because of {str(e)}")

    @classmethod
    def cal_inventories_cycle_ratio(cls, finance_dict):
        """
        計算存貨周轉率
        = 銷貨成本 ÷ 存貨
        """
        try:
            inventories_cycle_ratio = (
                finance_dict['operating_cost'] / finance_dict['inventories']
            )

            finance_dict["inventories_cycle_ratio"
                         ] = StatsProcessor.cal_percentage(
                             inventories_cycle_ratio
                         )
        except (KeyError, ZeroDivisionError, TypeError) as e:
            finance_dict["inventories_cycle_ratio"] = None
            # print(f"Error calculating 存貨周轉率 because of {str(e)}")

    @classmethod
    def cal_dio(cls, finance_dict):
        """
        計算 存貨週轉天數 or 平均售貨天數
        DIO = 365天 * (存貨 ÷ 銷貨成本)
        MUDA MUDA MUDA !!!
        """
        try:
            dio = 365 * (
                finance_dict["inventories"] / finance_dict["operating_cost"]
            )
            finance_dict["dio"] = StatsProcessor.cal_non_percentage(
                dio, to_str=True, postfix="日"
            )
        except (KeyError, ZeroDivisionError, TypeError) as e:
            finance_dict["dio"] = None
            # print(f"Error calculating 存貨週轉天數 because of {str(e)}")

    @classmethod
    def cal_inventories_revenue_ratio(cls, finance_dict):
        """
        計算存貨佔營收比率
        存貨佔營收比= 存貨 ÷ 營業收入
        """
        try:
            inventories_revenue_ratio = (
                finance_dict['inventories'] / finance_dict['revenue']
            )

            finance_dict["inventories_revenue_ratio"
                         ] = StatsProcessor.cal_percentage(
                             inventories_revenue_ratio
                         )
        except (KeyError, ZeroDivisionError, TypeError) as e:
            finance_dict["inventories_revenue_ratio"] = None
            # print(f"Error calculating 存貨佔營收比率 because of {str(e)}")

    @classmethod
    def cal_cash_of_conversion_cycle(cls, finance_dict):
        """
        計算現金循環週期
        存貨週轉天數 + 應收帳款週轉天數 - 應付帳款週轉天數
        """
        try:
            cash_of_conversion_cycle = (
                finance_dict["dio"] + finance_dict["dso"] - finance_dict['dpo']
            )
            finance_dict["cash_of_conversion_cycle"
                         ] = StatsProcessor.cal_non_percentage(
                             cash_of_conversion_cycle, to_str=True, postfix="日"
                         )
        except (KeyError, ZeroDivisionError, TypeError) as e:
            finance_dict["cash_of_conversion_cycle"] = None

    @classmethod
    def cal_asset_turnover(cls, finance_dict):
        """
        計算資產周轉率
        營業收入 ÷ 資產總額
        """
        try:
            asset_turnover = (
                finance_dict["revenue"] / finance_dict["inventories"]
            )
            finance_dict["asset_turnover"] = StatsProcessor.cal_percentage(
                asset_turnover
            )
        except Exception as e:
            finance_dict["asset_turnover"] = None

    @classmethod
    def cal_application_turnover(cls, finance_dict):
        """
        不動產、廠房及設備週轉率
        營業收入 ÷ 不動產、廠房與設備平均餘額
        """
        try:
            applcation_turnover = (
                finance_dict['revenue'] / finance_dict["application"]
            )
            finance_dict['application_turnover'
                         ] = StatsProcessor.cal_percentage(applcation_turnover)

        except Exception as e:
            finance_dict['application_turnover'] = None

    @classmethod
    def cal_current_ratio(cls, finance_dict):
        """
        計算流動比率 = 流動資產 / 流動負債
        """
        try:
            current_ratio = (
                finance_dict['current_assets'] /
                finance_dict['current_liabilities']
            )
            finance_dict['current_ratio'] = StatsProcessor.cal_percentage(
                current_ratio
            )
        except (KeyError, ZeroDivisionError, TypeError) as e:
            finance_dict['current_ratio'] = None
            # print(f"Error calculating current ratio: {e}")

    @classmethod
    def cal_quick_ratio(cls, finance_dict):
        """
        速動比率
        (流動資產 - 存貨) / 流動負債
        """
        try:
            quick_ratio = (
                finance_dict['current_assets'] - finance_dict['inventories']
            ) / finance_dict['current_liabilities']
            finance_dict['quick_ratio'] = StatsProcessor.cal_percentage(
                quick_ratio
            )
        except (KeyError, ZeroDivisionError, TypeError) as e:
            finance_dict['quick_ratio'] = None
            # print(f"Error calculating quick ratio: {e}")

    @classmethod
    def cal_debt_to_equity_ratio(cls, finance_dict):
        """
        # 負債權益比率 = 總負債 / 股東權益
        """
        try:
            debt_to_equity_ratio = finance_dict['total_liabilities'
                                                ] / finance_dict['equity']
            finance_dict['debt_to_equity_ratio'
                         ] = StatsProcessor.cal_percentage(
                             debt_to_equity_ratio
                         )
        except (KeyError, ZeroDivisionError, TypeError) as e:
            finance_dict['debt_to_equity_ratio'] = None
            # print(f"Error calculating debt to equity ratio: {e}")

    @classmethod
    def cal_net_debt_to_equity_ratio(cls, finance_dict):
        """
        # 淨負債權益比率 = (總負債 - 現金及約當現金) / 股東權益
        """
        try:
            net_debt_to_equity_ratio = (
                finance_dict['total_liabilities'] -
                finance_dict['cash_and_cash_equivalents']
            ) / finance_dict['equity']
            finance_dict['net_debt_to_equity_ratio'
                         ] = StatsProcessor.cal_percentage(
                             net_debt_to_equity_ratio
                         )
        except (KeyError, ZeroDivisionError, TypeError) as e:
            finance_dict['net_debt_to_equity_ratio'] = None
            # print(f"Error calculating net debt to equity ratio: {e}")

    @classmethod
    def cal_interest_coverage_ratio(cls, finance_dict):
        """
        # 利息保障倍數 = EBIT / 利息費用
        """
        try:
            interest_coverage_ratio = finance_dict['EBIT'] / finance_dict[
                'interest_expense']
            finance_dict['interest_coverage_ratio'
                         ] = StatsProcessor.cal_non_percentage(
                             interest_coverage_ratio, to_str=True, postfix="倍"
                         )
        except (KeyError, ZeroDivisionError, TypeError) as e:
            finance_dict['interest_coverage_ratio'] = None
            # print(f"Error calculating interest coverage ratio: {e}")

    @classmethod
    def cal_debt_to_operating_cash_flow(cls, finance_dict):
        """
        有息負債 / 營業活動現金流
        """
        try:
            debt_to_operating_cash_flow = finance_dict[
                'interest_bearing_debt'] / finance_dict['operating_cash_flow']
            finance_dict['debt_to_operating_cash_flow'
                         ] = StatsProcessor.cal_percentage(
                             debt_to_operating_cash_flow
                         )
        except (KeyError, ZeroDivisionError, TypeError) as e:
            finance_dict['debt_to_operating_cash_flow'] = None
            # print(f"Error calculating debt to operating cash flow: {e}")

    @classmethod
    def cal_debt_to_free_cash_flow(cls, finance_dict):
        """
        # 有息負債 / 自由現金流
        """
        try:
            debt_to_free_cash_flow = finance_dict['interest_bearing_debt'
                                                  ] / finance_dict['fcf']
            finance_dict['debt_to_free_cash_flow'
                         ] = StatsProcessor.cal_percentage(
                             debt_to_free_cash_flow
                         )
        except (KeyError, ZeroDivisionError, TypeError) as e:
            finance_dict['debt_to_free_cash_flow'] = None
            # print(f"Error calculating debt to free cash flow: {e}")

    @classmethod
    def cal_cash_flow_ratio(cls, finance_dict):
        """
        # 現金流量比率 = 營業活動現金流 / 流動負債
        """
        try:
            cash_flow_ratio = finance_dict[
                'operating_cash_flow'] / finance_dict['current_liabilities']
            finance_dict['cash_flow_ratio'] = StatsProcessor.cal_percentage(
                cash_flow_ratio
            )
        except (KeyError, ZeroDivisionError, TypeError) as e:
            finance_dict['cash_flow_ratio'] = None
            # print(f"Error calculating cash flow ratio: {e}")
