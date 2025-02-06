from pymongo import MongoClient
from config import Config

class Database:
    _instance = None
    _client = None
    _db = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if Database._client is None:
            Database._client = MongoClient(Config.MONGODB_URI)
            Database._db = Database._client[Config.DATABASE_NAME]

    @property
    def db(self):
        return Database._db

    def get_collection(self, collection_name):
        return self.db[collection_name]

    def close(self):
        if Database._client:
            Database._client.close()
            Database._client = None
            Database._db = None