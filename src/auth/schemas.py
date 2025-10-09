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
    id: int
    email: EmailStr
    is_active: bool = True
    is_verified: bool = False
    role: UserRole

class UserCreate(schemas.BaseUserCreate):
    email: EmailStr  # email validation
    password: str
    is_active: bool | None = True
    is_verified: bool | None = False
    role: UserRole

class UserUpdate(schemas.BaseUserUpdate):
    role: UserRole
