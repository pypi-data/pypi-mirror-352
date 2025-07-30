from .base import AsyncBaseFetcher
from ..db_extractors import AsyncCashFlowExtractor
from neurostats_API.async_mode.factory import get_extractor
from neurostats_API.transformers import (
    TWSECashFlowTransformer, USCashFlowTransformer
)
from neurostats_API.utils import NoCompanyError, NotSupportedError


class AsyncCashFlowFetcher(AsyncBaseFetcher):

    def __init__(self, ticker, client):

        super().__init__()
        self.transformer_map = {
            "tw": TWSECashFlowTransformer,
            "us": USCashFlowTransformer
        }
        self.ticker = ticker
        try:
            self.extractor = get_extractor("DB_cash_flow", self.ticker, client)
            self.company_name = self.extractor.get_company_name()
            self.zone = self.extractor.get_zone()

            transformer = self.get_transformer(self.zone)
            self.transformer = transformer(ticker, self.company_name, self.zone)
        
        except NotSupportedError as e:
            raise NotSupportedError(
                f"{self.__class__.__name__} only support {list(self.transformer_map.keys())} companies now, {ticker} is not available"
            ) from e
        except NoCompanyError:
            raise

    async def query_data(self, start_date=None, end_date=None):
        fetched_data = await self.extractor.query_data(start_date, end_date)

        transformed_data = self.transformer.process_transform(fetched_data)

        return transformed_data

    async def query_data_stats_only(self, start_date=None, end_date=None):
        fetched_data = await self.extractor.query_data(start_date, end_date)

        transformed_data = self.transformer.process_stats_page(fetched_data)

        return transformed_data

    async def query_data_QoQ_and_YoY_only(self, start_date=None, end_date=None):
        if (self.zone != 'tw'):
            raise NotSupportedError("query_data_QoQ_and_YoY_only() only supports for TW companies")
        fetched_data = await self.extractor.query_data(start_date, end_date)

        transformed_data = self.transformer.process_QoQ(fetched_data)

        return transformed_data
