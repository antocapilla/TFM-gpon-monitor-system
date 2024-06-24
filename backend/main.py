from fastapi import FastAPI
from api.manager_routes import router as manager_router
from api.monitoring_routes import router as monitoring_router

app = FastAPI()

app.include_router(manager_router, prefix="/manager", tags=["manager"])
app.include_router(monitoring_router, prefix="/monitoring", tags=["monitoring"])

# @app.on_event("startup")
# async def startup_event():
#     start_scheduler()