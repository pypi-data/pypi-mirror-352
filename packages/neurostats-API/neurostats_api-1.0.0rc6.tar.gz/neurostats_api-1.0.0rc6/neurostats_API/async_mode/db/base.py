from pymongo import AsyncMongoClient

class BaseDBClient:
    def __init__(self, client:  AsyncMongoClient, zone= None):
        self.client = client
        self.zone = zone or "tw"  # 預設台灣
        self.db = self._select_db()

    def _select_db(self):
        """
        根據 zone 選擇對應的資料庫
        """
        zone_db_map = {
            "tw": "company_test",
            "us": "company_us"
        }
        db_name = zone_db_map.get(self.zone, "company_test")
        return self.client[db_name]

    def get_collection(self, collection_name: str):
        """
        傳回指定 collection
        """
        return self.db[collection_name]
