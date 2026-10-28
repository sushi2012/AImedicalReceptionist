
# app/models/appointment.py

from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class AppointmentCreate(BaseModel):
    """Data required to create a dental appointment."""

    model_config = ConfigDict(str_strip_whitespace=True)

    patient_name: str = Field(min_length=2, max_length=100)
    patient_phone: str = Field(min_length=7, max_length=20)
    service: str = Field(min_length=2, max_length=100)

    start_time: datetime
    end_time: datetime

    doctor_id: str | None = None
    reason: str | None = Field(default=None, max_length=500)

    @field_validator("start_time", "end_time")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Appointment times must include a timezone")
        return value.astimezone(timezone.utc)

    @model_validator(mode="after")
    def validate_appointment_time(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self


class AppointmentResponse(BaseModel):
    """Public representation of an appointment."""

    id: str
    patient_name: str
    patient_phone: str
    service: str
    start_time: datetime
    end_time: datetime
    doctor_id: str | None = None
    reason: str | None = None
    status: str
    created_at: datetime
