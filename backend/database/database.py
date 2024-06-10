from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client["hotel_monitoring"]
collection = db["monitoring_data"]