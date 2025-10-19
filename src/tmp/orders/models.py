from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.tmp.db import Base

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