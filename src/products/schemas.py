from pydantic import BaseModel

class ProductRead(BaseModel):
    id: int
    name: str
    description: str
    stock: int = 0
    threshold: int = 0

class ProductUpdate(BaseModel):
    name: str
    description: str
    stock: int
    threshold: int