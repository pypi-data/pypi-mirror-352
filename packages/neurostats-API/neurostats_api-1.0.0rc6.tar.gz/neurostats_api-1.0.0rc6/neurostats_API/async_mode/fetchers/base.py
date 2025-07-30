import abc
from datetime import datetime, timedelta, date
import json
import pandas as pd
from pymongo import MongoClient
import pytz
from typing import Union
from neurostats_API.utils import StatsDateTime, StatsProcessor, YoY_Calculator, NotSupportedError

class AsyncBaseFetcher(abc.ABC):
    """
    Fetcher目的: 真正給其他使用者的接口
    """
    def __init__(self):
        self.timezone = pytz.timezone("Asia/Taipei")
        self.target_metric_dict = {
            'value': ['value'],
            'value_and_percentage': ['value', 'percentage'],
            'percentage': ['percentage'],
            'grand_total': ['grand_total'],
            'grand_total_values': ['grand_total', 'grand_total_percentage'],
            'grand_total_percentage': ['grand_total_percentage'],
            'growth': [f'YoY_{i}' for i in [1, 3, 5, 10]],
            'grand_total_growth': [f"YoY_{i}" for i in [1, 3, 5, 10]]
        }
        self.transformer_map = None
    @ abc.abstractmethod
    async def query_data(self):
        """
        user使用的接口
        """
        return NotImplementedError()
    
    @staticmethod
    def str_to_datetime(self, date_str: str) -> StatsDateTime:
        date = self.timezone.localize(datetime.strptime(date_str, "%Y-%m-%d"))
        year, month, day = date.year, date.month, date.day
        season = (month - 1) // 3 + 1
        return StatsDateTime(date, year, month, day, season)
    
    def get_transformer(self, zone):
        transformer = self.transformer_map.get(zone)
        if (transformer is None):
            raise NotSupportedError(
                f"{self.__class__.__name__} get transformer failed: only supports {list(self.transformer_map.keys())}, got {zone}"
            )
        
        return transformer