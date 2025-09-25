from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db import Base
from src.auth.schemas import UserRole
from src.orders.models import Order


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    role: Mapped[str] = mapped_column(
        Enum(UserRole), nullable=False, default=UserRole.SALESMAN
    )


    orders_as_manager: Mapped[list[Order]] = relationship(
        "Order",
        back_populates="manager", 
        foreign_keys="[Order.manager_id]"
    )

    orders_as_delivery_guy: Mapped[list[Order]] = relationship(
        "Order",
        back_populates="delivery_guy",
        foreign_keys="[Order.delivery_guy_id]"
    )

