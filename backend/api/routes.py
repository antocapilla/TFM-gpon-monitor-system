from fastapi import APIRouter
from models.monitoring_data import MonitoringData
from services.monitoring_service import MonitoringService

router = APIRouter()

@router.post("/monitoring-data")
async def create_monitoring_data(data: MonitoringData):
    MonitoringService.create_monitoring_data(data)
    return {"message": "Monitoring data created successfully"}

@router.get("/monitoring-data")
async def get_monitoring_data():
    data = MonitoringService.get_monitoring_data()
    return data

@router.get("/monitoring-data/{device_id}")
async def get_monitoring_data_by_device(device_id: str):
    data = MonitoringService.get_monitoring_data_by_device(device_id)
    return data

@router.get("/monitoring-data")
async def get_monitoring_data(start_date: str = None, end_date: str = None):
    data = MonitoringService.get_monitoring_data(start_date, end_date)
    return data