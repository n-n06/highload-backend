from dataclasses import dataclass

from src.domain.value_objects import LocationType


@dataclass
class Location:
    # id: int
    name: str
    address: str
    location_type : LocationType
