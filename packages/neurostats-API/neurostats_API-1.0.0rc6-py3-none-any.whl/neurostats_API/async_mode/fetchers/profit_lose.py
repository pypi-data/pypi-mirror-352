from neurostats_API.async_mode.db_extractors import AsyncProfitLoseExtractor
from neurostats_API.async_mode.factory import get_extractor
from neurostats_API.transformers import (
    TWSEProfitLoseTransformer,
    USProfitLoseTransformer
)
from neurostats_API.utils import (
    NoCompanyError,
    NotSupportedError
)

from .base import AsyncBaseFetcher

class AsyncProfitLoseFetcher(AsyncBaseFetcher):
    def __init__(
        self, 
        ticker,
        client
    ):
        self.ticker = ticker
        
        self.transformer_map = {
            "tw": TWSEProfitLoseTransformer,
            "us": USProfitLoseTransformer
        }
        try:
            self.extractor = get_extractor("DB_profit_lose", ticker, client)
            company_name = self.extractor.get_company_name()
            zone = self.extractor.get_zone()

            transformer = self.get_transformer(zone)
            self.transformer = transformer(ticker, company_name, zone)
        
        except NotSupportedError as e:
            raise NotSupportedError(
                 f"{self.__class__.__name__} only support {list(self.transformer_map.keys())} companies now, {ticker} is not available"
            ) from e

    async def query_data(self, start_date = None, end_date = None):
        fetched_data = await self.extractor.query_data(start_date, end_date)

        transformed_data = self.transformer.process_transform(
            fetched_data
        )

        return transformed_data