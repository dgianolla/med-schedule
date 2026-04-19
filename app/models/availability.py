from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class AvailabilityBlock(Base):
    __tablename__ = "availability_blocks"

    professional_id = Column(
        PG_UUID(as_uuid=True), ForeignKey("professionals.id"), nullable=True
    )
    specialty = Column(String(100), nullable=True)
    start_at = Column(DateTime(timezone=True), nullable=False)
    end_at = Column(DateTime(timezone=True), nullable=False)
    reason = Column(String(200), nullable=True)
    recurring = Column(String(20), default="none")

    __table_args__ = (
        Index(
            "ix_availability_professional_start_end",
            "professional_id",
            "start_at",
            "end_at",
        ),
    )
