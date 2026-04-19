from sqlalchemy import Boolean, Column, String

from app.models.base import Base


class ProviderRoute(Base):
    __tablename__ = "provider_routes"

    specialty_slug = Column(String(100), unique=True, nullable=False)
    provider = Column(String(50), nullable=False)
    active = Column(Boolean, default=True)
