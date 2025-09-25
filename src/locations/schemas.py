import enum

from pydantic import BaseModel


class LocationType(enum.Enum):
    WAREHOUSE = "warehouse"
    TRADING_POINT = "trading_point"

class LocationRead(BaseModel):
    id: int
    name: str 
    address: str 
    location_type: LocationType = LocationType.WAREHOUSE
