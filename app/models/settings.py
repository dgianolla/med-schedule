from datetime import time

from sqlalchemy import Boolean, Column, Integer, Time

from app.models.base import Base


class SchedulingSettings(Base):
    __tablename__ = "scheduling_settings"

    weekday_opening = Column(Time, default=time(8, 0))
    weekday_closing = Column(Time, default=time(17, 0))
    saturday_opening = Column(Time, default=time(8, 0))
    saturday_closing = Column(Time, default=time(12, 0))
    sunday_closed = Column(Boolean, default=True)
    holidays_closed = Column(Boolean, default=True)
    buffer_minutes = Column(Integer, default=0)
    max_advance_days = Column(Integer, default=60)
