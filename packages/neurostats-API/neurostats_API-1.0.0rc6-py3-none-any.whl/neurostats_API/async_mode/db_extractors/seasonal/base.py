from ..base import BaseDBExtractor
from datetime import datetime
import json
import pandas as pd
from pymongo import ASCENDING, DESCENDING
from neurostats_API.async_mode.db import TWSEDBClient, USDBClient
from neurostats_API.utils import StatsDateTime, StatsProcessor, NotSupportedError
import yaml


class AsyncBaseSeasonalDBExtractor(BaseDBExtractor):

    def __init__(self, ticker, client):
        super().__init__(ticker, client)

        self.collection_name_map = self._get_collection_map()
        self.collection_name = self._get_collection_name()
        if (self.collection_name is None):
            raise NotSupportedError(
                f"{self.__class__.__name__} only supports {list(self.collection_name_map.keys())}, got {self.zone} with ticker = \"{self.ticker}\""
            )
        self.collection = self.db_client.get_collection(self.collection_name)

        self.column_name_map = None

    async def query_data(
        self,
        start_date=None,
        end_date=None,
        get_latest=False    # 決定是否只取得最新一筆資料
    ):
        if (start_date is None):
            start_date = "1991-01-01"
        if (end_date is None):
            end_date = self._get_today()

        start_year, start_season = self._get_year_and_season(date=start_date)
        end_year, end_season = self._get_year_and_season(date=end_date)

        query, projection, sort = self._prepare_query(
            start_year, start_season, end_year, end_season, get_latest
        )
        cursor = self.collection.find(query, projection).sort(sort)

        if (get_latest):
            cursor = cursor.limit(1)

        fetched_data = [data async for data in cursor]

        return fetched_data

    def _get_collection_name(self):

        return self.collection_name_map.get(self.zone, None)

    def _get_collection_map(self):
        return {"tw": "twse_seasonal_report", "us": "us_fundamentals"}

    def _prepare_query(
        self,
        start_year=None,
        start_season=None,
        end_year=None,
        end_season=None,
        get_latest=False
    ):
        chart_name = self.column_name_map.get(self.get_zone(), None)

        query = {
            "ticker": self.ticker,
            chart_name: {"$exists": True}
        }

        query = self._update_query_with_year_season(
            query, start_year, start_season, end_year, end_season
        )

        projection = {
            "_id": 0,
            "ticker": 1,
            "year": 1,
            "season": 1,
            chart_name: 1,
        }

        if (get_latest):
            sort = [("year", DESCENDING), ("season", DESCENDING)]
        else:
            sort = [("year", ASCENDING), ("season", ASCENDING)]

        return query, projection, sort

    def _get_year_and_season(self, date):
        if (isinstance(date, str)):
            date = datetime.strptime(date, "%Y-%m-%d")

        year = date.year
        month = date.month

        season = (month - 1) // 3 + 1

        return year, season

    def _update_query_with_year_season(
        self, query, start_year, start_season, end_year, end_season
    ):
        if all(v is not None for v in [start_year, start_season]):
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
                            "season": {
                                "$gte": start_season
                            }
                        },
                    ]
                }
            )

        if all(v is not None for v in [end_year, end_season]):
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
                                    "season": {
                                        "$lte": end_season
                                    }
                                },
                            ]
                        }
                    ]
                }
            )

        return query
