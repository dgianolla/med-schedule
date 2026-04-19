from sqlalchemy import Boolean, Column, String, Text

from app.models.base import Base


class Convenio(Base):
    __tablename__ = "convenios"

    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=True)
    active = Column(Boolean, default=True)
    contact = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)
