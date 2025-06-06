from pymongo import MongoClient

def get_database():
    # Use hardcoded connection for now to avoid Django settings issues
    client = MongoClient("mongodb://localhost:27017")
    return client["pos_system"]

def get_collection(collection_name):
    db = get_database()
    return db[collection_name]