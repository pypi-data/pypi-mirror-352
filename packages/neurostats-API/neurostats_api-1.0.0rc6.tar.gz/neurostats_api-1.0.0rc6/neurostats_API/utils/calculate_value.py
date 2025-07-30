from .data_process import StatsProcessor
import numpy as np
class YoY_Calculator:
    def __init__(self):
        pass

    @classmethod
    def cal_growth(cls, target_value: float, past_value: float, delta: int):
        """
        計算成長率以及年化成長率
        target_value: float，這個時間的數值
        past_value: float，過去的這個時間數值
        delta: int，代表隔了幾年/季 delta > 1 時改以年化成長率計算
        """
        try:
            if (delta > 1):
                YoY = ((target_value / past_value)**(1 / delta)) - 1

            else:
                YoY = ((target_value - past_value) / past_value)

        except Exception as e:
            return None

        if (isinstance(YoY, complex)): # 年化成長率有複數問題
            return None
        
        if YoY != YoY:  # 確認是否為nan (Python 中 nan不等於自己)
            return None

        return YoY
    @classmethod
    def calculate_growth(cls, this_value, last_value, delta):
        try:
            return YoY_Calculator.cal_growth(
                this_value, last_value, delta
            ) * 100
        except Exception:
            return None

    @classmethod
    def cal_YoY(
        cls, data_dict: dict
    ):
        year_shifts = [1, 3, 5, 10]
        return_dict = {}

        for time_index in data_dict.keys():
            year, season = map(int, time_index.split("Q"))
            
            year_data = data_dict.get(f"{year}Q{season}", {}).copy()
            if not year_data:
                continue

            for key, data in list(year_data.items()):
                if key in ["year", "season"]:
                    continue
                
                if (isinstance(data, dict)):
                    temp_dict = data
                    value = data.get("value", None)
                else:
                    temp_dict = {"value": data}
                    value = data

                this_value = StatsProcessor.process_str_to_float(value)
                
                for shift in year_shifts:
                    past_value = data_dict.get(f"{year - shift}Q{season}", {}).get(key, {})
                    if (isinstance(past_value, dict)):
                        past_value = past_value.get('value', None)
                    past_value = StatsProcessor.process_str_to_float(
                        past_value
                    )

                    growth = cls.calculate_growth(this_value, past_value, shift) if past_value else None

                    temp_dict[
                        f"YoY_{shift}"
                    ] = f"{growth:.2f}%" if growth else None

                year_data[key] = temp_dict
            return_dict[f"{year}Q{season}"] = year_data
        return return_dict
    @classmethod
    def cal_QoQ(cls, data_dict):
        return_dict = {}

        for time_index, this_data in data_dict.items():
            year, season = map(int, time_index.split("Q"))
            last_year, last_season = (
                year - 1, 4
            ) if season == 1 else (year, season - 1)

            for key in list(this_data.keys()):
                if key == "season":
                    continue

                value = this_data.get(key, None)

                if (isinstance(value, dict)):
                    temp_dict = value
                    this_value = value.get("value", None)
                else:
                    temp_dict = {"value": value}
                    this_value = value
                
                this_value = StatsProcessor.process_str_to_float(this_value)
                
                last_value = data_dict.get(
                    f"{last_year}Q{last_season}",{}
                ).get(key, {})

                if (isinstance(last_value, dict)):
                    last_value = last_value.get("value", None)

                last_value = StatsProcessor.process_str_to_float(last_value)
                growth = cls.calculate_growth(
                    this_value, last_value, 1
                ) if last_value is not None else None
                temp_dict['growth'] = (f"{growth:.2f}%" if growth else None)

                this_data[key] = temp_dict

            return_dict[time_index] = this_data

        return return_dict
