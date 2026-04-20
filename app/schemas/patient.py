from datetime import date, datetime
from typing import Optional
from uuid import UUID

from uuid import UUID

from pydantic import BaseModel, Field, field_serializer


class PatientCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    phone: str = Field(..., min_length=8, max_length=20)
    email: Optional[str] = Field(None, max_length=200)
    document: Optional[str] = Field(None, max_length=30)
    birth_date: Optional[date] = None
    address: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None


class PatientUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    phone: Optional[str] = Field(None, min_length=8, max_length=20)
    email: Optional[str] = Field(None, max_length=200)
    document: Optional[str] = Field(None, max_length=30)
    birth_date: Optional[date] = None
    address: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None


class PatientResponse(BaseModel):
    id: UUID
    name: str
    phone: str
    email: Optional[str] = None
    document: Optional[str] = None
    birth_date: Optional[date] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PatientListResponse(BaseModel):
    id: UUID
    name: str
    phone: str

    @field_serializer("name")
    def mask_name(self, name: str, _info):
        parts = name.strip().split()
        if len(parts) > 1:
            return f"{parts[0]} {''.join([p[0] + '.' for p in parts[1:]])}"
        return name

    @field_serializer("phone")
    def mask_phone(self, phone: str, _info):
        clean = "".join(filter(str.isdigit, phone))
        if len(clean) >= 10:
            return f"({clean[:2]}) 9****-**{clean[-2:]}"
        return "***"

    model_config = {"from_attributes": True}
