from .base import AsyncBaseFetcher
from ..db_extractors import AsyncBalanceSheetExtractor
from neurostats_API.transformers import (
    TWSEBalanceSheetTransformer, USBalanceSheetTransformer
)
from neurostats_API.async_mode.factory import get_extractor
from neurostats_API.utils import NotSupportedError


class AsyncBalanceSheetFetcher(AsyncBaseFetcher):

    def __init__(self, ticker, client):
        super().__init__()
        self.ticker = ticker
        self.transformer_map = {
            "tw": TWSEBalanceSheetTransformer,
            "us": USBalanceSheetTransformer
        }
        self.extractor = get_extractor("DB_balance_sheet", ticker, client)
        company_name = self.extractor.get_company_name()
        zone = self.extractor.get_zone()

        transformer = self.get_transformer(zone)
        self.transformer = transformer(ticker, company_name, zone)

    async def query_data(self, start_date=None, end_date=None):
        fetched_data = await self.extractor.query_data(start_date, end_date)

        transformed_data = self.transformer.process_transform(fetched_data)

        return transformed_data
