from fastapi import FastAPI

from app.api.receptionist import router as receptionist_router

app = FastAPI(
    title="Dental Clinic AI Receptionist",
    description="Backend API for a dental clinic AI receptionist",
    version="1.0.0",
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
