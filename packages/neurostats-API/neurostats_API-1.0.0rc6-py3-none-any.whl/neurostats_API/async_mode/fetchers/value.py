from .base import AsyncBaseFetcher
from ..db_extractors import (
    AsyncDailyValueDBExtractor, AsyncTEJDailyValueDBExtractor
)
from neurostats_API.async_mode.factory import get_extractor
from neurostats_API.transformers import TWSEAnnualValueTransformer, TWSEHistoryValueTransformer
from neurostats_API.utils import NotSupportedError


class AsyncTWSEStatsValueFetcher(AsyncBaseFetcher):

    def __init__(self, ticker, client):

        self.ticker = ticker
        self.transformer_map = {
                "tw": (TWSEHistoryValueTransformer, TWSEAnnualValueTransformer)
            }
        try:
            self.daily_data_extractor = get_extractor("TWSE_value", ticker, client, fetch_type = 'D')
            self.annual_data_extractor = get_extractor("TWSE_value", ticker, client, fetch_type = 'Y')

            self.company_name = self.daily_data_extractor.get_company_name()
            self.zone = self.daily_data_extractor.get_zone()

            transformer = self.get_transformer(self.zone)

            daily_transformer, annual_transformer = transformer
            self.daily_transformer = daily_transformer(
                ticker, self.company_name, self.zone
            )
            self.annual_transformer = annual_transformer(
                ticker, self.company_name, self.zone
            )

            self.return_dict = {
                "ticker": self.ticker,
                "company_name": self.company_name
            }
        except NotSupportedError as e:
            raise NotSupportedError(
                f"{self.__class__.__name__} only support {list(self.transformer_map.keys())} companies now, {ticker} is not available"
            ) from e

    async def query_data(self, start_date=None, end_date=None):

        annual_data = await self.annual_data_extractor.query_data(
            start_date, end_date
        )
        daily_data = await self.daily_data_extractor.query_data(
            start_date=start_date, end_date=end_date
        )

        self.return_dict['yearly_data'
                         ] = self.annual_transformer.process_transform(
                             annual_data
                         )
        self.return_dict['daily_data'] = self.daily_transformer.process_latest(
            daily_data
        )
        self.return_dict['value_serie'
                         ] = self.daily_transformer.process_transform(
                             daily_data
                         )

        return self.return_dict

    async def query_value_serie(self, start_date=None, end_date=None):
        daily_data = await self.daily_data_extractor.query_data(
            start_date, end_date
        )
        self.return_dict['value_serie'
                         ] = self.daily_transformer.process_transform(
                             daily_data
                         )

        return self.return_dict
