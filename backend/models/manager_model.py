from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class ONTModel(BaseModel):
    serial: str
    connected_users: int
    bandwidth: int
    uptime: float
    ip_address: Optional[str] = None
    hosts: List[str] = []

class FloorModel(BaseModel):
    name: str
    url: Optional[str] = None
    geoJsonData: Optional[Dict[str, Any]] = None  # Cambiado de drawings a geoJsonData
    onts: List[ONTModel] = []

class BuildingModel(BaseModel):
    name: str
    floors: List[FloorModel] = []

class ManagerModel(BaseModel):
    buildings: List[BuildingModel] = []