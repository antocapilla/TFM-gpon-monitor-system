from fastapi import APIRouter, HTTPException
from models.simulation_model import Simulation, SimulationParameters
from services.simulation_service import SimulationService

router = APIRouter()

@router.post("/simulations")
async def create_simulation(simulation: Simulation):
    return await SimulationService.create_simulation(simulation)

@router.get("/simulations/{simulation_id}")
async def get_simulation(simulation_id: str):
    simulation = await SimulationService.get_simulation(simulation_id)
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return simulation

@router.post("/simulations/{simulation_id}/run")
async def run_simulation(simulation_id: str):
    simulation = await SimulationService.run_simulation(simulation_id)
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return simulation

@router.get("/simulations/{simulation_id}/status")
async def get_simulation_status(simulation_id: str):
    status = await SimulationService.get_simulation_status(simulation_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return {"status": status}