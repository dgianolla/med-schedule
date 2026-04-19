from sqlalchemy import Boolean, Column, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.models.base import Base


class AppointmentType(Base):
    __tablename__ = "appointment_types"

    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    default_duration_minutes = Column(Integer, nullable=False, default=30)
    description = Column(Text, nullable=True)
    active = Column(Boolean, default=True)
