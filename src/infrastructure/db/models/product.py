from typing import Optional
from sqlalchemy import String, CheckConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from src.infrastructure.db.models.base import Base

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    # stock: Mapped[int] = mapped_column(default=0)
    # threshold: Mapped[int] = mapped_column(default=0)

    locations: Mapped[list["LocationProduct"]] = relationship("LocationProduct", back_populates="product")

    # __table_args__ = (
    #     CheckConstraint("stock >= 0", name="check_stock_ge_0"),
    #     CheckConstraint("threshold >= 0", name="check_threshold_ge_0")
    # )
