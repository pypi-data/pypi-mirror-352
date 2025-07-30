from .base import AsyncBaseFetcher
from ..db_extractors import AsyncTWSEMonthlyRevenueExtractor
from neurostats_API.async_mode.factory import get_extractor
from neurostats_API.transformers import TWSEMonthlyRevenueTransformer
from neurostats_API.utils import NoCompanyError, NotSupportedError


class AsyncMonthlyRevenueFetcher(AsyncBaseFetcher):

    def __init__(self, ticker, client):
        self.ticker = ticker
        self.transformer_map = {
            "tw": TWSEMonthlyRevenueTransformer,
        }

        try:
            self.extractor = get_extractor("TWSE_month_revenue", ticker, client)
            company_name = self.extractor.get_company_name()
            zone = self.extractor.get_zone()

            transformer = self.get_transformer(zone)

            self.transformer = transformer(ticker, company_name, zone)
        except NotSupportedError as e:
            raise NotSupportedError(
                "AsyncMonthRevenueFetcher only supports tw company now"
            ) from e


    async def query_data(self, start_date=None, end_date=None):
        fetched_data = await self.extractor.query_data(start_date, end_date)

        transformed_data = self.transformer.process_transform(fetched_data)

        return transformed_data
