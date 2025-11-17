from dataclasses import dataclass


@dataclass
class LocationProduct:
    id: int
    location_id: int
    product_id: int
    stock: int
