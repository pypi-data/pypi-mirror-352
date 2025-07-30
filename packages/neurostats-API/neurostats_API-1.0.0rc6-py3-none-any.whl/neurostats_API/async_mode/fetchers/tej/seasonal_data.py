from neurostats_API.async_mode.fetchers.base import AsyncBaseFetcher
from datetime import datetime
from neurostats_API.async_mode.db_extractors import (
    AsyncTEJFinanceStatementDBExtractor, AsyncTEJSelfSettlementDBExtractor
)
from neurostats_API.async_mode.factory import get_extractor
from neurostats_API.transformers import TEJFinanceStatementTransformer
from neurostats_API.utils import NotSupportedError


class AsyncTEJSeasonalFetcher(AsyncBaseFetcher):

    def __init__(
        self,
        ticker,
        client,
        collection='TEJ_finance_statement',
        fetch_type='Q'
    ):
        self.ticker = ticker
        self.fetch_type = fetch_type
        self.transformer_map = {"tw": TEJFinanceStatementTransformer}
        try:
            self.db_extractor = get_extractor(
                collection=collection,
                ticker=ticker,
                client=client,
                fetch_type=fetch_type
            )

            self.company_name = self.db_extractor.get_company_name()
            self.zone = self.db_extractor.get_zone()

            

            transformer = self.get_transformer(self.zone)

            self.transformer = transformer(
                ticker=ticker,
                company_name=self.company_name,
                zone=self.zone,
                target_column=fetch_type
            )

        except NotSupportedError as e:
            raise NotSupportedError(
                f"{self.__class__.__name__} only support {list(self.transformer_map.keys())} companies now, {ticker} is not available"
            ) from e

    async def query_data(
        self,
        start_date=None,
        end_date=None,
        fetch_mode='QoQ',
        use_cal=True,
        indexes=None
    ):
        fetched_data = await self.db_extractor.query_data(
            start_date=None, end_date=end_date
        )    # 先索取目標日期之前的之後再截斷

        if (start_date is None):
            start_date = datetime.strptime("1991-01-01", "%Y-%m-%d")

        transformed_data = self.transformer.process_transform(
            fetched_data=fetched_data,
            fetch_mode=fetch_mode,
            start_date=start_date,
            use_cal=use_cal,
            indexes=indexes
        )    # 轉換並根據開始日期截斷

        return transformed_data

    def _get_extractor(self, collection):
        EXTRACTOR_MAP = {
            "TEJ_finance_statement": AsyncTEJFinanceStatementDBExtractor,
            "TEJ_self_settlement": AsyncTEJSelfSettlementDBExtractor,
        }

        extractor = EXTRACTOR_MAP.get(collection, None)

        if (extractor is None):
            raise ValueError(
                f"{collection} not a regular argument for collection, only {list(EXTRACTOR_MAP.keys())} available"
            )

        return extractor
