from pydantic import BaseModel
from typing import Optional
from src.locations.models import LocationType


class OrderRead(BaseModel):
    id: int
    manager_id: int
    delivery_guy_id: Optional[int]
    location_id: int
    status: str

    class Config:
        orm_mode = True  


class OrderCreate(BaseModel):
    delivery_guy_id: Optional[int]
    location_id: int
    status: Optional[str] = "pending" 


class OrderUpdate(BaseModel):
    delivery_guy_id: Optional[int]
    status: Optional[str]