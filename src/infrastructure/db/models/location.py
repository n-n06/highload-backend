from sqlalchemy import String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.db.models.base import Base
from src.domain.value_objects.location_type import LocationType

class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(length=256), nullable=False, unique=True)
    address: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    location_type: Mapped[LocationType] = mapped_column(Enum(LocationType), nullable=False, default=LocationType.TRADING_POINT)

    users: Mapped[list["User"]] = relationship("User", back_populates="location")
    products: Mapped[list["LocationProduct"]] = relationship("LocationProduct", back_populates="location")

    orders_from: Mapped[list["Order"]] = relationship(
        "Order",
        back_populates="location_from",
        foreign_keys="[Order.location_from_id]"
    )
    orders_to: Mapped[list["Order"]] = relationship(
        "Order",
        back_populates="location_to",
        foreign_keys="[Order.location_to_id]"
    )
