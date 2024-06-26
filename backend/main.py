from config import FRONTEND_URL
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from api.manager_routes import router as manager_router
from api.monitoring_routes import router as monitoring_router
from api.simulation_routes import router as simulation_routes
from api.file_routes import router as file_router
from services.simulation_service import SimulationService
import os
from socketio import AsyncServer, ASGIApp
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(manager_router, prefix="/manager", tags=["manager"])
app.include_router(monitoring_router, prefix="/monitoring", tags=["monitoring"])
app.include_router(simulation_routes, prefix="/simulator", tags=["simulation"])
app.include_router(file_router, prefix="/files", tags=["files"])

# Configurar SocketIO
sio = AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = ASGIApp(sio)
app.mount("/socket.io", socket_app)

# Verificar si el directorio 'uploads' existe
if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
else:
    logger.warning("'uploads' directory does not exist. File uploads may not work correctly.")

@sio.on('connect')
async def connect(sid, environ):
    logger.info(f"Client connected: {sid}")

@sio.on('disconnect')
async def disconnect(sid):
    logger.info(f"Client disconnected: {sid}")

@sio.on('start_simulation')
async def handle_start_simulation(sid, data):
    logger.info(f"Received simulation request from {sid}")
    config = data.get('config')
    building_name = data.get('building')
    floor_name = data.get('floor')
    
    if not all([config, building_name, floor_name]):
        await sio.emit('simulation_error', {'error': 'Missing required data'}, room=sid)
        return
    
    logger.info(f"Starting simulation for building: {building_name}, floor: {floor_name}")
    await SimulationService.run_simulation(sio, sid, config, building_name, floor_name)

# Función para emitir el progreso
async def emit_progress(simulation_id, progress):
    await sio.emit('simulation_progress', {'simulation_id': simulation_id, 'progress': progress})