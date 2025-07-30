from .base import BaseDBClient
import os
from pymongo import AsyncMongoClient
from dotenv import load_dotenv

class USDBClient(BaseDBClient):
    def __init__(self, client):
        """初始化時接收 MongoDB 連接 URI"""
        super().__init__(client, zone = 'us')