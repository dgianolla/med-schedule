from sqlalchemy import Boolean, Column, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.models.base import Base


class Professional(Base):
    __tablename__ = "professionals"
    __table_args__ = (UniqueConstraint("name", "specialty", name="uq_professional_name_specialty"),)

    name = Column(String(200), nullable=False)
    specialty = Column(String(100), nullable=False)
    specialty_slug = Column(String(100), nullable=False)
    external_id = Column(String(100), nullable=True)
    provider = Column(String(50), nullable=False, default="local")
    active = Column(Boolean, default=True)
