from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Enum, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.db.models.base import Base
from src.domain.value_objects.user_roles import UserRole

if TYPE_CHECKING:
    from src.infrastructure.db.models.order import Order
    from src.infrastructure.db.models.location import Location


class User(Base):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(length=320), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(
        String(length=1024), nullable=False
    )
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), nullable=False, default=UserRole.SALESMAN
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    location_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("locations.id"), nullable=True
    )

    orders_as_manager: Mapped[list["Order"]] = relationship(
        "Order",
        back_populates="manager",
        foreign_keys="[Order.manager_id]"
    )

    orders_as_delivery_guy: Mapped[list["Order"]] = relationship(
        "Order",
        back_populates="delivery_guy",
        foreign_keys="[Order.delivery_guy_id]"
    )

    location: Mapped[Optional["Location"]] = relationship(
        "Location",
        back_populates="users",
        foreign_keys=[location_id]
    )

