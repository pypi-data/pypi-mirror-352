from .base import BaseDailyTechDBExtractor


class AsyncYFDailyTechDBExtractor(BaseDailyTechDBExtractor):

    def __init__(self, ticker, client):
        super().__init__(ticker, client)

    def _get_collection_name(self):
        self.collection_name_map = {"tw": "twse_daily_share_price", "us": "us_technical"}

        return self.collection_name_map.get(self.zone, None)
