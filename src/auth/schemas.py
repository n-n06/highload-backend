from fastapi_users import schemas
from pydantic import EmailStr

import enum
from typing import Optional

class UserRole(enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    SALESMAN = "salesman"
    DELIVERY = "delivery"

class UserRead(schemas.BaseUser[int]):
    role: UserRole

class UserCreate(schemas.BaseUserCreate):
    email: EmailStr  # email validation
    password: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False
    role: UserRole

class UserUpdate(schemas.BaseUserUpdate):
    role: UserRole
