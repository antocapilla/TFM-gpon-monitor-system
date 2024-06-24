from database.database import monitoring_config_collection
from models.monitoring_model import MonitoringConfig

class ConfigService:
    @staticmethod
    def get_monitoring_config():
        config = monitoring_config_collection.find_one()
        if config:
            return MonitoringConfig(**config)
        else:
            # Si no existe una configuración, crear una predeterminada
            default_config = MonitoringConfig()
            monitoring_config_collection.insert_one(default_config.dict())
            return default_config

    @staticmethod
    def update_monitoring_config(config: MonitoringConfig):
        monitoring_config_collection.update_one({}, {"$set": config.dict()}, upsert=True)