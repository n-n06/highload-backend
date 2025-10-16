from pydantic import BaseModel
from typing import Optional


class OrderRead(BaseModel):
    id: int
    manager_id: int
    delivery_guy_id: Optional[int]
    location_id: int
    status: str

    class Config:
        orm_mode = True  


class OrderCreate(BaseModel):
    delivery_guy_id: int | None = None
    location_id: int
    status: str | None = "pending" 

class BaseOrderUpdate(BaseModel):
    pass

class OrderUpdate(BaseOrderUpdate):
    delivery_guy_id: int     
    status: str

class OrderPartUpdate(BaseOrderUpdate):
    delivery_guy_id: int | None = None
    status: str | None = None
