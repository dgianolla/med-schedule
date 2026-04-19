from abc import ABC, abstractmethod
from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class TimeSlot(BaseModel):
    time: str
    available: bool


class AppointmentRecord(BaseModel):
    id: str
    patient_name: str
    patient_phone: str
    professional_id: str
    scheduled_at: str
    ends_at: str
    status: str
    specialty: str
    external_id: Optional[str] = None


class CreateAppointmentRequest(BaseModel):
    patient_name: str
    patient_phone: str
    patient_email: Optional[str] = None
    specialty: str
    professional_id: Optional[str] = None
    date: str
    time: str
    convenio_id: Optional[str] = None
    convenio_name: Optional[str] = None
    source: str = "lia"
    notes: Optional[str] = None
    patient_notes: Optional[str] = None


class Appointment(BaseModel):
    id: str
    patient_name: str
    patient_phone: str
    patient_email: Optional[str] = None
    professional_id: Optional[str] = None
    professional_name: Optional[str] = None
    specialty: str
    scheduled_at: str
    ends_at: str
    duration_minutes: int
    status: str
    source: str
    convenio_id: Optional[str] = None
    convenio_name: Optional[str] = None
    notes: Optional[str] = None
    patient_notes: Optional[str] = None
    external_id: Optional[str] = None
    cancelled_at: Optional[str] = None
    cancellation_reason: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class AppointmentProvider(ABC):
    """Abstract base for all scheduling providers."""

    @abstractmethod
    async def get_available_dates(
        self, professional_id: str, month: int, year: int
    ) -> list[date]: ...

    @abstractmethod
    async def get_available_times(
        self, professional_id: str, date: date
    ) -> list[TimeSlot]: ...

    @abstractmethod
    async def get_agenda(
        self, professional_id: str | None, date_from: date, date_to: date
    ) -> list[AppointmentRecord]: ...

    @abstractmethod
    async def create_appointment(
        self, payload: CreateAppointmentRequest
    ) -> Appointment: ...

    @abstractmethod
    async def cancel_appointment(
        self, appointment_id: str, reason: str | None = None
    ) -> Appointment: ...
