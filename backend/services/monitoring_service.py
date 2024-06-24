import requests
from database.database import monitoring_data_collection, monitoring_config_collection, buildings_collection, floors_collection, onts_collection
from services.manager_service import ManagerService
from models.monitoring_model import MonitoringData, MonitoringConfig
from config import SWH_API_URL, SWH_API_USERNAME, SWH_API_PASSWORD

class MonitoringService:
    @staticmethod
    def create_monitoring_data(data: MonitoringData):
        monitoring_data_collection.insert_one(data.dict())

    @staticmethod
    def get_monitoring_data_by_device(device_id: str):
        data = list(monitoring_data_collection.find({"device_id": device_id}))
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

        data = list(monitoring_data_collection.find(query))
        for item in data:
            item["_id"] = str(item["_id"])
        return data
    
    @staticmethod
    def get_latest_monitoring_data_of_floor(floor_id: str):
        floor = ManagerService.get_floor_by_id(floor_id)
        if not floor:
            return None

        ont_ids = [ont.id for ont in floor.onts]
        query = {"device_id": {"$in": ont_ids}}

        data = list(monitoring_data_collection.find(query).sort("timestamp", -1).limit(1))
        for item in data:
            item["_id"] = str(item["_id"])
        return data

    @staticmethod
    def get_latest_monitoring_data_of_building(building_id: str):
        building = ManagerService.get_building_by_id(building_id)
        if not building:
            return None

        ont_ids = []
        for floor in building.floors:
            ont_ids.extend(ont.id for ont in floor.onts)

        query = {"device_id": {"$in": ont_ids}}

        data = list(monitoring_data_collection.find(query).sort("timestamp", -1).limit(1))
        for item in data:
            item["_id"] = str(item["_id"])
        return data
    
    @staticmethod
    def collect_and_store_ont_data():
        config = MonitoringService.get_monitoring_config()
        if not config.enabled:
            print("Data collection is disabled. Skipping.")
            return

        try:
            response = requests.get(SWH_API_URL, auth=(SWH_API_USERNAME, SWH_API_PASSWORD))
            response.raise_for_status()
            onts_data = response.json()

            for ont_data in onts_data:
                monitoring_model = MonitoringData(
                    device_id=ont_data["device_id"],
                    timestamp=ont_data["timestamp"],
                    # ... mapear otros campos de los datos al modelo MonitoringData
                )
                monitoring_data_collection.insert_one(monitoring_model.dict())

            print("ONT data collected and stored successfully")
        except requests.exceptions.RequestException as e:
            print(f"Error collecting ONT data from SWH API: {e}")
        except Exception as e:
            print(f"Error storing ONT data: {e}")

    @staticmethod
    def get_monitoring_config():
        config_data = monitoring_config_collection.find_one()
        if config_data:
            return MonitoringConfig(**config_data)
        return MonitoringConfig()

    @staticmethod
    def update_monitoring_config(config: MonitoringConfig):
        monitoring_config_collection.update_one({}, {"$set": config.dict()}, upsert=True)