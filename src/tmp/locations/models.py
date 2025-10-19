from sqlalchemy import Column, Integer, String, Enum

from src import Base
from src import LocationType

class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    address = Column(String, nullable=False)
    location_type = Column(Enum(LocationType), nullable=False, default=LocationType.TRADING_POINT)