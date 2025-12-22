from typing import Optional
from sqlalchemy import String, ForeignKey, Enum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from src.infrastructure.db.models.base import Base
from src.domain.value_objects.status import Status


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    manager_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    delivery_guy_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    location_from_id: Mapped[Optional[int]] = mapped_column(ForeignKey("locations.id"), nullable=True)
    location_to_id: Mapped[Optional[int]] = mapped_column(ForeignKey("locations.id"), nullable=True)
    status: Mapped[Status] = mapped_column(Enum(Status), default=Status.PENDING, nullable=False)

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
    products: Mapped[list["OrderProduct"]] = relationship("OrderProduct", back_populates="order", lazy="selectin")


class OrderProduct(Base):
    __tablename__ = "order_products"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)

    order: Mapped["Order"] = relationship("Order", back_populates="products")
    product: Mapped["Product"] = relationship("Product", lazy="joined") 
