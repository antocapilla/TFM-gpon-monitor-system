from fastapi import APIRouter, BackgroundTasks, Query
from typing import List, Optional
from datetime import datetime
from services.monitoring_service import MonitoringService
from models.monitoring_model import ONTData, MonitoringConfig

router = APIRouter()

@router.post("/collect-data")
async def start_data_collection(background_tasks: BackgroundTasks):
    background_tasks.add_task(MonitoringService.collect_and_store_ont_data)
    return {"message": "ONT data collection started in the background"}

@router.post("/store-data")
async def store_monitoring_data(data: List[ONTData]):
    MonitoringService.create_monitoring_data(data)
    return {"message": "ONT monitoring data stored successfully"}

@router.delete("/delete")
def delete_monitoring_data(
    building: str = Query(None),
    floor: str = Query(None),
    serial: str = Query(None)
):
    result = MonitoringService.delete_monitoring_data(building, floor, serial)
    return {
        "message": f"Datos eliminados correctamente. {result['deleted_count']} documentos borrados.",
        "onts_affected": result['onts_affected']
    }

@router.get("/time-series/")
async def get_time_series_data(
    serial: Optional[str] = None,
    floor: Optional[str] = None,
    building: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    interval: str = 'hour'
):
    data = MonitoringService.get_time_series_data(
        serial=serial,
        floor=floor,
        building=building,
        start_date=start_date,
        end_date=end_date,
        interval=interval
    )
    return data

@router.get("/latest-values")
async def get_latest_values(
    serial: Optional[str] = None,
    floor: Optional[str] = None,
    building: Optional[str] = None
):
    data = MonitoringService.get_latest_values(
        serial=serial,
        floor=floor,
        building=building
    )
    return data

@router.get("/config")
async def get_monitoring_config():
    config = MonitoringService.get_monitoring_config()
    return config

@router.put("/config")
async def update_monitoring_config(config: MonitoringConfig):
    MonitoringService.update_monitoring_config(config)
    return {"message": "Monitoring configuration updated successfully"}

