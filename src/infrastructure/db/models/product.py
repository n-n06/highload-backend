from sqlalchemy import Column, Integer, String, CheckConstraint
from src.tmp.db import Base

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
