from .base import BaseBalanceSheetTransformer
from neurostats_API.utils import StatsProcessor


class USBalanceSheetTransformer(BaseBalanceSheetTransformer):

    def __init__(self, ticker, company_name, zone):
        super().__init__(ticker, company_name, zone)

        self.data_df = None
        self.return_keys = [
            'balance_sheet',
            'balance_sheet_YoY'
        ]

    def process_transform(self, fetched_data):
        if (not fetched_data):
            return self._get_empty_structure()

        return_dict = {"ticker": self.ticker, "company_name": self.company_name}

        # QoQ表格
        self.data_df = self._process_us_format(fetched_data)

        # YoY表格
        target_season = fetched_data[0]['season']
        total_table_YoY = self._slice_target_season(
            self.data_df.T, target_season
        )

        return_dict.update(
            {
                'balance_sheet': self.data_df,
                "balance_sheet_YoY": total_table_YoY
            }
        )

        return return_dict
