from .base import AsyncBaseMonthlyDBExtractor

class AsyncTWSEMonthlyRevenueExtractor(AsyncBaseMonthlyDBExtractor):
    def __init__(self, ticker, client):
        super().__init__(ticker, client)
