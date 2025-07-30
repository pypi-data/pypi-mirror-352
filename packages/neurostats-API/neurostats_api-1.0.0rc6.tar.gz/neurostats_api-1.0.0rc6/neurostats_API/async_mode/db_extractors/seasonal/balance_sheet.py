from .base import AsyncBaseSeasonalDBExtractor
from datetime import datetime
import json
import pandas as pd
from pymongo import ASCENDING, DESCENDING
from neurostats_API.async_mode.db import TWSEDBClient, USDBClient
from neurostats_API.utils import StatsDateTime, StatsProcessor
import yaml

class AsyncBalanceSheetExtractor(AsyncBaseSeasonalDBExtractor):

    def __init__(self, ticker, client):

        super().__init__(ticker, client)
        
        self.column_name_map = {
            'tw': "balance_sheet",
            'us': "balance_sheet"
        }