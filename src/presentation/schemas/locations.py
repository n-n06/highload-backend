from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict
from src.domain.value_objects.location_type import LocationType

if TYPE_CHECKING:
    from src.presentation.schemas.users import UserRead


class LocationCreate(BaseModel):
    name: str
    address: str
    location_type: LocationType = LocationType.WAREHOUSE

class LocationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    address: str
    location_type: LocationType = LocationType.WAREHOUSE
    users: list[Any] = []

class BaseLocationUpdate(BaseModel):
    pass

class LocationUpdate(BaseLocationUpdate):
    name: str
    address: str

class LocationPartUpdate(BaseLocationUpdate):
    name: str | None = None
    address: str | None = None
