from sqlalchemy import String, Enum, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db import Base
from src.auth.schemas import UserRole
from src.orders.models import Order


class User(Base):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(length=320), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(
        String(length=1024), nullable=False
    )
    role: Mapped[str] = mapped_column(
        Enum(UserRole), nullable=False, default=UserRole.SALESMAN
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # associated location of the user
    location_id: Mapped[int] = mapped_column(
        ForeignKey("locations.id"), nullable=True
    )
    location = relationship("Location", back_populates="users")

    
    # order processing 
    orders_as_manager: Mapped[list["Order"]] = relationship(
        "Order",
        back_populates="manager",
        foreign_keys="[Order.manager_id]",
    )
    orders_as_delivery_guy: Mapped[list["Order"]] = relationship(
        "Order",
        back_populates="delivery_guy",
        foreign_keys="[Order.delivery_guy_id]",
    )



