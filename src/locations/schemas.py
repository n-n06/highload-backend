import enum

from pydantic import BaseModel


class LocationType(enum.Enum):
    WAREHOUSE = "warehouse"
    TRADING_POINT = "trading_point"

class LocationCreate(BaseModel):
    name: str 
    address: str 
    location_type: LocationType = LocationType.WAREHOUSE

class LocationRead(BaseModel):
    id: int
    name: str 
    address: str 
    location_type: LocationType = LocationType.WAREHOUSE

class BaseLocationUpdate(BaseModel):
    pass

class LocationUpdate(BaseLocationUpdate):
    name: str
    address: str

class LocationPartUpdate(BaseLocationUpdate):
    name: str | None = None
    address: str | None = None
