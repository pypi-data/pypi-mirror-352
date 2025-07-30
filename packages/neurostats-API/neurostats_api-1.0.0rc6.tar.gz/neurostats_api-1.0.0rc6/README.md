# neurostats_API

- [檔案架構](#檔案架構)
- [下載](#下載)
- [使用方法](#使用方法)

## 檔案架構

```
./neurostats_API
├── async_mode
│   ├── db
│   ├── db_extractors
│   │   ├── daily
│   │   ├── month_revenue
│   │   └── seasonal
│   ├── factory
│   └── fetchers
├── config
│   ├── company_list
│   ├── tej_db
│   └── twse
├── fetchers
├── transformers
│   ├── balance_sheet
│   ├── cash_flow
│   ├── daily_chip
│   │   └── utils
│   ├── daily_tech
│   │   └── utils
│   ├── finance_overview
│   ├── month_revenue
│   ├── profit_lose
│   ├── tej
│   └── value
└── utils
```
- `neurostats_API`: 主要的package運行內容
   - `async_mode`: \[新版新增\]以非同步方式進行DB資料的取得以及回傳資料
      - `/db`: 連接到伺服器下的特定db
      - `/db_extractor`: 決定取得db下的哪個collection的檔案，以及取得檔案內容
      ` `/factory`: 使extractor的初始化變得通用
      - `/fetchers`:  開發者將此套件用於其他專案的接口
   - `fetchers`: (舊版)回傳service內容的fetcher檔案夾
   - `transformers`: \[新版新增\] 處理從DB取出的資料，以dictionary的方式回傳需要的資料
   - `config`: 【新舊通用】存放各種設定檔的dictionary，例如公司名單、各項指標對應的計算欄位、每個項目屬於哪份財報等設定
   - `utils`: 【新舊通用】class之間通用的函式，例如讀取檔案、計算成長率函式、轉換格式與進位等

## 下載
```
pip install neurostats-API
```
### 確認下載成功
```Python 
>>> import neurostats_API
>>> print(neurostats_API.__version__)
1.0.0rc6
```

### 下載舊版
```
pip install neurostats-API==0.0.25
```

## 使用方式 (以Balance_Sheet為例)
### Async Mode
```
from neurostats_API.async_mode.fetchers import AsyncBalanceSheetFetcher
from pymongo import AsyncMongoClient

db_client = AsyncMongoClient("<伺服器的MONGO_URI>")
ticker = "2330"

fetcher = AsyncBalanceSheetFetcher(ticker, db_client)

data = await fetcher.query_data()

print(data)
```
詳細各個fetcher的使用法請到[async_mode的fetchers資料夾下觀看](./neurostats_API/async_mode/fetchers/README.md)

### Sync Mode
(#TODO)

> 舊版使用方法請到[fetchers資料夾下觀看](./neurostats_API/fetchers/README.md)