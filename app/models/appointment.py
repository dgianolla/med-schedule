from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Index,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class Appointment(Base):
    __tablename__ = "appointments"

    patient_name = Column(String(200), nullable=False)
    patient_phone = Column(String(20), nullable=False)
    patient_email = Column(String(200), nullable=True)
    patient_id = Column(
        PG_UUID(as_uuid=True), ForeignKey("patients.id"), nullable=True
    )
    professional_id = Column(
        PG_UUID(as_uuid=True), ForeignKey("professionals.id"), nullable=True
    )
    professional_name = Column(String(200), nullable=True)
    appointment_type_id = Column(
        PG_UUID(as_uuid=True), ForeignKey("appointment_types.id"), nullable=True
    )
    specialty = Column(String(100), nullable=False)
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    ends_at = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    status = Column(String(30), nullable=False, default="scheduled")
    source = Column(String(30), nullable=False, default="lia")
    convenio_id = Column(PG_UUID(as_uuid=True), nullable=True)
    convenio_name = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    patient_notes = Column(Text, nullable=True)
    external_id = Column(String(200), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    cancellation_reason = Column(String(500), nullable=True)
    medical_notes = Column(Text, nullable=True)

    __table_args__ = (
        Index("ix_appointments_scheduled_at", "scheduled_at"),
        Index("ix_appointments_patient_phone", "patient_phone"),
        Index("ix_appointments_status_scheduled_at", "status", "scheduled_at"),
        Index("ix_appointments_professional_scheduled", "professional_id", "scheduled_at"),
        Index("ix_appointments_external_id", "external_id"),
    )
