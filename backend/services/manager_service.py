from typing import List, Optional, Dict, Any
from models.manager_model import BuildingModel, FloorModel, ONTModel
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
        print(f"Updating floor: building={building_name}, floor={floor_name}, data={floor}")
        
        # Crear un diccionario de actualización solo con los campos no nulos
        update_fields = {f"floors.$.{key}": value for key, value in floor.dict().items() if value is not None}
        
        # Realizar la actualización solo con los campos no nulos
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
    def add_ont_to_floor(building_name: str, floor_name: str, ont: ONTModel):
        manager_collection.update_one(
            {"name": building_name, "floors.name": floor_name},
            {"$push": {"floors.$.onts": ont.dict()}}
        )

    @staticmethod
    def get_ont_by_name(building_name: str, floor_name: str, ont_serial: str) -> Optional[ONTModel]:
        building = manager_collection.find_one(
            {"name": building_name, "floors.name": floor_name, "floors.onts.name": ont_serial},
            {"floors.$": 1}
        )
        if building and building["floors"] and building["floors"][0]["onts"]:
            ont = next((o for o in building["floors"][0]["onts"] if o["name"] == ont_serial), None)
            if ont:
                return ONTModel(**ont)
        return None

    @staticmethod
    def update_ont(building_name: str, floor_name: str, ont_serial: str, ont: ONTModel):
        manager_collection.update_one(
            {"name": building_name, "floors.name": floor_name, "floors.onts.name": ont_serial},
            {"$set": {"floors.$[floor].onts.$[ont]": ont.dict()}},
            array_filters=[{"floor.name": floor_name}, {"ont.name": ont_serial}]
        )

    @staticmethod
    def delete_ont(building_name: str, floor_name: str, ont_serial: str):
        manager_collection.update_one(
            {"name": building_name, "floors.name": floor_name},
            {"$pull": {"floors.$.onts": {"serial": ont_serial}}}
        )

    # Nuevo método para actualizar el geoJsonData de un piso
    @staticmethod
    def update_floor_geojson(building_name: str, floor_name: str, geojson_data: Dict[str, Any]):
        manager_collection.update_one(
            {"name": building_name, "floors.name": floor_name},
            {"$set": {"floors.$.geoJsonData": geojson_data}}
        )