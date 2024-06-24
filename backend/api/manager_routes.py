from fastapi import APIRouter
from services.manager_service import ManagerService
from models.manager_model import BuildingModel, FloorModel, ONTModel

router = APIRouter()

# Building Routes
@router.get("/buildings")
async def get_all_buildings():
    buildings = ManagerService.get_all_buildings()
    return buildings

@router.post("/buildings")
async def create_building(building: BuildingModel):
    created_building = ManagerService.create_building(building)
    return created_building

@router.get("/buildings/{building_name}")
async def get_building_by_name(building_name: str):
    building = ManagerService.get_building_by_name(building_name)
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

@router.get("/buildings/{building_name}/floors/{floor_name}")
async def get_floor_by_name(building_name: str, floor_name: str):
    floor = ManagerService.get_floor_by_name(building_name, floor_name)
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
@router.post("/buildings/{building_name}/floors/{floor_name}/onts")
async def add_ont_to_floor(building_name: str, floor_name: str, ont: ONTModel):
    ManagerService.add_ont_to_floor(building_name, floor_name, ont)
    return {"message": "ONT added to floor successfully"}

@router.get("/buildings/{building_name}/floors/{floor_name}/onts/{ont_name}")
async def get_ont_by_name(building_name: str, floor_name: str, ont_name: str):
    ont = ManagerService.get_ont_by_name(building_name, floor_name, ont_name)
    return ont

@router.put("/buildings/{building_name}/floors/{floor_name}/onts/{ont_name}")
async def update_ont(building_name: str, floor_name: str, ont_name: str, ont: ONTModel):
    ManagerService.update_ont(building_name, floor_name, ont_name, ont)
    return {"message": "ONT updated successfully"}

@router.delete("/buildings/{building_name}/floors/{floor_name}/onts/{ont_name}")
async def delete_ont(building_name: str, floor_name: str, ont_name: str):
    ManagerService.delete_ont(building_name, floor_name, ont_name)
    return {"message": "ONT deleted successfully"}