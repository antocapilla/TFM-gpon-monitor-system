from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client["monitoring_db"]
collection = db["monitoring_data"]
config_collection = db["monitoring_config"]