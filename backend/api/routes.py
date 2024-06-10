from fastapi import APIRouter, BackgroundTasks
from services.monitoring_service import MonitoringService
from services.config_service import ConfigService
from models.monitoring_model import MonitoringConfig, MonitoringData

router = APIRouter()

@router.post("/start-data-collection")
async def start_data_collection(background_tasks: BackgroundTasks):
    background_tasks.add_task(MonitoringService.collect_and_store_ont_data)
    return {"message": "Data collection started in the background"}

@router.post("/monitoring-data")
async def create_monitoring_data(data: MonitoringData):
    MonitoringService.create_monitoring_data(data)
    return {"message": "Monitoring data created successfully"}

@router.get("/monitoring-data/{device_id}")
async def get_monitoring_data_by_device(device_id: str):
    data = MonitoringService.get_monitoring_data_by_device(device_id)
    return data

@router.get("/monitoring-data")
async def get_monitoring_data(start_date: str = None, end_date: str = None):
    data = MonitoringService.get_monitoring_data(start_date, end_date)
    return data

@router.get("/monitoring-config")
async def get_monitoring_config():
    config = ConfigService.get_monitoring_config()
    return config

@router.put("/monitoring-config")
async def update_monitoring_config(config: MonitoringConfig):
    ConfigService.update_monitoring_config(config)
    return {"message": "Monitoring configuration updated successfully"}