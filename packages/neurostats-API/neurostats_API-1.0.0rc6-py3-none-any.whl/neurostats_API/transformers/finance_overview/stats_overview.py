from .base import BaseFinanceOverviewTransformer, FinanceOverviewProcessor
from neurostats_API.utils import StatsProcessor


class FinanceOverviewTransformer(BaseFinanceOverviewTransformer):

    def __init__(self, ticker, company_name, zone):
        super().__init__(ticker, company_name, zone)

        self.target_fields = StatsProcessor.load_yaml(
            "twse/finance_overview_dict.yaml"
        )
        self.inverse_dict = StatsProcessor.load_txt(
            "twse/seasonal_data_field_dict.txt", json_load=True
        )

    def process_transform(self, balance_sheet, profit_lose, cash_flow):

        processed_data_dict = self._filter_target_data(
            balance_sheet, profit_lose, cash_flow
        )
        FinanceOverviewProcessor.process_rate(processed_data_dict) # 處理百分比
        FinanceOverviewProcessor.process_all(processed_data_dict) # 計算所有指標公式
        self._fill_nan_index(processed_data_dict) # 處理空值
        FinanceOverviewProcessor.process_thousand_dollar(processed_data_dict) # 處理千元單位

        return processed_data_dict

    def _filter_target_data(self, balance_sheet, profit_lose, cash_flow):
        balance_sheet = balance_sheet[-1]
        cash_flow = cash_flow[-1]
        profit_lose = profit_lose[-1]
        seasons = [
            (int(report['year']), int(report['season']))
            for report in (balance_sheet, profit_lose, cash_flow)
        ]

        max_date = max(seasons)
        year, season = max_date

        data_dict = {
            'balance_sheet': balance_sheet['balance_sheet'],
            'profit_lose': profit_lose['profit_lose'],
            "cash_flow": cash_flow['cash_flow']
        }
        filtered_dict = {
            "year": year,
            "season": season
        }


        for key, target_sets in self.target_fields.items():
            try:
                small_targets = target_sets['field']
                value_index = target_sets['value']

                for small_target in small_targets:
                    big_target = self.inverse_dict[small_target]
                    # 透過inverse_dict取得項目在balance_sheet/profit_lose/cash_flow

                if (small_target == "利息費用_bank"):
                    small_target = small_target[:small_target.find("_bank")]

                seasonal_data = data_dict.get(big_target, {})    # 對應的列表

                filtered_dict[key] = seasonal_data.get(small_target, {}).get(
                    value_index, None
                )    # 取對應的值

            except Exception as e:
                print(f"filter failed :{e}")
                continue

        return filtered_dict

    def _fill_nan_index(self, finance_dict):
        for key in self.target_fields.keys():
            if (key not in finance_dict.keys()):
                finance_dict[key] = None
