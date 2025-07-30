from .base import BaseDailyTechDBExtractor


class AsyncTEJDailyTechDBExtractor(BaseDailyTechDBExtractor):

    def __init__(self, ticker, client):
        super().__init__(ticker, client)

    def _get_collection_name(self):
        self.collection_name_map = {"tw": "TEJ_share_price"}

        return self.collection_name_map.get(self.zone, None)
