from sqlalchemy import Integer, String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.db.models.base import Base
from src.domain.value_objects.location_type import LocationType

class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(length=256), nullable=False, unique=True)
    address: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    location_type: Mapped[str] = mapped_column(Enum(LocationType), nullable=False, default=LocationType.TRADING_POINT)

    # Relationships
    users = relationship("User", back_populates="location")
    products = relationship("LocationProduct", back_populates="location")

    # Orders where this location is source or destination
    orders_from = relationship(
        "Order",
        back_populates="location_from",
        foreign_keys="[Order.location_from_id]"
    )
    orders_to = relationship(
        "Order",
        back_populates="location_to",
        foreign_keys="[Order.location_to_id]"
    )
