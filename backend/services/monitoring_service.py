import requests
from database.database import collection
from models.monitoring_model import MonitoringData
from config import SWH_API_URL, SWH_API_USERNAME, SWH_API_PASSWORD
from pydantic import BaseModel
from services.config_service import ConfigService

class MonitoringService:
    @staticmethod
    def create_monitoring_data(data: MonitoringData):
        collection.insert_one(data.dict())

    @staticmethod
    def collect_and_store_ont_data():
        config = ConfigService.get_monitoring_config()
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
                collection.insert_one(monitoring_model.dict())

            print("ONT data collected and stored successfully")
        except requests.exceptions.RequestException as e:
            print(f"Error collecting ONT data from SWH API: {e}")
        except Exception as e:
            print(f"Error storing ONT data: {e}")
    
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
    
class MonitoringConfig(BaseModel):
    enabled: bool = True
    interval: int = 300
    # Agrega otros parámetros de configuración según tus necesidades