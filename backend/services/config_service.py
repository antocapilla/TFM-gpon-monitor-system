from database.database import config_collection
from models.monitoring_model import MonitoringConfig

class ConfigService:
    @staticmethod
    def get_monitoring_config():
        config = config_collection.find_one()
        if config:
            return MonitoringConfig(**config)
        else:
            # Si no existe una configuración, crear una predeterminada
            default_config = MonitoringConfig()
            config_collection.insert_one(default_config.dict())
            return default_config

    @staticmethod
    def update_monitoring_config(config: MonitoringConfig):
        config_collection.update_one({}, {"$set": config.dict()}, upsert=True)