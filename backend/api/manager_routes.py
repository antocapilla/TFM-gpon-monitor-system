from fastapi import APIRouter, HTTPException
from typing import List
from models.manager_model import BuildingModel, FloorModel, ONTPosition
from services.manager_service import ManagerService

router = APIRouter()

# Building Routes
@router.post("/buildings", response_model=str)
async def create_building(building: BuildingModel):
    return ManagerService.create_building(building)

@router.get("/buildings", response_model=List[BuildingModel])
async def get_all_buildings():
    return ManagerService.get_all_buildings()

@router.get("/buildings/{building_name}", response_model=BuildingModel)
async def get_building_by_name(building_name: str):
    building = ManagerService.get_building_by_name(building_name)
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    return building

@router.put("/buildings/{building_name}")
async def update_building(building_name: str, building: BuildingModel):
    ManagerService.update_building(building_name, building)
    return {"message": "Building updated successfully"}

@router.delete("/buildings/{building_name}")
async def delete_building(building_name: str):
    ManagerService.delete_building(building_name)
    return {"message": "Building deleted successfully"}

# Floor Routes
@router.post("/buildings/{building_name}/floors")
async def add_floor_to_building(building_name: str, floor: FloorModel):
    ManagerService.add_floor_to_building(building_name, floor)
    return {"message": "Floor added to building successfully"}

@router.get("/buildings/{building_name}/floors/{floor_name}", response_model=FloorModel)
async def get_floor_by_name(building_name: str, floor_name: str):
    floor = ManagerService.get_floor_by_name(building_name, floor_name)
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")
    return floor

@router.put("/buildings/{building_name}/floors/{floor_name}")
async def update_floor(building_name: str, floor_name: str, floor: FloorModel):
    ManagerService.update_floor(building_name, floor_name, floor)
    return {"message": "Floor updated successfully"}

@router.delete("/buildings/{building_name}/floors/{floor_name}")
async def delete_floor(building_name: str, floor_name: str):
    ManagerService.delete_floor(building_name, floor_name)
    return {"message": "Floor deleted successfully"}

# ONT Routes
@router.get("/available-onts")
async def get_available_onts():
    return ManagerService.get_available_onts()
    
@router.post("/buildings/{building_name}/floors/{floor_name}/onts")
async def add_ont_to_floor(building_name: str, floor_name: str, ont: ONTPosition):
    ManagerService.add_ont_to_floor(building_name, floor_name, ont)
    return {"message": "ONT added to floor successfully"}

@router.get("/buildings/{building_name}/floors/{floor_name}/onts/{ont_serial}", response_model=ONTPosition)
async def get_ont_by_serial(building_name: str, floor_name: str, ont_serial: str):
    ont = ManagerService.get_ont_by_serial(building_name, floor_name, ont_serial)
    if not ont:
        raise HTTPException(status_code=404, detail="ONT not found")
    return ont

@router.put("/buildings/{building_name}/floors/{floor_name}/onts/{ont_serial}")
async def update_ont_position(building_name: str, floor_name: str, ont_serial: str, ont_position: ONTPosition):
    ManagerService.update_ont_position(building_name, floor_name, ont_serial, ont_position.x, ont_position.y)
    return {"message": "ONT position updated successfully"}

@router.delete("/buildings/{building_name}/floors/{floor_name}/onts/{ont_serial}")
async def delete_ont(building_name: str, floor_name: str, ont_serial: str):
    ManagerService.delete_ont(building_name, floor_name, ont_serial)
    return {"message": "ONT deleted successfully"}

# GeoJSON Route
@router.put("/buildings/{building_name}/floors/{floor_name}/geojson")
async def update_floor_geojson(building_name: str, floor_name: str, geojson_data: dict):
    ManagerService.update_floor_geojson(building_name, floor_name, geojson_data)
    return {"message": "Floor GeoJSON data updated successfully"}