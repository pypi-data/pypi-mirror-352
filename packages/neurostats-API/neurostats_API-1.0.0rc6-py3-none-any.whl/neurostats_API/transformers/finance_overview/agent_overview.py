from .base import BaseFinanceOverviewTransformer

class AgentOverviewTransformer(BaseFinanceOverviewTransformer):
    def __init__(self, ticker, company_name, zone):
        super().__init__(ticker, company_name, zone)
    
    def process_transform(self, tech_data, balance_sheet_list, profit_lose_list, cash_flow_list):
        """
        tech_data: tech_fetcher回傳的技術面資料 (pd.DataFrame)
        seasonal_data: 一系列的balance_sheet, profit_lose, cash_flow
        """
        seasonal_data = [
            {
                **balance_sheet['balance_sheet'],
                **profit_lose['income_statement'],
                **cash_flow['cash_flow']
            } for balance_sheet, profit_lose, cash_flow in zip(
                balance_sheet_list,
                profit_lose_list,
                cash_flow_list
            )
        ]

        TTM_data = self._get_TTM_data(seasonal_data)

        return_dict = {
            "date":
            self._get_latest_date(tech_data),
            "ticker":
            self.ticker,
            "company_name":self.company_name,
            "category":
            self._get_category(),
            "market_open":
            self._is_us_market_open(),
            "latest_close":
            self._get_latest_close(tech_data),
            "close_offset":
            self._get_latest_offset(tech_data).get("value", "0.0"),
            "close_offset_percentage":
            self._get_latest_offset(tech_data).get("percentage", "0.0%"),
            "latest_volume":
            self._get_latest_volume(tech_data),
            "average_volume":
            self._get_latest_average_volume(tech_data, 30),
            "market_capitalzation":
            self._get_market_capitalization(tech_data, seasonal_data),
            "P_E":
            self._get_PE(tech_data, TTM_data),
            "P_S":
            self._get_PS(tech_data, TTM_data, seasonal_data),
        }

        return return_dict
        