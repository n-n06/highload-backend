import enum

from pydantic import BaseModel, ConfigDict

from src.products.schemas import ProductRead

"""
Basic CRUD schemas
"""
class LocationType(enum.Enum):
    WAREHOUSE = "warehouse"
    TRADING_POINT = "trading_point"

class LocationCreate(BaseModel):
    name: str 
    address: str 
    location_type: LocationType = LocationType.WAREHOUSE

class LocationProductRead(BaseModel):
    product: ProductRead
    stock: int

    model_config = ConfigDict(from_attributes=True)

class LocationRead(BaseModel):
    id: int
    name: str 
    address: str 
    location_type: LocationType
    products: list[LocationProductRead] = []

    model_config = ConfigDict(from_attributes=True)

class LocationReadShallow(BaseModel):
    id: int
    name: str 
    address: str 
    location_type: LocationType

    model_config = ConfigDict(from_attributes=True)

class BaseLocationUpdate(BaseModel):
    pass

class LocationUpdate(BaseLocationUpdate):
    name: str
    address: str

class LocationPartUpdate(BaseLocationUpdate):
    name: str | None = None
    address: str | None = None


"""
Location <==> Product Schemas
"""

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
