from datetime import time
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SchedulingSettingsResponse(BaseModel):
    id: UUID
    weekday_opening: time
    weekday_closing: time
    saturday_opening: time
    saturday_closing: time
    sunday_closed: bool
    holidays_closed: bool
    buffer_minutes: int
    max_advance_days: int
    created_at: Optional[time] = None
    updated_at: Optional[time] = None

    model_config = {"from_attributes": True}


class SchedulingSettingsUpdate(BaseModel):
    weekday_opening: Optional[time] = None
    weekday_closing: Optional[time] = None
    saturday_opening: Optional[time] = None
    saturday_closing: Optional[time] = None
    sunday_closed: Optional[bool] = None
    holidays_closed: Optional[bool] = None
    buffer_minutes: Optional[int] = None
    max_advance_days: Optional[int] = None


class DailyReportResponse(BaseModel):
    date: str
    total: int
    by_status: dict[str, int]
    by_professional: dict[str, int]
    by_type: dict[str, int]


class WeeklyReportResponse(BaseModel):
    week_start: str
    week_end: str
    total: int
    by_status: dict[str, int]
    by_professional: dict[str, int]
    by_type: dict[str, int]
    daily_breakdown: dict[str, int]
