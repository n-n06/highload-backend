from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from src.infrastructure.db.models.base import Base


class LocationProduct(Base):
    __tablename__ = "location_products"

    id: Mapped[int] = mapped_column(primary_key=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    stock: Mapped[int] = mapped_column(default=0, nullable=False)

    location: Mapped["Location"] = relationship("Location", back_populates="products")
    product: Mapped["Product"] = relationship("Product", back_populates="locations")
