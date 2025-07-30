from typing import Type, TypedDict, Optional
from neurostats_API.async_mode.db_extractors import (
    AsyncTEJDailyTechDBExtractor, AsyncYFDailyTechDBExtractor,
    AsyncDailyValueDBExtractor, AsyncTEJDailyValueDBExtractor,
    AsyncTWSEChipDBExtractor, AsyncTWSEMonthlyRevenueExtractor,
    AsyncBalanceSheetExtractor, AsyncProfitLoseExtractor,
    AsyncCashFlowExtractor, AsyncTEJFinanceStatementDBExtractor,
    AsyncTEJSelfSettlementDBExtractor
)
from neurostats_API.utils import NotSupportedError


class ExtractorConfig(TypedDict):
    class_: Type
    description: Optional[str]
    default_kwargs: dict


EXTRACTOR_MAP: dict[str, ExtractorConfig] = {
    # TEJ 相關
    "TEJ_finance_statement": {
        "class_":
        AsyncTEJFinanceStatementDBExtractor,
        "default_kwargs": {
            "fetch_type": "Q"
        },
        "description":
        """
        DB_collection: TEJ_finance_statement
        對應TEJ的\"會計師簽證財務資料\"
        """,
    },
    "TEJ_self_settlement": {
        "class_":
        AsyncTEJSelfSettlementDBExtractor,
        "default_kwargs": {
            "fetch_type": "Q"
        },
        "description":
        """
        DB_collection: TEJ_self_settlement
        對應TEJ的\"公司自結數\"
        """
    },

    # TWSE 本地DB
    "DB_balance_sheet": {
        "class_":
        AsyncBalanceSheetExtractor,
        "default_kwargs": {},
        "description":
        """
        DB_collection: twse_seasonal_report(tw), us_fundamental(us)
        對應TWSE的\"資產負債表\"與美股的\"Balance_Sheet\"
        tw: 選取balance_sheet欄
        us: 選取balance_sheet欄
        """
    },
    "DB_profit_lose": {
        "class_":
        AsyncProfitLoseExtractor,
        "default_kwargs": {},
        "description":
        """
        DB_collection: twse_seasonal_report(tw), us_fundamental(us)
        對應TWSE的\"損益表\"與美股的\"Income Statement\"
        tw: 選取profit_lose欄
        us: 選取income_statement欄
        """
    },
    "DB_cash_flow": {
        "class_":
        AsyncCashFlowExtractor,
        "default_kwargs": {},
        "description":
        """
        DB_collection: twse_seasonal_report(tw), us_fundamental(us)
        對應TWSE的\"金流表\"與美股的\"Cash Flow\"
        tw: 選取cash_flow欄
        us: 選取cash_flow欄
        """
    },

    # tech
    "YF_tech": {
        "class_":
        AsyncYFDailyTechDBExtractor,
        "default_kwargs": {},
        "description":
        """
        DB_collection: twse_daily_share_price(tw), us_tech(us)
        開高低收
        """
    },
    "TEJ_tech": {
        "class_":
        AsyncTEJDailyTechDBExtractor,
        "default_kwargs": {},
        "description":
        """
        DB_collection: TEJ_share_price
        TEJ的開高低收
        """
    },

    # Month Revenue
    "TWSE_month_revenue": {
        "class_":
        AsyncTWSEMonthlyRevenueExtractor,
        "default_kwargs": {},
        "description":
        """
        DB_collection: twse_month_revenue
        TWSE的月營收
        """
    },

    # Chip
    "TWSE_chip": {
        "class_":
        AsyncTWSEChipDBExtractor,
        "default_kwargs": {
            "fetch_type": "I"
        },
        "description":
        """
        DB_collection: twse_chip
        TWSE的籌碼面
        """
    },

    # Value
    "TWSE_value": {
        "class_":
        AsyncDailyValueDBExtractor,
        "default_kwargs": {},
        "description":
        """
        DB_collection: twse_daily_share_price
        TWSE的評價面
        """
    }
}


def get_extractor(collection: str, ticker: str, client, **override_kwargs):
    """
    collection: extractor對應的KEY_NAME,
    ticker: 初始化extractor用的參數, 指定哪家公司
    client: 初始化extractor用的參數, 連接的db_client
    overide_kwargs: 除ticker與client外部分extractor會需要的參數，例如fetch_type
    """

    config = EXTRACTOR_MAP.get(collection, None)

    if (config is None):
        # 不存在的extractor name處理
        valid = ", ".join(EXTRACTOR_MAP.keys())
        raise NotSupportedError(
            f"{collection} not a regular argument for collection, only {[valid]} available"
        )

    extractor_cls = config["class_"]
    default_kwargs: dict = config["default_kwargs"]

    init_kwargs = {**default_kwargs, **override_kwargs}    # 用後續的參數覆蓋

    return extractor_cls(ticker, client, **init_kwargs)
