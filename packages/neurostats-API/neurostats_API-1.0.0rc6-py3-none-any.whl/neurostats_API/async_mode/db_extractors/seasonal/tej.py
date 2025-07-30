from .base import AsyncBaseSeasonalDBExtractor
from datetime import datetime
from neurostats_API.utils import NotSupportedError
from pymongo import ASCENDING


class AsyncTEJSeasonalDBExtractor(AsyncBaseSeasonalDBExtractor):

    def __init__(self, ticker, client, fetch_type='Q'):
        super().__init__(ticker, client)

        self.fetch_type = fetch_type

        if (self.zone != 'tw'):
            raise NotSupportedError(None)

    async def query_data(self, start_date=None, end_date=None):
        if (start_date is None):
            start_date = "1991-01-01"
        if (end_date is None):
            end_date = self._get_today()

        query, projection, sort = self._prepare_query(start_date, end_date)

        cursor = self.collection.find(query, projection).sort(sort)

        fetched_data = [data async for data in cursor]

        return fetched_data

    def _prepare_query(self, start_date, end_date):
        start_date = self._transform_date(start_date)
        end_date = self._transform_date(end_date)

        query = {
            "ticker": self.ticker,
            "date": {
                "$gte": start_date,
                "$lte": end_date
            }
        }

        projection = {
            "_id": 0,
            "year": 1,
            "season": 1,
            self.fetch_type: 1,
        }

        sorting = [("year", ASCENDING), ("season", ASCENDING)]

        return query, projection, sorting

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


class AsyncTEJFinanceStatementDBExtractor(AsyncTEJSeasonalDBExtractor):

    def __init__(self, ticker, mongo_uri, fetch_type='Q'):
        super().__init__(ticker, mongo_uri, fetch_type=fetch_type)

    def _get_collection_map(self):
        return {
            'tw': "TEJ_finance_statement"
        }
    
class AsyncTEJSelfSettlementDBExtractor(AsyncTEJSeasonalDBExtractor):
    def __init__(self, ticker, mongo_uri, fetch_type='Q'):
        super().__init__(ticker, mongo_uri, fetch_type=fetch_type)

    def _get_collection_map(self):
        return {
            'tw': "TEJ_self_settlement"
        }