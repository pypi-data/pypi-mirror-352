from .base import BaseProfitLoseTransformer
from neurostats_API.utils import StatsProcessor, YoY_Calculator
import pandas as pd


class TWSEProfitLoseTransformer(BaseProfitLoseTransformer):
    def __init__(self, ticker, company_name, zone):
        super().__init__(ticker, company_name, zone)

        # 載入欄位切片設定檔（定義哪些欄位要顯示在報表上）
        self.table_settings = StatsProcessor.load_yaml("twse/profit_lose.yaml")

        # 設定最後回傳的所有欄位 key，包含主頁面、總覽、成長率、比率等
        self.return_keys = [
            'profit_lose', 'grand_total_profit_lose', 'revenue', 'grand_total_revenue', 
            'gross_profit', 'grand_total_gross_profit', 'gross_profit_percentage', 
            'grand_total_gross_profit_percentage', 'operating_income', 'grand_total_operating_income', 'operating_income_percentage', 
            'grand_total_operating_income_percentage', 'net_income_before_tax', 'grand_total_net_income_before_tax', 'net_income_before_tax_percentage', 
            'grand_total_net_income_before_tax_percentage', 'net_income', 'grand_total_net_income', 'net_income_percentage', 
            'grand_total_income_percentage', 'EPS', 'EPS_growth', 'grand_total_EPS', 
            'grand_total_EPS_growth', 'profit_lose_all', 'profit_lose_YoY'
        ]

        self.stats_df = None  # 主頁面統計用 DataFrame
        self.new_df = None    # 完整表格用 DataFrame（包含 TEJ 格式）
    
    def process_transform(self, fetched_data):
        if (not fetched_data):
            return self._get_empty_structure()  # 若查無資料，回傳空表結構

        processed_data = self._process_fn(fetched_data)

        return processed_data


    def _process_fn(self, fetched_data):
        return_dict = {
            "ticker": self.ticker,
            "company_name": self.company_name,
        }

        target_season = fetched_data[-1]['season']  # 用來選擇同一季的欄位當作 YoY 主體

        # 轉換原始 JSON -> dict 格式（key: Q1 ~ Q4）
        stats_dict = self._process_twse_to_stats_format(fetched_data).to_dict()

        # 計算 QoQ 與 YoY 成長率欄位
        stats_dict = YoY_Calculator.cal_QoQ(stats_dict)

        # 建立主頁面 DataFrame 並擴充 _value / _percentage 欄位
        self.stats_df = pd.DataFrame.from_dict(stats_dict)
        self.stats_df = self._slice_target_season(self.stats_df, target_season)
        self.stats_df = StatsProcessor.expand_value_percentage(self.stats_df)

        # 處理各種單位轉換欄位
        self.stats_df = self._apply_process_unit_pipeline(
            self.stats_df,
            postfix_list=[
                '_value',
                '_percentage',
                '_growth',
                "_YoY_1",
                "_YoY_3",
                "_YoY_5",
                "_YoY_10",
            ]
        )

        # 篩選主頁面欄位（排除 grand_total 欄）
        grand_total_value_col = self.stats_df.columns.str.endswith("grand_total_value")
        grand_total_percentage_col = self.stats_df.columns.str.endswith("grand_total_percentage")
        self.stats_df = self.stats_df.loc[
            :,
            (~grand_total_value_col) & (~grand_total_percentage_col) 
        ]

        
        stats_main_page_df = StatsProcessor.slice_table(
            self.stats_df,
            mode = 'value_and_percentage',
        )
        stats_grand_total_df = StatsProcessor.slice_table(
            self.stats_df,
            mode = 'grand_total_values'
        )

        # 建立完整表格 new_df，轉為 TEJ 標準格式並做單位處理
        self.new_df = self._process_twse_to_tej_format(stats_dict)
        self.new_df = self._apply_process_unit_pipeline(
            self.new_df,
            postfix_list=[
                '_value',
                '_percentage',
                '_growth',
                "_YoY_1",
                "_YoY_3",
                "_YoY_5",
                "_YoY_10",
            ]
        )
        # 建立 YoY 子表格（以 transposed 的方式）
        new_df_YoY = self._slice_target_season(self.new_df.T, target_season)

        # 回填主欄位資訊至結果 dict
        return_dict.update({
            "profit_lose": stats_main_page_df,
            "grand_total_profit_lose": stats_grand_total_df,
            "profit_lose_all": self.new_df,
            "profit_lose_YoY": new_df_YoY
        })

        # 根據設定檔切出其他欄位（如營收、毛利率等）
        self._process_target_columns(
            return_dict,
            new_df_YoY.T,
        )

        return return_dict

    def _process_target_columns(self, return_dict ,data_df):
        for name, setting in self.table_settings.items():
            target_indexes = setting.get('target_index', [None])
            for target_index in target_indexes:
                try:
                    # 使用設定檔定義的 mode + index，切出對應欄位表格
                    return_dict[name] = StatsProcessor.slice_table(
                        total_table=data_df,
                        mode=setting['mode'],
                        target_index=target_index
                    )
                    break  # 第一個成功就跳出（允許 fallback 多個 index）
                except Exception as e:
                    continue