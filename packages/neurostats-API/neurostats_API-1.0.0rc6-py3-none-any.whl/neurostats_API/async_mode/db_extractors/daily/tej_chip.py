from .base import BaseDailyTechDBExtractor
from datetime import datetime
from pymongo import ASCENDING, DESCENDING


class AsyncTEJDailyChipDBExtractor(BaseDailyTechDBExtractor):

    def __init__(self, ticker, client):
        super().__init__(ticker, client)

    def _get_collection_name(self):
        self.collection_name_map = {"tw": "TEJ_chip"}

        return self.collection_name_map.get(self.zone, None)
