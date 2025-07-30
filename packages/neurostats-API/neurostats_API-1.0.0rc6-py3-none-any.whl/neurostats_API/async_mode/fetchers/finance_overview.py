from .base import AsyncBaseFetcher
from datetime import datetime
import importlib.resources as pkg_resources

from neurostats_API.async_mode.db_extractors import (
    AsyncBalanceSheetExtractor, AsyncCashFlowExtractor, AsyncProfitLoseExtractor
)
from neurostats_API.async_mode.factory import get_extractor
from neurostats_API.transformers import AgentOverviewTransformer, FinanceOverviewTransformer
from neurostats_API.utils import StatsDateTime, StatsProcessor, NoCompanyError, NotSupportedError
import numpy as np
import pandas as pd
import pytz
import holidays
import warnings

warnings.filterwarnings(
    "ignore",
    category=holidays.deprecations.v1_incompatibility.
    FutureIncompatibilityWarning
)
import yaml


class AsyncFinanceOverviewFetcher(AsyncBaseFetcher):
    """
    對應iFa.ai -> 財務分析 -> 重要指標(finance_overview)
    """

    def __init__(self, ticker, db_client):
        super().__init__()

        self.target_fields = StatsProcessor.load_yaml(
            "twse/finance_overview_dict.yaml"
        )
        self.inverse_dict = StatsProcessor.load_txt(
            "twse/seasonal_data_field_dict.txt", json_load=True
        )
        try:
            self.balance_sheet_extractor = get_extractor(
                "DB_balance_sheet", ticker, db_client
            )
            self.profit_lose_extractor = get_extractor(
                "DB_profit_lose", ticker, db_client
            )
            self.cashflow_extractor = get_extractor(
                "DB_cash_flow", ticker, db_client
            )

            company_name = self.balance_sheet_extractor.get_company_name()
            zone = self.balance_sheet_extractor.get_zone()

            if (zone != 'tw'):
                raise NotSupportedError(None)

            self.transformer = FinanceOverviewTransformer(
                ticker, company_name, zone
            )
        except NotSupportedError as e:
            raise NotSupportedError("FinanceOverviewFetcher only supports TW corporation now") from e

    async def query_data(self, date=None):

        balance_sheet = await self.balance_sheet_extractor.query_data(
            end_date=date, get_latest=True
        )
        profit_lose = await self.profit_lose_extractor.query_data(
            end_date=date, get_latest=True
        )
        cash_flow = await self.cashflow_extractor.query_data(
            end_date=date, get_latest=True
        )

        transformed_data = self.transformer.process_transform(
            balance_sheet, profit_lose, cash_flow
        )

        return transformed_data


class AsyncAgentOverviewFetcher(AsyncBaseFetcher):
    """
    用於P1-Agent 的 公司股市經濟概況頁面
    """

    def __init__(self, ticker, db_client):
        from neurostats_API.async_mode.fetchers import AsyncTechFetcher
        self.ticker = ticker
        self.tech_fetcher = AsyncTechFetcher(
            ticker=self.ticker, client=db_client
        )
        try:
            self.balance_sheet_extractor = AsyncBalanceSheetExtractor(
                ticker=self.ticker, client=db_client
            )
            self.profit_lose_extractor = AsyncProfitLoseExtractor(
                ticker=self.ticker, client=db_client
            )
            self.cash_flow_extractor = AsyncCashFlowExtractor(
                ticker=self.ticker, client=db_client
            )

            company_name = self.balance_sheet_extractor.get_company_name()
            zone = self.balance_sheet_extractor.get_zone()

            self.transformer_map = {'us': AgentOverviewTransformer}

            transformer = self.get_transformer(zone)
            self.transformer = transformer(ticker, company_name, zone)

        except NotSupportedError as e:
            raise NotSupportedError(
                f'Agent Overview only supports US corporation now, Got zone={zone}, ticker={ticker}'
            ) from e

    async def query_data(self, date=None):

        tech_data = await self.tech_fetcher.get_daily(
            start_date=None, end_date=date
        )
        balance_sheet = await self.balance_sheet_extractor.query_data(
            end_date=date
        )
        profit_lose = await self.profit_lose_extractor.query_data(end_date=date)
        cash_flow = await self.cash_flow_extractor.query_data(end_date=date)

        return_data = self.transformer.process_transform(
            tech_data=tech_data,
            balance_sheet_list=balance_sheet,
            profit_lose_list=profit_lose,
            cash_flow_list=cash_flow
        )

        return return_data
