from pymongo import MongoClient

def get_db():
    client = MongoClient("mongodb+srv://sofia:Qs6EBv98YKUljnKH@cluster0.swmafyy.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client["sofias_platform"]
    return db

def get_collection(collection_name):
    db = get_db()
    collection = db[collection_name]  
    return collection
