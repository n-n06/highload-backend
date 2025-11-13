from typing import Optional

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.db import Base

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    manager_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    delivery_guy_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    location_from_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("locations.id"), nullable=True
    )
    location_to_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("locations.id"), nullable=True
    )

    status: Mapped[str] = mapped_column(String, default="pending")


    # Relationships
    manager: Mapped["User"] = relationship(
        "User",
        back_populates="orders_as_manager",
        foreign_keys=[manager_id],
    )
    delivery_guy: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="orders_as_delivery_guy",
        foreign_keys=[delivery_guy_id],
    )

    location_from: Mapped[Optional["Location"]] = relationship(
        "Location",
        back_populates="orders_from",
        foreign_keys=[location_from_id],
    )
    location_to: Mapped[Optional["Location"]] = relationship(
        "Location",
        back_populates="orders_to",
        foreign_keys=[location_to_id],
    )