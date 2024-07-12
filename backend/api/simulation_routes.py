from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from services.simulation_service import SimulationService
from services.manager_service import ManagerService

router = APIRouter()
simulation_service = SimulationService()
manager_service = ManagerService()

class SimulationRequest(BaseModel):
    building_name: str
    floor_name: str

@router.post("/run-simulation")
async def run_simulation(request: SimulationRequest):
    try:
        # Obtener datos del piso usando ManagerService
        floor_data = manager_service.get_floor_by_name(request.building_name, request.floor_name)
        
        if not floor_data:
            raise HTTPException(status_code=404, detail="Floor not found")

        geojson_data = floor_data.geoJsonData if floor_data.geoJsonData else {}
        onts = floor_data.onts if floor_data.onts else []
        scale = floor_data.scale if floor_data.scale else 1.0

        print("GeoJSON data:", geojson_data)
        print("ONTs:", onts)
        print("Scale:", scale)

        # Ejecutar la simulación
        simulation_result = simulation_service.run_simulation(geojson_data, onts, scale)

        return {
            "message": "Simulation completed successfully",
            "result": simulation_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))