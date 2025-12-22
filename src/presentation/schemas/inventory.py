from pydantic import BaseModel, ConfigDict

from .products import ProductRead


class LocationProductRead(BaseModel):
    product: ProductRead
    stock: int

    model_config = ConfigDict(from_attributes=True)


class LocationProductDetail(LocationProductRead):
    product_id: int
    location_id: int

    model_config = ConfigDict(from_attributes=True)


class LocationProductCreate(BaseModel):
    product_id: int
    quantity: int
    threshold: int | None = None

    model_config = ConfigDict(from_attributes=True)


class LocationProductUpdate(BaseModel):
    quantity: int | None = None
    threshold: int | None = None

    model_config = ConfigDict(from_attributes=True)


class StockAdjustment(BaseModel):
    delta: int

    model_config = ConfigDict(from_attributes=True)


class TransferItem(BaseModel):
    product_id: int
    quantity: int

    model_config = ConfigDict(from_attributes=True)


class TransferRequest(BaseModel):
    to_location_id: int
    items: list[TransferItem]

    model_config = ConfigDict(from_attributes=True)
