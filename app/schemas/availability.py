from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AvailableDatesRequest(BaseModel):
    specialty: str = Field(..., min_length=1, max_length=100)
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2020, le=2030)


class AvailableTimesRequest(BaseModel):
    professional_id: UUID
    date: date


class AgendaRequest(BaseModel):
    professional_id: Optional[UUID] = None
    date_from: date
    date_to: date


class AvailabilityBlockCreate(BaseModel):
    professional_id: Optional[UUID] = None
    specialty: Optional[str] = Field(None, max_length=100)
    start_at: datetime
    end_at: datetime
    reason: Optional[str] = Field(None, max_length=200)
    recurring: str = Field(default="none", pattern="^(none|daily|weekly|monthly)$")


class AvailabilityBlockResponse(BaseModel):
    id: UUID
    professional_id: Optional[UUID] = None
    specialty: Optional[str] = None
    start_at: datetime
    end_at: datetime
    reason: Optional[str] = None
    recurring: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TimeSlotResponse(BaseModel):
    time: str
    available: bool


class AvailableDateResponse(BaseModel):
    date: str
    slots_available: int
