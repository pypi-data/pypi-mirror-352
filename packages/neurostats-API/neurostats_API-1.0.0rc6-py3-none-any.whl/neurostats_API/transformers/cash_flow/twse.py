from .base import BaseCashFlowTransformer
from neurostats_API.utils import StatsProcessor

class TWSECashFlowTransformer(BaseCashFlowTransformer):
    def __init__(self, ticker, company_name, zone):
        super().__init__(ticker, company_name, zone)

        self.cash_flow_dict = StatsProcessor.load_yaml(
            "twse/cash_flow_percentage.yaml"
        )  # 計算子表格用

        self.return_keys = ['cash_flow', 'CASHO', 'CASHI', 'CASHF', 'cash_flow_all', 'cash_flow_YoY']

    def process_transform(self, fetched_data):
        """
        轉換整體
        """
        if (not fetched_data):
            return self._get_empty_structure()

        return_dict = {
            "ticker": self.ticker,
            "company_name": self.company_name
        }

        return_dict.update(self.process_stats_page(fetched_data))
        return_dict.update(self.process_QoQ(fetched_data))

        return return_dict
    def process_stats_page(self, fetched_data):
        """
        這裡主要回傳stats頁面相關的部分
        """
        if (not fetched_data):
            return self._get_empty_structure()

        stats_page_df, CASHO_df, CASHI_df, CASHF_df = self._process_twse_to_stats_format(fetched_data)
        target_season = fetched_data[0]['season']

        return {
            'cash_flow': self._slice_and_expand(stats_page_df, target_season),
            "CASHO": self._slice_and_expand(CASHO_df, target_season),
            "CASHI": self._slice_and_expand(CASHI_df, target_season),
            "CASHF": self._slice_and_expand(CASHF_df, target_season)
        }
    
    def process_QoQ(self, fetched_data):
        """
        這裡主要只會回傳其他地方需要的部分，此符合TEJ格式
        """
        if (not fetched_data):
            return self._get_empty_structure()
        
        data_df = self._process_twse_to_tej_format(fetched_data)
        data_df = self._cal_QoQ(data_df.T.to_dict())
        data_df = data_df.T
        target_season = fetched_data[0]['season']

        data_df_YoY = self._slice_target_season(data_df, target_season)

        return {
            "cash_flow_all": data_df,
            "cash_flow_YoY": data_df_YoY
        }

    def _slice_and_expand(self, data_df, target_season):
        data_df = self._slice_target_season(data_df, target_season)
        data_df = StatsProcessor.expand_value_percentage(data_df)

        return data_df