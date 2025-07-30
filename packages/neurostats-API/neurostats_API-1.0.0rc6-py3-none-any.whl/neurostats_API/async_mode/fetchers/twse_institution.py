from .base import AsyncBaseFetcher
from datetime import datetime, timedelta
from ..db_extractors import (
    AsyncTWSEChipDBExtractor,
    AsyncYFDailyTechDBExtractor,
)
from neurostats_API.async_mode.factory import get_extractor
from neurostats_API.utils import NotSupportedError
from neurostats_API.transformers import TWSEChipTransformer


class AsyncTWSEInstitutionFetcher(AsyncBaseFetcher):

    def __init__(self, ticker, client):
        self.ticker = ticker
        self.transformer_map = {"tw": TWSEChipTransformer}
        try:
            self.extractor = get_extractor(
                "TWSE_chip", ticker, client, fetch_type='I'
            )
            self.daily_extractor = get_extractor("YF_tech", ticker, client)

            company_name = self.extractor.get_company_name()
            zone = self.extractor.get_zone()

            transformer = self.get_transformer(zone)
            self.transformer = transformer(ticker, company_name, zone)

        except NotSupportedError as e:
            raise NotSupportedError(
                f"{self.__class__.__name__} only support {list(self.transformer_map.keys())} companies now, {ticker} is not available"
            ) from e

    async def query_data(
        self, start_date=None, end_date=None, get_latest=False
    ):
        fetched_data = await self.extractor.query_data(
            start_date, end_date, get_latest
        )
        tech_data = await self.daily_extractor.query_data(
            start_date, end_date, get_latest
        )

        fetched_data = {"institution_trading": fetched_data}
        transformed_data = self.transformer.process_transform(
            tech_data=tech_data, **fetched_data
        )

        return transformed_data

    async def query_data_annual(self):
        """
        取一年內的資料
        """
        end_date = datetime.today()
        start_date = end_date - timedelta(days=365)

        fetched_data = await self.query_data(
            start_date, end_date, get_latest=False
        )

        return fetched_data
