from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client["network_management_db"]

# Colecciones para el monitoreo de dispositivos
monitoring_data_collection = db["monitoring_data"]
monitoring_config_collection = db["monitoring_config"]

# Colecciones para la gestión de edificios y ONTs
manager_collection = db["manager"]
buildings_collection = db["buildings"]
floors_collection = db["floors"]
onts_collection = db["onts"]