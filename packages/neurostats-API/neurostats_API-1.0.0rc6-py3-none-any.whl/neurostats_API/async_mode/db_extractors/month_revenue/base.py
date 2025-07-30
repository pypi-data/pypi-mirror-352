from ..base import BaseDBExtractor
from datetime import datetime
import json
import pandas as pd
from pymongo import ASCENDING, DESCENDING
from neurostats_API.async_mode.db import TWSEDBClient, USDBClient
from neurostats_API.utils import StatsDateTime, StatsProcessor, NotSupportedError
import yaml


class AsyncBaseMonthlyDBExtractor(BaseDBExtractor):

    def __init__(self, ticker, client):
        super().__init__(ticker, client)

        self.collection_name_map = None
        self.collection_name = self._get_collection_name()

        if (self.collection_name is None):
             raise NotSupportedError(
                    f"{self.__class__.__name__} only supports {list(self.collection_name_map.keys())}, got {self.zone} with ticker = \"{self.ticker}\""
                )

        self.collection = self.db_client.get_collection(self.collection_name)

    async def query_data(
        self, start_date=None, end_date=None, get_latest=False
    ):
        if (start_date is None):
            start_date = "1991-01-01"
        if (end_date is None):
            end_date = self._get_today()

        start_year, start_month = self._get_year_and_month(date=start_date)
        end_year, end_month = self._get_year_and_month(date=end_date)

        query, projection, sort = self._prepare_query(
            start_year, start_month, end_year, end_month, get_latest
        )
        cursor = self.collection.find(query, projection).sort(sort)
        if (get_latest):
            cursor = cursor.limit(1)

        fetched_data = [data async for data in cursor]

        return fetched_data

    def _get_collection_name(self):
        self.collection_name_map = {
            "tw": "twse_monthly_revenue",
        }

        collection_name = self.collection_name_map.get(self.zone, None)

        return collection_name

    def _prepare_query(
        self,
        start_year=None,
        start_month=None,
        end_year=None,
        end_month=None,
        get_latest=False
    ):

        query = {"ticker": self.ticker}

        query = self._update_query_with_year_month(
            query, start_year, start_month, end_year, end_month
        )

        projection = {
            "_id": 0,
        }

        if (get_latest):
            sort = [("year", DESCENDING), ("month", DESCENDING)]
        else:
            sort = [("year", ASCENDING), ("month", ASCENDING)]

        return query, projection, sort

    def _get_year_and_month(self, date):
        if (isinstance(date, str)):
            date = datetime.strptime(date, "%Y-%m-%d")

        year = date.year
        month = date.month

        return year, month

    def _update_query_with_year_month(
        self, query, start_year, start_month, end_year, end_month
    ):
        if all(v is not None for v in [start_year, start_month]):
            # 大於start_year條件
            query.update(
                {
                    "$or": [
                        {
                            "year": {
                                "$gt": start_year
                            }
                        },
                        {
                            "year": start_year,
                            "month": {
                                "$gte": start_month
                            }
                        },
                    ]
                }
            )

        if all(v is not None for v in [end_year, end_month]):
            # 小於end_year條件
            query.update(
                {
                    "$and":
                    query.get("$and", []) + [
                        {
                            "$or": [
                                {
                                    "year": {
                                        "$lt": end_year
                                    }
                                },
                                {
                                    "year": end_year,
                                    "month": {
                                        "$lte": end_month
                                    }
                                },
                            ]
                        }
                    ]
                }
            )

        return query
