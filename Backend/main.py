from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.agents.receptionist import get_receptionist
from app.api.receptionist import router as receptionist_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await get_receptionist()
    yield


app = FastAPI(
    title="Dental Clinic AI Receptionist",
    description="Backend API for a dental clinic AI receptionist",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
def home():
    return {
        "message": "Dental Clinic AI Receptionist API is running!"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


app.include_router(receptionist_router)
