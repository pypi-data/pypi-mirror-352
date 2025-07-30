from ..base import BaseDBExtractor
from datetime import datetime
from neurostats_API.utils import NotSupportedError
from pymongo import ASCENDING, DESCENDING


class BaseDailyTechDBExtractor(BaseDBExtractor):

    def __init__(self, ticker, client):
        super().__init__(ticker, client)

        self.collection_name_map = None
        self.collection_name = self._get_collection_name()
        
        if (self.collection_name is None):
             raise NotSupportedError(
                    f"{self.__class__.__name__} only supports {list(self.collection_name_map.keys())}, got {self.zone} with ticker = \"{self.ticker}\""
                )

        self.collection = self.db_client.get_collection(self.collection_name)

    async def query_data(self, start_date=None, end_date=None, get_latest = False):
        if (self.collection is None):
            return []

        if (start_date is None):
            start_date = "1991-01-01"
        if (end_date is None):
            end_date = self._get_today()

        query, projection, sort = self._prepare_query(
            start_date=start_date, end_date=end_date, get_latest=get_latest
        )

        if (get_latest):
            cursor = self.collection.find(query, projection).sort(sort).limit(1)
        else:
            cursor = self.collection.find(query, projection).sort(sort)

        fetched_data = [data async for data in cursor]

        return fetched_data

    def _get_collection_name(self):
        self.collection_name_map = {"tw": "twse_daily_share_price", "us": "us_technical"}
        collection_name = self.collection_name_map.get(self.zone, None)

        return collection_name 

    def _prepare_query(self, start_date=None, end_date=None, get_latest = False):
        query = {"ticker": self.ticker}

        query = self._update_query_with_date(query, start_date, end_date)

        projection = {
            "_id": 0,
        }

        if (get_latest):
            sort = [("date", DESCENDING)]
        else:
            sort = [("date", ASCENDING)]

        return query, projection, sort

    def _update_query_with_date(self, query, start_date, end_date):
        start_date = self._transform_date(start_date)
        end_date = self._transform_date(end_date)

        date_range = {"$gte": start_date, "$lte": end_date}

        query.update({"date": date_range})

        return query

    def _transform_date(self, date):
        if (isinstance(date, str)):
            try:
                return datetime.strptime(date, "%Y-%m-%d")
            except Exception as e:
                raise ValueError(
                    "date string format imcompatible, should be \"YYYY-MM-DD\""
                )
        elif (isinstance(date, datetime)):
            return date
        else:
            raise ValueError(
                "date type imcompatible, should be string(\"YYYY-MM-DD\") or datetime.datetime"
            )