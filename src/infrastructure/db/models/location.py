from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import Mapped, relationship

from src import Base
from src import LocationType
from src.tmp.auth.models import User

class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    address = Column(String, nullable=False)
    location_type = Column(Enum(LocationType), nullable=False, default=LocationType.TRADING_POINT)
    users : Mapped[list[User]] = relationship("users", back_populates="locations")
