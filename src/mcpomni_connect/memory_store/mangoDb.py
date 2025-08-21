from pymongo import MongoClient

class MangoDb:
    def __init__(self, uri="mongodb://localhost:27017/", db_name="mcpomni_connect"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    def get_collection(self, collection_name: str):
        return self.db[collection_name]
    
    def insert_one(self, collection_name: str, data: dict):