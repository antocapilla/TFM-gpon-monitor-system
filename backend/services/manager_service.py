from typing import List, Optional, Dict, Any
from services.swh_service import SWHService
from models.manager_model import BuildingModel, FloorModel, ONTPosition
from database.database import manager_collection

class ManagerService:
    @staticmethod
    def create_building(building: BuildingModel):
        result = manager_collection.insert_one(building.dict())
        return str(result.inserted_id)

    @staticmethod
    def get_all_buildings() -> List[BuildingModel]:
        buildings = list(manager_collection.find())
        return [BuildingModel(**building) for building in buildings]

    @staticmethod
    def get_building_by_name(name: str) -> Optional[BuildingModel]:
        building = manager_collection.find_one({"name": name})
        return BuildingModel(**building) if building else None

    @staticmethod
    def update_building(name: str, building: BuildingModel):
        manager_collection.replace_one({"name": name}, building.dict(), upsert=True)

    @staticmethod
    def delete_building(name: str):
        manager_collection.delete_one({"name": name})

    @staticmethod
    def add_floor_to_building(building_name: str, floor: FloorModel):
        manager_collection.update_one(
            {"name": building_name},
            {"$push": {"floors": floor.dict()}}
        )

    @staticmethod
    def get_floor_by_name(building_name: str, floor_name: str) -> Optional[FloorModel]:
        building = manager_collection.find_one(
            {"name": building_name, "floors.name": floor_name},
            {"floors.$": 1}
        )
        if building and building.get("floors"):
            return FloorModel(**building["floors"][0])
        return None

    @staticmethod
    def update_floor(building_name: str, floor_name: str, floor: FloorModel):
        update_fields = {f"floors.$.{key}": value for key, value in floor.dict().items() if value is not None}
        manager_collection.update_one(
            {"name": building_name, "floors.name": floor_name},
            {"$set": update_fields}
        )

    @staticmethod
    def delete_floor(building_name: str, floor_name: str):
        manager_collection.update_one(
            {"name": building_name},
            {"$pull": {"floors": {"name": floor_name}}}
        )

    @staticmethod
    def get_available_onts():
        # Obtener todas las ONTs
        all_onts = ManagerService.get_all_onts()
        
        # Crear un conjunto de seriales de ONTs asignadas
        assigned_ont_serials = {ont['serial'] for ont in all_onts}
        
        # Obtener todas las ONTs disponibles del SWH
        all_available_onts = SWHService.get_available_onts()
        
        # Filtrar las ONTs que no están asignadas
        available_onts = [ont for ont in all_available_onts if ont not in assigned_ont_serials]
        
        return available_onts

    @staticmethod
    def add_ont_to_floor(building_name: str, floor_name: str, ont: ONTPosition):
        manager_collection.update_one(
            {"name": building_name, "floors.name": floor_name},
            {"$push": {"floors.$.onts": ont.dict()}}
        )

    @staticmethod
    def update_ont_position(building_name: str, floor_name: str, ont_serial: str, x: float, y: float):
        manager_collection.update_one(
            {"name": building_name, "floors.name": floor_name, "floors.onts.serial": ont_serial},
            {"$set": {"floors.$[floor].onts.$[ont].x": x, "floors.$[floor].onts.$[ont].y": y}},
            array_filters=[{"floor.name": floor_name}, {"ont.serial": ont_serial}]
        )

    @staticmethod
    def get_all_onts():
        buildings = manager_collection.find()
        all_onts = []
        for building in buildings:
            for floor in building.get('floors', []):
                all_onts.extend(floor.get('onts', []))
        return all_onts

    @staticmethod
    def get_onts_for_building(building_name: str):
        building = manager_collection.find_one({"name": building_name})
        if not building:
            return []
        return [ont for floor in building.get('floors', []) for ont in floor.get('onts', [])]

    @staticmethod
    def get_onts_for_floor(building_name: str, floor_name: str):
        building = manager_collection.find_one(
            {"name": building_name, "floors.name": floor_name},
            {"floors.$": 1}
        )
        if not building or not building.get('floors'):
            return []
        return building['floors'][0].get('onts', [])

    @staticmethod
    def get_ont_by_serial(building_name: str, floor_name: str, ont_serial: str) -> Optional[ONTPosition]:
        building = manager_collection.find_one(
            {"name": building_name, "floors.name": floor_name, "floors.onts.serial": ont_serial},
            {"floors.$": 1}
        )
        if building and building["floors"] and building["floors"][0]["onts"]:
            ont = next((o for o in building["floors"][0]["onts"] if o["serial"] == ont_serial), None)
            if ont:
                return ONTPosition(**ont)
        return None

    @staticmethod
    def update_ont_position(building_name: str, floor_name: str, ont_serial: str, x: float, y: float):
        manager_collection.update_one(
            {"name": building_name, "floors.name": floor_name, "floors.onts.serial": ont_serial},
            {"$set": {"floors.$[floor].onts.$[ont].x": x, "floors.$[floor].onts.$[ont].y": y}},
            array_filters=[{"floor.name": floor_name}, {"ont.serial": ont_serial}]
        )

    @staticmethod
    def delete_ont(building_name: str, floor_name: str, ont_serial: str):
        manager_collection.update_one(
            {"name": building_name, "floors.name": floor_name},
            {"$pull": {"floors.$.onts": {"serial": ont_serial}}}
        )

    @staticmethod
    def update_floor_geojson(building_name: str, floor_name: str, geojson_data: Dict[str, Any]):
        manager_collection.update_one(
            {"name": building_name, "floors.name": floor_name},
            {"$set": {"floors.$.geoJsonData": geojson_data}}
        )