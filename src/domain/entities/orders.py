from dataclasses import dataclass, field
from typing import Optional

from src.domain.value_objects import Status


@dataclass
class Order:
    id: int
    manager_id: int
    location_from_id: int
    location_to_id: int
    status: Status
    delivery_guy_id: Optional[int] = None
    products: list["OrderProduct"] = field(default_factory=list)


@dataclass
class OrderProduct:
    id: int
    order_id: int
    product_id: int
    quantity: int