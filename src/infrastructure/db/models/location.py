from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import Mapped, relationship

from src.domain.value_objects import LocationType
from src.infrastructure.db.base import Base

class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    address = Column(String, nullable=False)
    location_type = Column(Enum(LocationType), nullable=False, default=LocationType.TRADING_POINT)
