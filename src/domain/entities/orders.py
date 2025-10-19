from dataclasses import dataclass, field

from src.domain.value_objects import Status


@dataclass
class Order:
    id: int
    manager_id: int
    delivery_guy_id: int
    status: Status