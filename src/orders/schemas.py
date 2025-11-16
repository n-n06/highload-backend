from pydantic import BaseModel, ConfigDict


from src.auth.schemas import UserRead
from src.locations.schemas import LocationReadShallow
from src.products.schemas import ProductRead



class OrderProductRead(BaseModel):
    product: ProductRead
    quantity: int

    model_config = ConfigDict(from_attributes=True)

class OrderProductCreate(BaseModel):
    product_id: int
    quantity: int

class OrderRead(BaseModel):
    id: int
    manager: UserRead
    delivery_guy: UserRead | None = None 
    location_from: LocationReadShallow
    location_to: LocationReadShallow
    status: str
    products: list[OrderProductRead]

    model_config = ConfigDict(from_attributes=True)

class OrderCreate(BaseModel):
    delivery_guy_id: int | None = None
    location_from_id: int
    location_to_id: int
    products: list[OrderProductCreate]
    status: str | None = "pending" 


class OrderUpdate(BaseModel):
    delivery_guy_id: int | None = None
    location_from_id: int | None = None
    location_to_id: int | None = None
    status: str | None = None
    comment: str | None = None
    products: list[OrderProductCreate] | None = None
