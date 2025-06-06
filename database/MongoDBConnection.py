from pymongo import MongoClient

class MongoDBConnection:
    def __init__(self, host: str = 'localhost', port: int = 27017, db_name: str = 'userbot'):
        self.client = MongoClient(host, port)
        self.db = self.client[db_name]

    def close(self):
        self.client.close()