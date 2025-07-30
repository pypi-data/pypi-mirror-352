from .base import BaseBalanceSheetTransformer
from neurostats_API.utils import StatsProcessor


class TWSEBalanceSheetTransformer(BaseBalanceSheetTransformer):

    def __init__(self, ticker, company_name, zone):
        super().__init__(ticker, company_name, zone)

        self.table_settings = StatsProcessor.load_yaml(
            "twse/balance_sheet.yaml"
        )
        self.return_keys = [
            'balance_sheet', 'total_asset', 'current_asset',
            'non_current_asset', 'current_debt', 'non_current_debt', 'equity',
            'balance_sheet_all', 'balance_sheet_YoY'
        ]

        self.stats_df = None
        self.new_df = None

    def process_transform(self, fetched_data):
        if (not fetched_data):
            return self._get_empty_structure()

        processed_data = self._process_fn(fetched_data)

        return processed_data

    def _process_fn(self, fetched_data):

        return_dict = {"ticker": self.ticker, "company_name": self.company_name}

        target_season = fetched_data[0]['season']

        self.stats_df = self._process_twse_to_stats_format(fetched_data)
        self.stats_df = self._slice_target_season(self.stats_df, target_season)

        # 轉換格式 (元 / 千元 / %)
        self.stats_df = StatsProcessor.expand_value_percentage(self.stats_df)
        self.stats_df = self._apply_process_unit_pipeline(
            self.stats_df, postfix_list=['_value', "_percentage"]
        )

        self.new_df = self._process_twse_to_tej_format(fetched_data)
        # 轉換格式 (元 / 千元 / %)
        self.new_df = self._apply_process_unit_pipeline(
            self.new_df, postfix_list=['_value', "_percentage"]
        )

        self.new_dict = self.new_df.to_dict()
        self.new_df = self._cal_QoQ(self.new_dict)
        self.new_df = self.new_df.T

        total_table_YoY = self._slice_target_season(
            self.new_df, target_season
        )

        return_dict.update(
            {
                "balance_sheet": self.stats_df,
                "balance_sheet_all": self.new_df,
                "balance_sheet_YoY": total_table_YoY
            }
        )
        # 抽取出小欄位整合
        self._process_target_columns(return_dict, self.stats_df)

        return return_dict

    def _process_target_columns(self, return_dict, stats_df):
        for name, setting in self.table_settings.items():
            target_indexes = setting.get('target_index', [None])
            for target_index in target_indexes:
                try:
                    return_dict[name] = StatsProcessor.slice_old_table(
                        total_table=stats_df, target_index=target_index
                    )
                    break
                except Exception as e:
                    continue
