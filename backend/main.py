from config import FRONTEND_URL
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from api.manager_routes import router as manager_router
from api.monitoring_routes import router as monitoring_router
from api.simulation_routes import router as simulation_routes
from api.file_routes import router as file_router
import os
from socketio import AsyncServer, ASGIApp
import logging

# Configurar el nivel de logging global a INFO
logging.basicConfig(level=logging.INFO)

# Desactivar los mensajes de depuración de PyMongo
logger = logging.getLogger("pymongo").setLevel(logging.WARNING)

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