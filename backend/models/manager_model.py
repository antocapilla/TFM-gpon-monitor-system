from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ONTPosition(BaseModel):
    serial: str
    x: Optional[float] = None
    y: Optional[float] = None

class FloorModel(BaseModel):
    name: str
    url: Optional[str] = None
    geoJsonData: Optional[Dict[str, Any]] = None
    onts: List[ONTPosition] = []
    scale: Optional[float] = None
    
class BuildingModel(BaseModel):
    name: str
    floors: List[FloorModel] = []

class ManagerModel(BaseModel):
    buildings: List[BuildingModel] = []