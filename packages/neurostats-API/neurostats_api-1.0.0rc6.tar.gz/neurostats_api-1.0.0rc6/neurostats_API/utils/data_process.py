from importlib.resources import files
import json
import numpy as np
import pandas as pd
import yaml

target_metric_dict = {
    'value': ['value'],
    'value_and_percentage': ['value', 'percentage'],
    'percentage': ['percentage'],
    'grand_total': ['grand_total'],
    'grand_total_values': ['grand_total', 'grand_total_percentage'],
    'grand_total_percentage': ['grand_total_percentage'],
    'growth': [f'YoY_{i}' for i in [1, 3, 5, 10]],
    'grand_total_growth': [f"grand_total_YoY_{i}" for i in [1, 3, 5, 10]]
}


class StatsProcessor:
    """
    1. 讀檔: txt / yaml
    2. 將巢狀dictionary / DataFrame扁平化
    """

    @classmethod
    def load_txt(cls, filename, json_load=True):
        txt_path = files('neurostats_API.config').joinpath(filename)
        with open(txt_path, 'r', encoding='utf-8') as f:
            data = json.load(f) if (json_load) else f.read()
        return data

    @classmethod
    def load_yaml(cls, filename):
        yaml_path = files('neurostats_API.config').joinpath(filename)
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        return data
    
    @classmethod
    def load_json(cls, filename):
        json_path = files('neurostats_API.config').joinpath(filename)
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return data

    @classmethod
    def expand_value_percentage(cls, dataframe):

        expanded_columns = {}
        for col in dataframe.columns:
            # Use json_normalize to split 'value' and 'percentage'
            expanded_df = pd.json_normalize(
                dataframe[col]).add_prefix(f"{col}_")
            expanded_df.index = dataframe.index
            # Append the expanded columns to the new DataFrame
            expanded_columns[col] = expanded_df

        try:
            expanded_df = pd.concat(expanded_columns.values(), axis=1)
        except ValueError: # No values to concat
            expanded_df = pd.DataFrame(columns = list(expanded_columns.keys()))

        return expanded_df
    
    @classmethod
    def slice_old_table(
        cls,
        total_table,
        target_index,
    ):
        """
        對舊格式的轉換
        對只有單層column的table，切出想要的index
        """

        if (target_index):
            target_index = target_index.split()
            return total_table.loc[target_index, :]
        else:
            return total_table

    @classmethod
    def slice_table(
            cls,
            total_table,
            mode='value',
            target_index=None,  # None or Str， 要特別抓哪個index
    ):
        """
        total_table: column應為 <時間>_<季>
        """
        try:
            target_metrics = target_metric_dict[mode]
        except KeyError as e:
            raise ValueError(f"mode Error: Get mode should be {list(target_metric_dict.keys())} but get {mode}")

        if (target_index):
            target_index = [index_name.strip() for index_name in target_index.split()]
            desired_order = []
            for index_name in target_index:
                desired_order += [f"{index_name}_{metric_name}" for metric_name in target_metrics]
            sliced_table = total_table.loc[:, desired_order]

            return sliced_table.T

        else:
            target_columns = total_table.columns.str.endswith(tuple(target_metrics))
            return total_table.loc[:, target_columns]

    @classmethod
    def slice_multi_col_table(
            cls,
            total_table,
            mode='value',
            target_index=None,  # None or Str， 要特別抓哪個index
    ):
        """
        對Multicolumn的dataframe切出目標的index
        """
        try:
            target_metrics = target_metric_dict[mode]
        except KeyError as e:
            return f"mode Error: Get mode should be {list(target_metric_dict.keys())} but get {mode}"

        times = total_table.columns.get_level_values(0).unique()
        desired_order = [(time, value_name) for time in times
                         for value_name in target_metrics]

        if (target_index):
            target_index = target_index.split()
            try:
                sliced_table = total_table.loc[
                    target_index,
                    pd.IndexSlice[:, target_metrics]][desired_order].T

            except Exception as e:  # 沒辦法完整取得表格
                # 先設立空表格
                empty_index = pd.Index(desired_order)
                empty_columns = pd.Index(target_index)
                sliced_table = pd.DataFrame(index=empty_index,
                                            columns=empty_columns)

                try:
                    # 提取有效的部分資料
                    partial_table = total_table.loc[
                        total_table.index.intersection(target_index),
                        pd.IndexSlice[:, target_metrics]
                    ]

                    # 遍歷 partial_table 的索引和值，手動填入 sliced_table
                    for row_index in partial_table.index:
                        for col_index in partial_table.columns:
                            if col_index in desired_order and row_index in target_index:
                                sliced_table.loc[col_index, row_index] = partial_table.loc[row_index, col_index]

                    # 確保 `sliced_table` 的排序符合 `desired_order`
                    sliced_table = sliced_table.reindex(index=desired_order, columns=target_index)
                except Exception as sub_e:
                    pass

            if (mode == 'value_and_percentage'):  # 因應balance_sheet 頁面的格式
                return_table = sliced_table.T
                return_table.columns = [
                    "_".join(flatten_indexs)
                    for flatten_indexs in return_table.columns.to_flat_index()
                ]
                return return_table

            sliced_table = sliced_table.reset_index()
            sliced_table = sliced_table.pivot(index='level_1',
                                              columns='level_0',
                                              values=target_index).sort_index(
                                                  axis=1,
                                                  level=1,
                                                  ascending=False)

            sliced_table.columns = sliced_table.columns.get_level_values(1)
            sliced_table.columns.name = None
            sliced_table.index.name = None

            return sliced_table.reindex(target_metrics)

        else:
            return_table = total_table.loc[:, pd.IndexSlice[:,
                                                            target_metrics]][
                                                                desired_order]
            return_table.columns = [
                "_".join(flatten_indexs)
                for flatten_indexs in return_table.columns.to_flat_index()
            ]
            return return_table

    @classmethod
    def cal_percentage(cls, value, postfix="%"):
        if (isinstance(value, (float, int))):
            if (np.isnan(value)):
                return None
            value = np.round(value * 100, 2).item()
            if (value != value): # nan值發生
                return None
            value = f"{value:.2f}{postfix}"

            return value

        else:
            return value

    @classmethod
    def cal_non_percentage(cls, value, to_str=False, postfix="元"):
        if (isinstance(value, (float, int))):
            if (np.isnan(value)):
                return None
            value = np.round(value, 2).item()
            if (postfix == "千元"):
                value = value * 1000
                try:
                    value = int(value)
                except Exception as e:
                    pass

                postfix = "元"

            if (to_str):
                if (isinstance(value, float)):
                    try:
                        value = f"{value:.2f}{postfix}"
                    except Exception as e:
                        value = f"{value}{postfix}"
                    return value
                elif (isinstance(value, int)):
                    value = f"{value}{postfix}"
                    return value

            else:
                return value

        else:
            return value

    @classmethod
    def cal_round_int(cls, value):
        """
        將數值取到個位數後轉為int
        """
        if (isinstance(value, (int, float))):
            return int(np.round(value).item())
        else:
            return value
    
    @classmethod
    def list_of_dict_to_dict(
        cls,
        data_list: list,
        key: str = "",
        keys: list = [],
        delimeter: str = "_",
        data_key: str = "Q"
    ):
        """
        TEJ DB 用
        List[Dict] -> Dict[Dict]
        input:
        data_list(List):
            [
                { "data":
                    {
                        "year": 2021...
                        "season": 1,
                        "Q": {}...
                        
                    }
                }
            ]
        
        key(str): 選擇哪一個key作為轉化後的index
        delimeter(str): 多個key時要用甚麼分隔
        return: 
        {
            "2021" : {# Q下的資料} ...
        }

        or  (keys = ['year', 'season'])
        {
            "2021Q2" : {}
        }
        """
        assert (key or keys), "func list_of_dict_to_dict must have argument \"key\" or \"keys\""

        return_dict = {}
        if (key):
            keys = [key]
        for data in data_list:

            pop_keys = []

            for key in keys:
                assert (key in data.keys())
                pop_keys.append(str(data.pop(key)))

            pop_key = delimeter.join(pop_keys)
            target_data = data.get(data_key, data)

            return_dict[pop_key] = target_data
        
        return return_dict
    
    @classmethod
    def process_str_to_float(cls, value):
        if isinstance(value, str) and "%" in value:
            value = value.replace("%", "")
        try:
            return float(value)
        except (ValueError, TypeError) as e:
            return None