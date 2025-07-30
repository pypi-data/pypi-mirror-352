from .base import AsyncBaseFetcher
from datetime import datetime
from ..db_extractors import (
    AsyncYFDailyTechDBExtractor, AsyncTEJDailyTechDBExtractor
)
from neurostats_API.async_mode.factory import get_extractor
from neurostats_API.transformers import DailyTechTransformer
from neurostats_API.utils import NotSupportedError
import pandas as pd
import yfinance as yf


class AsyncTechFetcher(AsyncBaseFetcher):

    def __init__(self, ticker, client):
        self.ticker = ticker
        self.transformer_map = {
            "tw": DailyTechTransformer,
            "us": DailyTechTransformer
        }
        try:
            self.yf_db_extractor = get_extractor("YF_tech", ticker, client)

            self.tej_db_extractor = None
            if (self.yf_db_extractor.get_zone() == 'tw'):
                self.tej_db_extractor = get_extractor("TEJ_tech", ticker, client)

            self.company_name = self.yf_db_extractor.get_company_name()
            self.zone = self.yf_db_extractor.get_zone()

            self.required_cols = [
                'date', 'open', 'high', 'low', 'close', 'volume'
            ]

            transformer = self.get_transformer(self.zone)
            self.transformer = transformer(ticker, self.company_name, self.zone)

        except NotSupportedError as e:
            raise NotSupportedError(
                f"{self.__class__.__name__} only supports {list(self.transformer_map.keys())}, got {self.zone} with ticker = \"{self.ticker}\""
            ) from e

    async def query_data(self, start_date=None, end_date=None):
        if (start_date is None):
            start_date = datetime.strptime("1991-01-01", "%Y-%m-%d")
        if (end_date is None):
            end_date = datetime.today()

        fetched_data = await self._fetch_data(start_date, end_date)

        transformed_data = self.transformer.process_transform(fetched_data)

        return transformed_data

    async def get_daily(self, start_date=None, end_date=None):
        await self.query_data(start_date, end_date)

        return self.transformer.get_daily()

    async def get_weekly(self, start_date=None, end_date=None):
        await self.query_data(start_date, end_date)

        return self.transformer.get_weekly()

    async def get_monthly(self, start_date=None, end_date=None):
        await self.query_data(start_date, end_date)

        return self.transformer.get_monthly()

    async def get_quarterly(self, start_date=None, end_date=None):
        await self.query_data(start_date, end_date)

        return self.transformer.get_quarterly()

    async def get_yearly(self, start_date=None, end_date=None):
        await self.query_data(start_date, end_date)

        return self.transformer.get_yearly()

    async def _fetch_data(self, start_date, end_date):

        if (self.ticker in ['GSPC', 'IXIC', 'DJI', 'TWII']):
            full_tick = f'^{self.ticker}'
            df = self._conduct_yf_search(full_tick, start_date, end_date)

            return df[self.required_cols]

        else:
            search_fn_map = {
                'tw': self._conduct_tw_db_search,
                'us': self._conduct_us_db_search
            }
            search_fn = search_fn_map.get(self.zone)
            df = await search_fn(start_date, end_date)

            return df

    def _conduct_yf_search(self, ticker, start_date, end_date):
        yf_ticker = yf.Ticker(ticker)
        origin_df = yf_ticker.history(period="10y")

        if origin_df.empty:
            return origin_df

        origin_df = origin_df.reset_index()
        origin_df["Date"] = pd.to_datetime(origin_df["Date"])
        df = origin_df.rename(
            columns={
                "Date": "date",
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Volume": "volume"
            }
        )

        df = df.loc[(df['date'] >= start_date) & (df['date'] <= end_date)]
        return df

    async def _conduct_tw_db_search(self, start_date, end_date):
        search_fns = [
            self._conduct_tw_db_search_yf,
            self._conduct_tw_db_search_tej,
        ]

        sync_search_fns = [
            lambda s_date, e_date: self.
            _conduct_yf_search(f'{self.ticker}.tw', s_date, e_date),
            lambda s_date, e_date: self.
            _conduct_yf_search(f'{self.ticker}.two', s_date, e_date),
        ]

        for search_method in search_fns:
            try:
                fetched_data = await search_method(start_date, end_date)
                if not fetched_data.empty:
                    break
            except (KeyError, ValueError, TypeError) as e:
                print(e)
                continue
        else:    # 找不到資料
            for search_method in sync_search_fns:
                fetched_data = search_method(start_date, end_date)
                if not fetched_data.empty:
                    break
            else:
                return pd.DataFrame(self.required_cols)

        return fetched_data[self.required_cols]

    async def _conduct_tw_db_search_yf(self, start_date, end_date):
        """
        尋找從yf與twse爬下來的台股資料
        """
        fetched_data = await self.yf_db_extractor.query_data(
            start_date, end_date
        )

        if (fetched_data):
            df = pd.DataFrame(fetched_data)
            return df
        else:
            return None

    async def _conduct_tw_db_search_tej(self, start_date, end_date):
        """
        尋找從TEJ爬下來的台股資料
        """
        fetched_data = await self.tej_db_extractor.query_data(
            start_date, end_date
        )

        if (fetched_data):
            df = pd.DataFrame(fetched_data)
            df = df.rename(
                columns={
                    "open_d": "open",
                    "high_d": "high",
                    "low_d": "low",
                    "close_d": "close",
                    "vol": "volume"
                }
            )

            return df
        else:
            return None

    def _conduct_us_db_search(self, start_date, end_date):
        search_fns = [
            self.yf_db_extractor.query_data, lambda s_date, e_date: self.
            _conduct_yf_search(f"{self.ticker}", s_date, e_date)
        ]

        for search_method in search_fns:
            try:
                df = search_method(start_date, end_date)
                break
            except (KeyError, ValueError, TypeError):
                continue
        else:    # 回傳空df
            df = pd.DataFrame(columns=self.required_cols)

        return df
