from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    per_page: int
    pages: int


class ErrorResponse(BaseModel):
    error: dict[str, str | dict]


class TimeSlot(BaseModel):
    time: str
    available: bool


class HealthCheck(BaseModel):
    status: str
    version: str = "1.0.0"
