from .base import BaseDailyTechDBExtractor
from datetime import datetime
from pymongo import ASCENDING, DESCENDING
from neurostats_API.utils import NotSupportedError

class AsyncTWSEChipDBExtractor(BaseDailyTechDBExtractor):

    def __init__(self, ticker, client, fetch_type = 'I'):

        """
        擷取台股每日籌碼資料。

        fetch_type:
            - 'I' (INSTITUTION): 法人買賣
            - 'M' (MARGIN): 融資融券餘額變化
            - 'S' (SECURITY_LENDING): 借券債券

        """
        super().__init__(ticker, client)

        column_name_map = {
            'tw': {
                "I" : "institution_trading",
                "M" : "margin_trading",
                "S" : "security_lending"
            },
        }
        self.target_column = column_name_map[self.zone][fetch_type]

    def _get_collection_name(self):
        self.collection_name_map = {"tw": "twse_chip"}
        collection_name = self.collection_name_map.get(self.zone, None)
        return collection_name
    
    def _prepare_query(self, start_date=None, end_date=None, get_latest = False):
        query, projection, sort = super()._prepare_query(start_date, end_date, get_latest)
        query.update(
            {
                self.target_column: {"$exists" : True}
            }
        )
        projection.update(
            {
                'date': 1,
                self.target_column: 1
            }
        )

        return query, projection, sort
