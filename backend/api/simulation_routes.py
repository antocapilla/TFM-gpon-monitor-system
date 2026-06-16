from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from services.simulation_service import SimulationService
from services.manager_service import ManagerService

router = APIRouter()
simulation_service = SimulationService()
manager_service = ManagerService()

# Palabra clave que identifica la simulación de asignación de canales.
_CHANNEL_KEYWORD = "canal"


class SimulationRequest(BaseModel):
    building_name: str
    floor_name: str
    simulation_type: Optional[str] = None


@router.post("/run-simulation")
async def run_simulation(request: SimulationRequest):
    # Obtener datos del piso usando ManagerService
    floor_data = manager_service.get_floor_by_name(request.building_name, request.floor_name)
    if not floor_data:
        raise HTTPException(status_code=404, detail="Floor not found")

    geojson_data = floor_data.geoJsonData or {}
    onts = floor_data.onts or []
    scale = floor_data.scale or 1.0

    is_channel_sim = bool(request.simulation_type) and _CHANNEL_KEYWORD in request.simulation_type.lower()

    try:
        if is_channel_sim:
            # Solo asignación de canales: evita el coste del ray tracing.
            result = {
                "channelAllocation": simulation_service.allocate_wifi_channels(onts, scale),
                "onts": [{"serial": o.serial, "name": o.serial, "x": o.x, "y": o.y} for o in onts],
            }
        else:
            # Propagación de señal (heatmap) + canales.
            result = simulation_service.run_simulation(geojson_data, onts, scale)
    except ValueError as e:
        # Datos de entrada insuficientes/incorrectos (GeoJSON vacío, sin ONT, ...).
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": "Simulation completed successfully", "result": result}
