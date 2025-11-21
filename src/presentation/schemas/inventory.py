from pydantic import BaseModel, ConfigDict

from .products import ProductRead


class LocationProductRead(BaseModel):
    product: ProductRead
    stock: int

    model_config = ConfigDict(from_attributes=True)


class LocationProductDetail(LocationProductRead):
    product_id: int
    location_id: int


class LocationProductCreate(BaseModel):
    product_id: int
    quantity: int
    threshold: int | None = None


class LocationProductUpdate(BaseModel):
    quantity: int | None = None
    threshold: int | None = None


class StockAdjustment(BaseModel):
    delta: int


class TransferItem(BaseModel):
    product_id: int
    quantity: int


class TransferRequest(BaseModel):
    to_location_id: int
    items: list[TransferItem]
