from .base import AsyncBaseFetcher
from datetime import datetime, timedelta
from neurostats_API.async_mode.factory import get_extractor
from ..db_extractors import (
    AsyncTWSEChipDBExtractor,
    AsyncYFDailyTechDBExtractor,
)

from neurostats_API.transformers import TWSEChipTransformer
from neurostats_API.utils import NotSupportedError
import pandas as pd


class AsyncTWSEMarginFetcher(AsyncBaseFetcher):
    """
    stats 網頁用
    """

    def __init__(self, ticker, client):
        self.ticker = ticker
        self.transformer_map = {"tw": TWSEChipTransformer}
        try:
            self.margin_extractor = get_extractor(
                "TWSE_chip", ticker, client, fetch_type='M'
            )
            self.security_extractor = get_extractor(
                "TWSE_chip", ticker, client, fetch_type='S'
            )
            self.daily_extractor = get_extractor("YF_tech", ticker, client)

            company_name = self.margin_extractor.get_company_name()
            zone = self.margin_extractor.get_zone()



            transformer = self.get_transformer(zone)
            self.transformer = transformer(ticker, company_name, zone)
        except NotSupportedError as e:
            raise NotSupportedError(
                f"{self.__class__.__name__} only support {list(self.transformer_map.keys())} companies now, {ticker} is not available"
            ) from e

    async def query_data(self, start_date=None, end_date=None):
        margin = await self.margin_extractor.query_data(start_date, end_date)
        security_lending = await self.security_extractor.query_data(
            start_date, end_date
        )

        tech_data = await self.daily_extractor.query_data(start_date, end_date)

        fetched_data = {
            "margin_trading": margin,
            "security_lending": security_lending
        }
        transformed_data = self.transformer.process_transform(
            tech_data=tech_data, **fetched_data
        )
        transformed_data['annual_trading'] = self._concat_data(
            transformed_data['annual_trading']
        )

        return transformed_data

    async def query_data_annual(self):
        """
        取一年內的資料
        """
        end_date = datetime.today()
        start_date = end_date - timedelta(days=365)

        fetched_data = await self.query_data(start_date, end_date)

        return fetched_data

    def _concat_data(self, annaual_data):
        """
        借券, 債券串接
        annaual_data: 
        {
            "margin_trading": pd.DataFrame,
            'security_lending': pd.DataFrame
        }
        """

        margin_annual = annaual_data.get("margin_trading")
        security_annaul = annaual_data.get("security_lending")

        unique_cols = [
            name for name in security_annaul.columns
            if name not in margin_annual.columns
        ]
        concat_df = pd.concat(
            [margin_annual, security_annaul[unique_cols]], axis=1
        )

        return {
            'margin_trading': margin_annual,
            'security_lending': security_annaul,
            'stats_page_history': concat_df
        }
