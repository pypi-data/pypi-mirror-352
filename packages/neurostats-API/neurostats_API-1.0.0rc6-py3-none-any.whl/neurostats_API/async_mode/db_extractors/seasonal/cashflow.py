from .base import AsyncBaseSeasonalDBExtractor

class AsyncCashFlowExtractor(AsyncBaseSeasonalDBExtractor):
    def __init__(self, ticker, client):
        super().__init__(ticker, client)

        self.column_name_map = {
            'tw': "cash_flow",
            'us': "cash_flow"
        }