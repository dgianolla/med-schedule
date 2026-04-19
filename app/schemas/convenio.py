from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ConvenioCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    code: Optional[str] = Field(None, max_length=50)
    active: bool = True
    contact: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None


class ConvenioUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    code: Optional[str] = Field(None, max_length=50)
    active: Optional[bool] = None
    contact: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None


class ConvenioResponse(BaseModel):
    id: UUID
    name: str
    code: Optional[str] = None
    active: bool
    contact: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
