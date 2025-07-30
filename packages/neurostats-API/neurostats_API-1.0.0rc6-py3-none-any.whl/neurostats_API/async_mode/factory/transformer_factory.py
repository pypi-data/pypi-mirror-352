# 本模組提供各種財報、評價、籌碼等資料轉換器的工廠函式，根據 zone（如 "tw"、"us"）自動選擇對應的 Transformer 類別。
# 若 zone 不支援則會拋出 NotSupportedError，方便統一管理與擴充。

from typing import Type, TypedDict, Optional
from neurostats_API.transformers import (
    AgentOverviewTransformer,
    TEJFinanceStatementTransformer,
    TWSEAnnualValueTransformer,
    TWSEBalanceSheetTransformer,
    TWSECashFlowTransformer,
    TWSEChipTransformer,
    TWSEHistoryValueTransformer,
    TWSEMonthlyRevenueTransformer,
    TWSEProfitLoseTransformer,
    USBalanceSheetTransformer,
    USCashFlowTransformer,
    USProfitLoseTransformer
)
from neurostats_API.utils import NotSupportedError


def get_balance_sheet_transformer(zone):
    """
    取得資產負債表（Balance Sheet）對應地區的 Transformer 類別。
    參數:
        zone: "tw"（台灣）或 "us"（美國）
    回傳:
        對應的 Transformer 類別
    """
    transformer_map = {
        "tw": TWSEBalanceSheetTransformer,
        "us": USBalanceSheetTransformer
    }
    return _get_transformer_by_zone("Balance Sheet", zone, transformer_map)

def get_cash_flow_transformer(zone):
    """
    取得現金流量表（Cash Flow）對應地區的 Transformer 類別。
    參數:
        zone: "tw" 或 "us"
    回傳:
        對應的 Transformer 類別
    """
    transformer_map = {
        "tw": TWSECashFlowTransformer,
        "us": USCashFlowTransformer
    }
    return _get_transformer_by_zone("Cash Flow", zone, transformer_map)

def get_profit_lose_transformer(zone):
    """
    取得損益表（Profit Lose, 又稱 Income Statement）對應地區的 Transformer 類別。
    參數:
        zone: "tw" 或 "us"
    回傳:
        對應的 Transformer 類別
    """

    transformer_map = {
        "tw": TWSEProfitLoseTransformer,
        "us": USProfitLoseTransformer
    }
    return _get_transformer_by_zone("Profit Lose (a.k.a. Income Statement)", zone, transformer_map)

def get_chip_transformer(zone):
    """
    取得籌碼面（Chip）對應地區的 Transformer 類別。
    參數:
        zone: "tw"
    回傳:
        對應的 Transformer 類別
    """
    transformer_map = {
        "tw": TWSEChipTransformer
    }
    return _get_transformer_by_zone("Chip", zone, transformer_map)


def get_monthly_revenue_transformer(zone):
    """
    取得月營收（Monthly Revenue）對應地區的 Transformer 類別。
    參數:
        zone: "tw"
    回傳:
        對應的 Transformer 類別
    """
    transformer_map = {
        "tw": TWSEMonthlyRevenueTransformer
    }
    return _get_transformer_by_zone("MonthlyRevenue", zone, transformer_map)


def get_annual_value_transformer(zone):
    """
    取得歷年評價面數值（Annual Value）對應地區的 Transformer 類別。
    參數:
        zone: "tw"
    回傳:
        對應的 Transformer 類別
    """
    transformer_map = {
        "tw": TWSEAnnualValueTransformer
    }
    return _get_transformer_by_zone("AnnualValue", zone, transformer_map)


def get_history_value_transformer(zone):
    """
    取得歷來評價面數值（History Value）對應地區的 Transformer 類別。
    參數:
        zone: "tw"
    回傳:
        對應的 Transformer 類別
    """
    transformer_map = {
        "tw": TWSEHistoryValueTransformer
    }
    return _get_transformer_by_zone("HistoryValue", zone, transformer_map)


def get_agent_overview_transformer(zone):
    """
    取得美股券商總覽（Agent Overview）對應地區的 Transformer 類別。
    參數:
        zone: "us"
    回傳:
        對應的 Transformer 類別
    """
    transformer_map = {
        "us": AgentOverviewTransformer
    }
    return _get_transformer_by_zone("AgentOverview", zone, transformer_map)


def get_tej_finance_statement_transformer(zone):
    """
    取得 TEJ 財報（TEJ Finance Statement）對應地區的 Transformer 類別。
    參數:
        zone: "tw"
    回傳:
        對應的 Transformer 類別
    """
    transformer_map = {
        "tw": TEJFinanceStatementTransformer
    }
    return _get_transformer_by_zone("TEJFinanceStatement", zone, transformer_map)

# === 共用內部工具 ===
def _get_transformer_by_zone(name: str, zone: str, transformer_map: dict):
    """
    根據 zone 回傳對應的 Transformer 類別，若 zone 不支援則拋出 NotSupportedError。
    參數:
        name: 字串，Transformer 名稱（用於錯誤訊息）
        zone: 地區代碼
        transformer_map: dict，zone 對應的 Transformer 類別
    回傳:
        對應的 Transformer 類別
    """
    transformer = transformer_map.get(zone)
    if not transformer:
        raise NotSupportedError(
            f"[transformer_factory] {name} Transformer only supports {list(transformer_map.keys())}, got '{zone}'"
        )
    return transformer
