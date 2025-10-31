from pydantic import BaseModel
from src.domain.value_objects.location_type import LocationType


class LocationCreate(BaseModel):
    name: str
    address: str
    location_type: LocationType = LocationType.WAREHOUSE

class LocationRead(BaseModel):
    id: int
    name: str
    address: str
    location_type: LocationType = LocationType.WAREHOUSE
    users: list[UserRead]

class BaseLocationUpdate(BaseModel):
    pass

class LocationUpdate(BaseLocationUpdate):
    name: str
    address: str

class LocationPartUpdate(BaseLocationUpdate):
    name: str | None = None
    address: str | None = None
