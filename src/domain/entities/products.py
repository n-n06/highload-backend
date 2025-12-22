from dataclasses import dataclass, field

@dataclass
class Product:
    id: int
    name: str
    description: str
    # stock: int
    # threshold: int
