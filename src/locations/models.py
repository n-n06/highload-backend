from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.db import Base
from src.locations.schemas import LocationType

class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(
        String(length=256), nullable=False, unique=True
    )
    address: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    location_type: Mapped[str] = mapped_column(
        Enum(LocationType), nullable=False, default=LocationType.TRADING_POINT
    )

    # users at this location
    users = relationship("User", back_populates="location")
    # available products
    products = relationship("LocationProduct", back_populates="location")

    # order souce and target
    orders_from = relationship(
        "Order", back_populates="location_from", 
        foreign_keys="[Order.location_from_id]"
    )
    orders_to = relationship(
        "Order", back_populates="location_to", 
        foreign_keys="[Order.location_to_id]"
    )