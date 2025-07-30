from .base import BaseDBClient
import os
from pymongo import AsyncMongoClient
from dotenv import load_dotenv

class TEJDBClient(BaseDBClient):
    def __init__(self, mongo_uri):
        """初始化時接收 MongoDB 連接 URI"""
        super().__init__(mongo_uri, zone = 'tw')
        self.db = self.client["company_test"]