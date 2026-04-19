from sqlalchemy import Column, Date, String, Text

from app.models.base import Base


class Patient(Base):
    __tablename__ = "patients"

    name = Column(String(200), nullable=False)
    phone = Column(String(20), nullable=False, unique=True)
    email = Column(String(200), nullable=True)
    document = Column(String(30), nullable=True)
    birth_date = Column(Date, nullable=True)
    address = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
