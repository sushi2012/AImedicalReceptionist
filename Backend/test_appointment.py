
import asyncio
from datetime import datetime, timedelta, timezone

from app.database.mongodb import (
    connect_to_mongodb,
    close_mongodb_connection,
)
from app.services.appointment_service import create_appointment


async def main():
    await connect_to_mongodb()

    try:
        start = datetime.now(timezone.utc) + timedelta(days=1)
        start = start.replace(hour=5, minute=30, second=0, microsecond=0)

        appointment_data = {
            "patient_name": "Test Patient",
            "patient_phone": "9876543210",
            "service": "Dental cleaning",
            "start_time": start.isoformat(),
            "end_time": (start + timedelta(minutes=30)).isoformat(),
            "doctor_id": "doctor_001",
            "reason": "Routine cleaning",
        }

        result = await create_appointment(appointment_data)
        print(result)
    finally:
        await close_mongodb_connection()


asyncio.run(main())
