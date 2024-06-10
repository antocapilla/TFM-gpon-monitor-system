from database.database import collection
from models.monitoring_data import MonitoringData

class MonitoringService:
    @staticmethod
    def create_monitoring_data(data: MonitoringData):
        collection.insert_one(data.dict())

    @staticmethod
    def get_monitoring_data():
        data = list(collection.find())
        # Convertir los ObjectId a cadenas de texto
        for item in data:
            item["_id"] = str(item["_id"])
        return data
    
    @staticmethod
    def get_monitoring_data_by_device(device_id: str):
        data = list(collection.find({"device_id": device_id}))
        for item in data:
            item["_id"] = str(item["_id"])
        return data
    
    @staticmethod
    def get_monitoring_data(start_date: str = None, end_date: str = None):
        query = {}
        if start_date and end_date:
            query["timestamp"] = {"$gte": start_date, "$lte": end_date}
        elif start_date:
            query["timestamp"] = {"$gte": start_date}
        elif end_date:
            query["timestamp"] = {"$lte": end_date}

        data = list(collection.find(query))
        for item in data:
            item["_id"] = str(item["_id"])
        return data