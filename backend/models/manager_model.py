from pydantic import BaseModel, Field
from typing import List, Optional

class ONTModel(BaseModel):
    name: str
    connected_users: int
    bandwidth: int
    uptime: float

class FloorModel(BaseModel):
    name: str
    url: Optional[str] = None
    drawings: List[str] = []
    onts: List[ONTModel] = []

class BuildingModel(BaseModel):
    name: str
    floors: List[FloorModel] = []

class ManagerModel(BaseModel):
    buildings: List[BuildingModel] = []