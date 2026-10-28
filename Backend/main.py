from contextlib import asynccontextmanager
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.receptionist import router as receptionist_router
from app.core.limiter import limiter
from app.database.mongodb import (
    connect_to_mongodb,
    close_mongodb_connection,
)

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongodb()
    try:
        yield
    finally:
        await close_mongodb_connection()


app = FastAPI(
    title="Dental Clinic AI Receptionist",
    description="Backend API for a dental clinic AI receptionist",
    version="1.0.0",
    lifespan=lifespan,
            )

# --- CORS ---
# Comma-separated origins in .env, e.g. "http://localhost:3000,https://app.example.com"
# Defaults to "*" for local development.
allowed_origins_raw = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = (
    [o.strip() for o in allowed_origins_raw.split(",") if o.strip()]
    if allowed_origins_raw != "*"
    else ["*"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Rate limiting ---
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)


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
