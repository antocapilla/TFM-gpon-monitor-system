from pydantic import BaseModel
from typing import List, Optional

class SimulationParameters(BaseModel):
    num_rays: int
    max_path_loss: float
    max_reflections: int
    max_transmissions: int
    tx_power: float
    frequency: float

class SimulationResult(BaseModel):
    received_power: List[List[float]]
    rays_data: List[dict]
    walls_data: List[dict]

class Simulation(BaseModel):
    id: Optional[str] = None
    building_name: str
    floor_name: str
    parameters: SimulationParameters
    result: Optional[SimulationResult] = None
    status: str = "pending"  # pending, running, completed, failed