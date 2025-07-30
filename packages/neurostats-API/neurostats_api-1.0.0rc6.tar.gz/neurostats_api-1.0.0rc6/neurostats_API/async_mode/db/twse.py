from .base import BaseDBClient
import os
from pymongo import AsyncMongoClient
from dotenv import load_dotenv

class TWSEDBClient(BaseDBClient):
    def __init__(self, client):
        super().__init__(client, zone= "tw")