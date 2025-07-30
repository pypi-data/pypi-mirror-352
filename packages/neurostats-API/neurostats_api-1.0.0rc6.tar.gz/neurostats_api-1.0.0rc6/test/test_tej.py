import pytest

mongo_uri = "mongodb+srv://admin:Neurowatt456&@axonnews-mongodb.nlui1.mongodb.net/?retryWrites=true&w=majority&appName=axonnews-mongodb"
ticker = "2330"
# collection_name = "TWN/AFESTM1"
collection_name = "TWN/AINVFQ1"

def test_QoQ():

    from neurostats_API import FinanceReportFetcher

    fetcher = FinanceReportFetcher(mongo_uri, collection_name=collection_name)

    modes = [
        fetcher.FetchMode.QOQ,
        fetcher.FetchMode.QOQ_NOCAL
    ]


    for mode in modes:
        data = fetcher.get(
            ticker,
            fetch_mode = mode,
            start_date="2024-01-01",
            end_date="2024-12-31",
        )
        print(data)
        if (isinstance(data, dict)):
            print(len(data.keys()))
        else:
            print(len(data.index))
def test_YoY():
    from neurostats_API import FinanceReportFetcher
    fetcher = FinanceReportFetcher(mongo_uri, collection_name=collection_name)

    modes = [
        fetcher.FetchMode.YOY,
        fetcher.FetchMode.YOY_NOCAL
    ]

    for mode in modes:
        data = fetcher.get(ticker, mode, indexes = ["r405"])
        print (data)

def test_stock_price():
    from neurostats_API import TEJStockPriceFetcher

    fetcher = TEJStockPriceFetcher(mongo_uri, collection_name="TWN/APIPRCD")

    data = fetcher.get(ticker, period='3y')

    print(data)
