from pydantic import BaseModel, ConfigDict

class ProductRead(BaseModel):
    id: int
    name: str
    description: str
    threshold: int = 0

    model_config = ConfigDict(from_attributes=True)

class BaseProductUpdate(BaseModel):
    pass

class ProductUpdate(BaseProductUpdate):
    name: str
    description: str
    threshold: int

class ProductPartUpdate(BaseProductUpdate):
    name: str | None = None
    description: str | None = None
    threshold: int | None = None
