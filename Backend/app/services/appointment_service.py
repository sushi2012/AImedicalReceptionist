
# app/services/appointment_service.py

from datetime import datetime, timezone

from bson import ObjectId

from app.database.mongodb import get_database
from app.models.appointment import AppointmentCreate


def get_appointments_collection():
    """Return the appointments collection from MongoDB."""
    return get_database()["appointments"]


def serialize_appointment(document: dict) -> dict:
    """Convert MongoDB ObjectId into a JSON-friendly string."""
    document["id"] = str(document.pop("_id"))
    return document


async def check_availability(
    start_time: datetime,
    end_time: datetime,
    doctor_id: str | None = None,
    exclude_appointment_id: str | None = None,
) -> bool:
    """Return True if no confirmed appointment overlaps the slot."""

    if start_time.tzinfo is None or start_time.utcoffset() is None:
        raise ValueError("start_time must include a timezone")

    if end_time.tzinfo is None or end_time.utcoffset() is None:
        raise ValueError("end_time must include a timezone")

    start_time = start_time.astimezone(timezone.utc)
    end_time = end_time.astimezone(timezone.utc)

    if end_time <= start_time:
        raise ValueError("end_time must be after start_time")

    query = {
        "status": "confirmed",
        "start_time": {"$lt": end_time},
        "end_time": {"$gt": start_time},
    }

    if doctor_id is not None:
        query["doctor_id"] = doctor_id

    if exclude_appointment_id is not None:
        if not ObjectId.is_valid(exclude_appointment_id):
            raise ValueError("Invalid appointment ID")

        query["_id"] = {"$ne": ObjectId(exclude_appointment_id)}

    collection = get_appointments_collection()
    existing_appointment = await collection.find_one(query)

    return existing_appointment is None


async def create_appointment(appointment_data: dict) -> dict:
    """Validate and save a new appointment."""

    appointment = AppointmentCreate.model_validate(appointment_data)

    available = await check_availability(
        start_time=appointment.start_time,
        end_time=appointment.end_time,
        doctor_id=appointment.doctor_id,
    )

    if not available:
        return {
            "success": False,
            "message": "This appointment slot is already booked.",
        }

    collection = get_appointments_collection()

    document = appointment.model_dump()
    document["start_time"] = appointment.start_time.astimezone(timezone.utc)
    document["end_time"] = appointment.end_time.astimezone(timezone.utc)
    document["status"] = "confirmed"
    document["created_at"] = datetime.now(timezone.utc)

    result = await collection.insert_one(document)

    saved_document = await collection.find_one(
        {"_id": result.inserted_id}
    )

    if saved_document is None:
        return {
            "success": False,
            "message": "Appointment was saved but could not be retrieved.",
        }

    return {
        "success": True,
        "message": "Appointment created successfully.",
        "appointment": serialize_appointment(saved_document),
    }


async def get_appointment(appointment_id: str) -> dict | None:
    """Retrieve one appointment by its MongoDB ID."""

    if not ObjectId.is_valid(appointment_id):
        return None

    collection = get_appointments_collection()

    document = await collection.find_one(
        {"_id": ObjectId(appointment_id)}
    )

    if document is None:
        return None

    return serialize_appointment(document)


async def get_appointments_by_phone(phone: str) -> list[dict]:
    """Retrieve appointments associated with a phone number."""

    collection = get_appointments_collection()

    cursor = collection.find(
        {"patient_phone": phone}
    ).sort("start_time", 1)

    appointments = []
    async for document in cursor:
        appointments.append(serialize_appointment(document))

    return appointments


async def cancel_appointment(appointment_id: str) -> dict:
    """Cancel an appointment without deleting its history."""

    if not ObjectId.is_valid(appointment_id):
        return {
            "success": False,
            "message": "Invalid appointment ID.",
              }

    collection = get_appointments_collection()

    result = await collection.update_one(
        {
            "_id": ObjectId(appointment_id),
            "status": "confirmed",
        },
        {
            "$set": {
                "status": "cancelled",
                "cancelled_at": datetime.now(timezone.utc),
            }
        },
    )

    if result.modified_count == 0:
        return {
            "success": False,
            "message": (
                "Appointment not found or it is already cancelled."
            ),
        }

    return {
        "success": True,
        "message": "Appointment cancelled successfully.",
    }
