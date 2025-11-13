from sqlalchemy import Column, Integer, String, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db import Base

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(
        String(length=1024), unique=True, nullable=False
    )
    description: Mapped[str] = mapped_column(
        String, nullable=True
    )

    threshold = Column(Integer, default=0)
    __table_args__ = (
        CheckConstraint("threshold >= 0", name="check_threshold_ge_0"),
    )

    # stock level control
    locations = relationship("LocationProduct", back_populates="product")