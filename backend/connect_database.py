from pymongo import MongoClient


class MongoConnection:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client['stackoverflow']
        self.collection = None

    def get_collection(self, name):
        self.collection = self.db[name]

    def save(self, obj):
        if len(obj) > 0 and isinstance(obj, dict):
            insert_id = self.collection.insert_one(obj).inserted_id
            return insert_id

    def remove(self, obj):
        if len(obj) > 0 and isinstance(obj, dict):
            self.collection.delete_one({"_id": obj.get("_id")})

    def update(self, obj, data):
        if len(obj) > 0 and isinstance(obj, dict):
            self.collection.update_one({"_id": obj.get("_id")}, {"$set": data})