from dataclasses import dataclass

from src.domain.value_objects import LocationType


@dataclass
class Location:
    name: str
    address: str
    location_type: LocationType
    id: int | None = None
