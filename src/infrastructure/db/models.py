from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Enum, CheckConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from src.infrastructure.db.base import Base
from src.domain.value_objects import UserRole, LocationType


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    delivery_guy_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    location_id = Column(Integer, ForeignKey("locations.id"))
    status = Column(String, default="pending")

    manager = relationship(
        "User",
        back_populates="orders_as_manager",
        foreign_keys=[manager_id],
    )
    delivery_guy = relationship(
        "User",
        back_populates="orders_as_delivery_guy",
        foreign_keys=[delivery_guy_id],
    )
    location = relationship("Location")


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


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    address = Column(String, nullable=False)
    location_type = Column(Enum(LocationType), nullable=False, default=LocationType.TRADING_POINT)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    stock = Column(Integer, default=0)
    threshold = Column(Integer, default=0)  # managers can define the limit for the product

    __table_args__ = (
        CheckConstraint("stock >= 0", name="check_stock_ge_0"),
        CheckConstraint("threshold >= 0", name="check_threshold_ge_0")
    )