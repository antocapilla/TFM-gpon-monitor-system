from fastapi import FastAPI
from api.routes import router
from services.scheduler import start_scheduler

app = FastAPI()
app.include_router(router)

# @app.on_event("startup")
# async def startup_event():
#     start_scheduler()