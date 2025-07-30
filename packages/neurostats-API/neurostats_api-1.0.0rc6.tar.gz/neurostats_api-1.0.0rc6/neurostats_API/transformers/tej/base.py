from ..base import BaseTransformer
from neurostats_API.utils import StatsProcessor, YoY_Calculator
import pandas as pd


class BaseTEJTransformer(BaseTransformer):

    def __init__(self, ticker, company_name, zone):
        super().__init__(ticker, company_name, zone)
        self.thousand_index_list = [] # 在子類別定義
        self.percent_index_list = [] # 在子類別定義
        self.skip_index = [] # 在子類別定義

    def _process_data_to_tej_format(self, fetched_data, target_key):
        table_dict = {}
        for data in fetched_data:
            year, season, target_dict = data['year'], data['season'], data[
                target_key]
            time_index = f"{year}Q{season}"
            table_dict[time_index] = target_dict

        return table_dict

    def _transform_value(self, data_dict):
        """
        處理千元, %等單位
        """

        data_df = pd.DataFrame.from_dict(data_dict)
        for category, postfix in [(self.thousand_index_list, "千元"),
                                  (self.percent_index_list, "%")]:
            process_list = list(set(data_df.index) & set(category))

            if postfix == "%":
                data_df = data_df.T
                data_df[process_list] = data_df[process_list].map(
                    lambda x: f"{x}%"
                )    # if (not np.isnan(x)) else None)
                data_df = data_df.T
            else:
                data_df.loc[process_list] = data_df.loc[process_list].map(
                    lambda x: StatsProcessor.
                    cal_non_percentage(x, postfix=postfix)
                )
        return data_df.to_dict()

    def _calculate_growth(self, this_value, last_value, delta):
        try:
            return YoY_Calculator.cal_growth(
                this_value, last_value, delta
            ) * 100
        except Exception:
            return None

    def _get_QoQ_data(self, data, use_cal=False):

        if (use_cal):
            new_dict = {}
            for time_index, data_dict in data.items():
                year, season = time_index.split('Q')
                year, season = int(year), int(season)
                last_year, last_season = (year - 1, 4) if season == 1 else (
                    year, season - 1
                )

                pre_data_dict = data.get(f"{last_year}Q{last_season}", {})

                new_dict[time_index] = self._calculate_QoQ_dict(
                    data_dict, pre_data_dict, delta=1
                )
            data = pd.DataFrame.from_dict(new_dict)
            return data

        else:
            data = pd.DataFrame.from_dict(data)
            return data

    def _get_YoY_data(self, data, target_season, use_cal=False):
        if (use_cal):
            new_dict = {}
            year_shifts = [1, 3, 5, 10]

            for time_index, data_dict in data.items():
                year, season = time_index.split('Q')
                year, season = int(year), int(season)

                target_items = []
                for shift in year_shifts:
                    last_year, last_season = (year - shift, season)

                    pre_data_dict = data.get(f"{last_year}Q{last_season}", {})

                    target_items.append(pre_data_dict)

                new_dict[time_index] = self._calculate_YoY_dict(
                    data_dict, target_items, year_shifts = year_shifts
                )

            data = pd.DataFrame.from_dict(new_dict)
            target_season_col = data.columns.str.endswith(f"{target_season}")
            data = data.loc[:, target_season_col]
        
        else:
            data = pd.DataFrame.from_dict(data)
            target_season_col = data.columns.str.endswith(f"{target_season}")
            data = data.loc[:, target_season_col]

        return data

    def _calculate_QoQ_dict(self, this_dict, last_dict, delta):
        temp_dict = {}
        for key in list(this_dict.keys()):
            if key in self.skip_index:
                temp_dict[f"{key}_value"] = this_dict[key]
                continue
            this_value = self._process_value(this_dict[key])

            last_value = last_dict.get(key, None)
            last_value = self._process_value(last_value)

            growth = self._calculate_growth(
                this_value, last_value, delta=delta
            ) if last_value is not None else None

            temp_dict[f"{key}_value"] = this_dict[key]
            temp_dict[f"{key}_growth"] = (f"{growth:.2f}%" if growth else None)

        return temp_dict
    
    def _calculate_YoY_dict(self, this_dict, last_dicts, year_shifts):
        temp_dict = {}
        for last_dict, delta in zip(last_dicts, year_shifts):
            for key in list(this_dict.keys()):
                if key in self.skip_index:
                    temp_dict[f"{key}_value"] = this_dict[key]
                    continue
                this_value = self._process_value(this_dict[key])

                last_value = last_dict.get(key, None)
                last_value = self._process_value(last_value)
                
                growth = self._calculate_growth(
                    this_value, last_value, delta=delta
                ) if last_value is not None else None

                temp_dict[f"{key}_value"] = this_dict[key]
                temp_dict[f"{key}_YoY_{delta}"] = (f"{growth:.2f}%" if growth else None)

        return temp_dict
