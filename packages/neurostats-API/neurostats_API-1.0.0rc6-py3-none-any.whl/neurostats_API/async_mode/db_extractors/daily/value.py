from .base import BaseDailyTechDBExtractor
from pymongo import ASCENDING, DESCENDING
from neurostats_API.utils import NotSupportedError

class AsyncDailyValueDBExtractor(BaseDailyTechDBExtractor):

    def __init__(self, ticker, client, fetch_type='D'):
        """
        fetch_type: 
        'D': daily
        'Y': yearly
        """
        self.fetch_type = fetch_type
        super().__init__(ticker, client)
        
    def _get_collection_name(self):
        self.collection_name_map = {
            "tw": {
                "D":"twse_daily_share_price",
                "Y": "twse_yearly_value"
            }
        }
        collection_map = self.collection_name_map.get(self.zone)
        if (collection_map is None):
            raise NotSupportedError(f"AsyncDailyValueDBExtractor only supports {self.collection_name_map.keys}, but get {self.zone}")
        collection_name = collection_map.get(self.fetch_type)
        if (collection_name is None):
            raise ValueError(f"AsyncDailyValueDBExtractor: Invalid fetch type : {self.fetch_type}")
        return collection_name
    
    def _prepare_query(self, start_date = None, end_date = None, get_latest = False):
        query_fn_map = {
            'D': super()._prepare_query,
            'Y': self._prepare_annual_query
        }

        query_fn = query_fn_map.get(self.fetch_type)
        query, projection, sorting = query_fn(start_date=start_date, end_date=end_date, get_latest=get_latest)

        projection.update(
            {   
                "date": 1,
                "year": 1,
                "close": 1,
                "P_E": 1,
                "P_B": 1,
                "P_FCF": 1,
                "P_S": 1,
                "EV_S": 1,
                "EV_OPI": 1,
                "EV_EBIT": 1,
                "EV_EBITDA": 1
            }
        )

        return query, projection, sorting


    def _prepare_annual_query(self, start_date, end_date, get_latest = False):
        start_date = self._transform_date(start_date)
        end_date = self._transform_date(end_date)

        start_year = start_date.year - 1911
        end_year = end_date.year - 1911
        query = {
            "ticker": self.ticker,
            "year": {
                "$gte": start_year,
                "$lte": end_year
            }
        }

        projection = {
            "_id": 0,
        }

        if (get_latest):
            sort = [("year", DESCENDING)]
        else:
            sort = [("year", ASCENDING)]

        return query, projection, sort


class AsyncTEJDailyValueDBExtractor(BaseDailyTechDBExtractor):

    def __init__(self, ticker, mongo_uri):
        super().__init__(ticker, mongo_uri)

    def _get_collection_name(self):
        self.collection_name_map = {"tw": "TEJ_share_price"}

        return self.collection_name_map.get(self.zone, None)
