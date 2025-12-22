from pydantic import BaseModel

class ProductCreate(BaseModel):
    name: str
    description: str

class ProductRead(BaseModel):
    id: int
    name: str
    description: str
    # stock: int = 0
    # threshold: int = 0

class BaseProductUpdate(BaseModel):
    pass

class ProductUpdate(BaseProductUpdate):
    name: str
    description: str

class ProductPartUpdate(BaseProductUpdate):
    name: str | None = None
    description: str | None = None
