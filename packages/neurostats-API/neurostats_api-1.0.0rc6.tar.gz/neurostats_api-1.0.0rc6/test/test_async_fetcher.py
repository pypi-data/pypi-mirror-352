import json
from pprint import PrettyPrinter
import pytest
import pandas as pd
import yaml
from pymongo import AsyncMongoClient


mongo_uri = "mongodb://neurowatt:neurodb123@db.neurowatt.ai:27017/neurowatt"
tickers = ["AAPL", "2330", "1260", "-1234"]

client = AsyncMongoClient(mongo_uri)

end_date = '2024-09-01'

pp = PrettyPrinter(indent=1)


pd.set_option("display.max_rows", 2)         # 顯示所有列
pd.set_option("display.max_columns", 2)      # 顯示所有欄
pd.set_option("display.width", 0)               # 自動根據 terminal 寬度換行
pd.set_option("display.max_colwidth", None)     # 顯示所有欄位字串長度（不省略）
pd.set_option("expand_frame_repr", False)


@pytest.mark.asyncio
async def test_balance_sheet():
    print("# Balance Sheet")
    from neurostats_API.async_mode.fetchers import AsyncBalanceSheetFetcher

    for ticker in tickers:
        fetcher = AsyncBalanceSheetFetcher(ticker, client)

        data = await fetcher.query_data()

        print_dict_summary(data)
    print('========================================')



@pytest.mark.asyncio
async def test_profit_lose():
    print("# Profit Lose")
    from neurostats_API.async_mode.fetchers import AsyncProfitLoseFetcher

    for ticker in tickers:
        fetcher = AsyncProfitLoseFetcher(ticker, client)

        data = await fetcher.query_data(start_date='2024-01-01' ,end_date=end_date)

        print_dict_summary(data)
    print('========================================')
    


@pytest.mark.asyncio
async def test_cash_flow():
    print("# Cash Flow")
    from neurostats_API.async_mode.fetchers import AsyncCashFlowFetcher
    for ticker in tickers:
        fetcher = AsyncCashFlowFetcher(ticker, client)

        data = await fetcher.query_data(end_date=end_date)

        print_dict_summary(data)
    print('========================================')
    


@pytest.mark.asyncio
async def test_cash_flow_partial():
    print("# Cash Flow (QoQ and YoY only)")
    from neurostats_API.async_mode.fetchers import AsyncCashFlowFetcher
    for ticker in tickers:
        fetcher = AsyncCashFlowFetcher(ticker, client)

        data = await fetcher.query_data_QoQ_and_YoY_only(end_date=end_date)

        print_dict_summary(data)
    print('========================================')


@pytest.mark.asyncio
async def test_month_revenue():
    print("# Month Revenue")
    from neurostats_API.async_mode.fetchers import AsyncMonthlyRevenueFetcher
    for ticker in tickers:
        fetcher = AsyncMonthlyRevenueFetcher(ticker, client)

        data = await fetcher.query_data(end_date=end_date)

        print_dict_summary(data)
    print('========================================')


@pytest.mark.asyncio
async def test_tech():
    print("# Tech")
    from neurostats_API.async_mode.fetchers import AsyncTechFetcher

    for ticker in tickers:
        fetcher = AsyncTechFetcher(ticker, client)

        test_fns = [
            fetcher.get_daily, fetcher.get_weekly, fetcher.get_monthly,
            fetcher.get_quarterly, fetcher.get_yearly, fetcher.get_tej
        ]

        for fetch_fn in test_fns:
            print(f"{fetch_fn.__name__}")
            data = await fetch_fn()

            print(data)
    print('========================================')
@pytest.mark.asyncio
async def test_institution():
    print("# Institution trading")
    from neurostats_API.async_mode.fetchers import AsyncTWSEInstitutionFetcher

    for ticker in tickers:
        fetcher = AsyncTWSEInstitutionFetcher(ticker, client)

        test_fns = [fetcher.query_data]

        for fetch_fn in test_fns:
            data = await fetch_fn()

            print_dict_summary(data)
    print('========================================')


@pytest.mark.asyncio
async def test_margin():
    print("# Margin trading")
    from neurostats_API.async_mode.fetchers import AsyncTWSEMarginFetcher

    for ticker in tickers:
        fetcher = AsyncTWSEMarginFetcher(ticker, client)

        test_fns = [fetcher.query_data, fetcher.query_data_annual]

        for fetch_fn in test_fns:
            data = await fetch_fn()

            print_dict_summary(data)
    print('========================================')

@pytest.mark.asyncio
async def test_value():
    print("# Valuation")
    from neurostats_API.async_mode.fetchers import AsyncTWSEStatsValueFetcher

    for ticker in tickers:
        fetcher = AsyncTWSEStatsValueFetcher(ticker, client)

        test_fn = [fetcher.query_data]

        for fetch_fn in test_fn:
            data = await fetch_fn()

            print_dict_summary(data)
    print('========================================')

@pytest.mark.asyncio
@pytest.mark.parametrize("ticker", tickers)
@pytest.mark.parametrize("collection", ["TEJ_finance_statement"])
@pytest.mark.parametrize("params", [
    {"fetch_mode": "QoQ", "use_cal": False, "indexes": []},
    {"fetch_mode": "QoQ", "use_cal": True, "indexes": []},
    {"fetch_mode": "QoQ", "use_cal": False, "indexes": ["eps"]},
    {"fetch_mode": "QoQ", "use_cal": True, "indexes": ["eps"]},
    {"fetch_mode": "YoY", "use_cal": False, "indexes": []},
    {"fetch_mode": "YoY", "use_cal": True, "indexes": []},
    {"fetch_mode": "YoY", "use_cal": False, "indexes": ["eps"]},
    {"fetch_mode": "YoY", "use_cal": True, "indexes": ["eps"]},
])
async def test_tej_fetchers(ticker, collection, params):
    from neurostats_API.utils import NoDataError
    from neurostats_API.async_mode.fetchers import AsyncTEJSeasonalFetcher
    print(f"# TEJ [{collection}] {ticker} - {params}")
    fetcher = AsyncTEJSeasonalFetcher(
        ticker=ticker,
        client=client,
        collection=collection
    )

    try:
        data = await fetcher.query_data(**params)
        
        print(data)
    except NoDataError:
        print(f"!! No data for [{collection}] {ticker} !!")
    print('========================================')


@pytest.mark.asyncio
async def test_stats_overview():
    print(f"# stats overview")
    from neurostats_API.async_mode.fetchers import AsyncFinanceOverviewFetcher

    for ticker in tickers:
        fetcher = AsyncFinanceOverviewFetcher(ticker, client)

        test_fn = [fetcher.query_data]

        for fetch_fn in test_fn:
            data = await fetch_fn()

            print_dict_summary(data)
    print('========================================')

@pytest.mark.asyncio
async def test_agent_overview():
    print(f"# Agents overview")
    from neurostats_API.async_mode.fetchers import AsyncAgentOverviewFetcher

    for ticker in tickers:
        fetcher = AsyncAgentOverviewFetcher(ticker, client)

        test_fn = [fetcher.query_data]

        for fetch_fn in test_fn:
            data = await fetch_fn()

            print_dict_summary(data)
    print('========================================')

def print_dict_summary(data: dict, indent: int = 1):
    prefix = " " * indent
    for key, value in data.items():
        if isinstance(value, pd.DataFrame):
            assert value.shape!= (0, 0)
            print(f"{prefix} \"{key}\": DataFrame shape = {value.shape}")
        elif isinstance(value, pd.Series):
            print(f"{prefix} \"{key}\": Series shape = {value.shape}")
        elif isinstance(value, dict):
            print(f"{prefix} \"{key}\": dict with {len(value)} keys")
            print_dict_summary(value, indent + 2)
        elif isinstance(value, list):
            print(f"{prefix} \"{key}\": list of length {len(value)}")
        else:
            val_preview = str(value)
            if len(val_preview) > 100:
                val_preview = val_preview[:100] + "..."
            print(f"{prefix} \"{key}\": {type(value).__name__} = {val_preview}")