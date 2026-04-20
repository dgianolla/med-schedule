from datetime import datetime, date
from typing import Optional
from uuid import UUID

from uuid import UUID

from pydantic import BaseModel, Field, field_validator, field_serializer


class CreateAppointmentRequest(BaseModel):
    patient_name: str = Field(..., min_length=1, max_length=200)
    patient_phone: str = Field(..., min_length=8, max_length=20)
    patient_email: Optional[str] = None
    patient_id: Optional[UUID] = None
    specialty: str = Field(..., min_length=1, max_length=100)
    professional_id: Optional[UUID] = None
    appointment_type_id: Optional[UUID] = None
    date: date
    time: str  # HH:MM format
    duration_minutes: Optional[int] = Field(None, gt=0)
    convenio_id: Optional[UUID] = None
    convenio_name: Optional[str] = None
    source: str = Field(default="admin", max_length=30)
    notes: Optional[str] = None
    patient_notes: Optional[str] = None
    medical_notes: Optional[str] = None

    @field_validator("time")
    @classmethod
    def validate_time_format(cls, v: str) -> str:
        parts = v.split(":")
        if len(parts) != 2:
            raise ValueError("Time must be in HH:MM format")
        hour, minute = int(parts[0]), int(parts[1])
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError("Invalid time values")
        return v


class AppointmentResponse(BaseModel):
    id: UUID
    patient_name: str
    patient_phone: str
    patient_email: Optional[str] = None
    patient_id: Optional[UUID] = None
    professional_id: Optional[UUID] = None
    professional_name: Optional[str] = None
    specialty: str
    scheduled_at: datetime
    ends_at: datetime
    duration_minutes: int
    status: str
    source: str
    convenio_id: Optional[UUID] = None
    convenio_name: Optional[str] = None
    notes: Optional[str] = None
    patient_notes: Optional[str] = None
    external_id: Optional[str] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    medical_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AppointmentUpdateRequest(BaseModel):
    patient_name: Optional[str] = None
    patient_phone: Optional[str] = None
    patient_email: Optional[str] = None
    patient_id: Optional[UUID] = None
    professional_id: Optional[UUID] = None
    professional_name: Optional[str] = None
    specialty: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    status: Optional[str] = None
    convenio_id: Optional[UUID] = None
    convenio_name: Optional[str] = None
    notes: Optional[str] = None
    patient_notes: Optional[str] = None
    medical_notes: Optional[str] = None


class CancelAppointmentRequest(BaseModel):
    reason: Optional[str] = Field(None, max_length=500)


class AppointmentListResponse(BaseModel):
    id: UUID
    patient_name: str
    patient_phone: str
    specialty: str
    professional_name: Optional[str] = None
    scheduled_at: datetime
    status: str
    source: str

    @field_serializer("patient_name")
    def mask_name(self, name: str, _info):
        parts = name.strip().split()
        if len(parts) > 1:
            return f"{parts[0]} {''.join([p[0] + '.' for p in parts[1:]])}"
        return name

    @field_serializer("patient_phone")
    def mask_phone(self, phone: str, _info):
        clean = "".join(filter(str.isdigit, phone))
        if len(clean) >= 10:
            return f"({clean[:2]}) 9****-**{clean[-2:]}"
        return "***"

    model_config = {"from_attributes": True}
