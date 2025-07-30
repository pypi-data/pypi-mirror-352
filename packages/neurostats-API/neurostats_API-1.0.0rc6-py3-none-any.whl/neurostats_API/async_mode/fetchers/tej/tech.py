import pandas as pd
from neurostats_API.async_mode.fetchers.base import AsyncBaseFetcher
from neurostats_API.async_mode.factory import get_extractor
from neurostats_API.utils import NotSupportedError

class AsyncTEJDailyTechFetcher(AsyncBaseFetcher):
    
    def __init__(
        self,
        ticker,
        client,
    ):
        self.ticker = ticker
        try:
            self.extractor = get_extractor("TEJ_tech", ticker, client)

            self.company_name = self.extractor.get_company_name()
            self.zone = self.extractor.get_zone()

        except NotSupportedError as e:
            raise NotSupportedError(
                f"{self.__class__.__name__} only support TW companies now, {ticker} is not available"
            ) from e
    
    async def query_data(self, start_date, end_date):
        data = await self.extractor.query_data(start_date, end_date)
        df = pd.DataFrame(data)
        return df.rename(columns={
            "open_d": "open",
            "high_d": "high",
            "low_d": "low",
            "close_d": "close",
            "vol": "volume"
        })