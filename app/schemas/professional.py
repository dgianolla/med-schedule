from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ProfessionalResponse(BaseModel):
    id: UUID
    name: str
    specialty: str
    specialty_slug: str
    external_id: Optional[str] = None
    provider: str
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProfessionalCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    specialty: str = Field(..., min_length=1, max_length=100)
    specialty_slug: str = Field(..., min_length=1, max_length=100)
    external_id: Optional[str] = Field(None, max_length=100)
    provider: str = Field(default="local", pattern="^(local|apphealth)$")
    active: bool = True


class ProfessionalUpdate(BaseModel):
    name: Optional[str] = None
    specialty: Optional[str] = None
    specialty_slug: Optional[str] = None
    external_id: Optional[str] = None
    provider: Optional[str] = None
    active: Optional[bool] = None


class AppointmentTypeResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    default_duration_minutes: int
    description: Optional[str] = None
    active: bool

    model_config = {"from_attributes": True}


class AppointmentTypeCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)
    default_duration_minutes: int = Field(default=30, gt=0)
    description: Optional[str] = None
    active: bool = True


class AppointmentTypeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    default_duration_minutes: Optional[int] = Field(None, gt=0)
    description: Optional[str] = None
    active: Optional[bool] = None
