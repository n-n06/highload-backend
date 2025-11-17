from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from src.infrastructure.db.models.base import Base


class LocationProduct(Base):
    __tablename__ = "location_products"

    id = Column(Integer, primary_key=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    stock = Column(Integer, default=0, nullable=False)

    location = relationship("Location", back_populates="products")
    product = relationship("Product", back_populates="locations")
