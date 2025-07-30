from ..base import BaseTransformer
from neurostats_API.utils import StatsProcessor
import numpy as np
import pandas as pd

class BaseCashFlowTransformer(BaseTransformer):
    def __init__(self, ticker, company_name, zone):
        super().__init__(ticker, company_name, zone)
    
    def _process_twse_to_stats_format(self, fetched_data):
        table_dict = {}
        CASHO_dict = {}
        CASHI_dict = {}
        CASHF_dict = {}

        checkpoints = ["營業活動之現金流量－間接法", "投資活動之現金流量", "籌資活動之現金流量", "匯率變動對現金及約當現金之影響"]
        main_cash_flow_names = [
            "營業活動之淨現金流入（流出）", "投資活動之淨現金流入（流出）", "籌資活動之淨現金流入（流出）", "其他"
        ] # 主要的比例對象
        partial_cash_flow_dicts = [CASHO_dict, CASHI_dict, CASHF_dict, dict()] 

        boundary = len(main_cash_flow_names) - 1
        
        for data in fetched_data:
            year, season, cash_flow = data['year'], data['season'], data['cash_flow']

            time_index = f"{year}Q{season}"
            table_dict[time_index] = cash_flow

            # 處理sub part
            main_cash_flow_name = ""
            partial_cash_flow = {}
            next_checkpoint = 0

            temp_dict = {}

            for index_name, cash_flow_value in cash_flow.items():
                if (next_checkpoint < boundary
                        and index_name == checkpoints[next_checkpoint]): # 找到了主要的變動點
                    main_cash_flow_name = main_cash_flow_names[next_checkpoint]
                    partial_cash_flow = partial_cash_flow_dicts[next_checkpoint]
                    partial_cash_flow[time_index] = {}
                    next_checkpoint += 1

                if main_cash_flow_name: # 有取得cash flow name再進行接下來的計算percentage
                    if (isinstance(cash_flow_value, dict)):
                        value = cash_flow_value.get('value', None) 
                    else:
                        value = cash_flow_value

                    # 處理cashflow percentage部分(取2位 + 接%)
                    main_value = cash_flow.get(main_cash_flow_name, None)
                    if (isinstance(main_value, dict)):
                        main_value = main_value.get('value', None)
                    else:
                        pass

                    try:
                        ratio = np.round(
                            (value / main_value) * 100, 2
                        )
                        ratio = f"{ratio}%"
                    except:
                        ratio = None
                    
                    value = StatsProcessor.cal_non_percentage(value, postfix="千元")
                    temp_dict[index_name] = {
                        "value" : value,
                        "percentage": ratio
                    }
                    partial_cash_flow[time_index][index_name] = temp_dict[index_name]

            table_dict[time_index] = temp_dict

        stats_df = pd.DataFrame(table_dict)

        CASHO_df = pd.DataFrame(CASHO_dict)
        CASHI_df = pd.DataFrame(CASHI_dict)
        CASHF_df = pd.DataFrame(CASHF_dict)

        return stats_df, CASHO_df, CASHI_df, CASHF_df
    
    def _process_twse_to_tej_format(self, fetched_data):
        """
        new_df 迎合 TEJ格式, 用於 report_generator
        """
        table_dict = {}
        for data in fetched_data:
            year, season, cash_flow = data['year'], data['season'], data['cash_flow']
            time_index = f"{year}Q{season}"

            new_cash_flow = self.flatten_dict(
                cash_flow,
                target_keys=["value", "percentage"]
            )

            table_dict[time_index] = new_cash_flow
        
        stats_df = pd.DataFrame.from_dict(table_dict)
        return stats_df
    
    def _process_us_format(self, fetched_data):
        """
        主要用於report generator
        """
        table_dict = {}
        for data in fetched_data:
            year, season, cash_flow = data['year'], data['season'], data['cash_flow']
            time_index = f"{year}Q{season}"

            table_dict[time_index] = cash_flow
        
        stats_df = pd.DataFrame.from_dict(table_dict)
        return stats_df
