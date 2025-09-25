from pydantic import BaseModel

class ProductRead(BaseModel):
    id: int
    name: str
    description: str
    stock: int = 0
    threshold: int = 0

class BaseProductUpdate(BaseModel):
    pass

class ProductUpdate(BaseProductUpdate):
    name: str
    description: str
    stock: int
    threshold: int

class ProductPartUpdate(BaseProductUpdate):
    name: str | None
    description: str | None
    stock: int | None
    threshold: int | None
