from fastapi_users import schemas
from pydantic import EmailStr

from src.domain.value_objects.user_roles import UserRole

class UserRead(schemas.BaseUser[int]):
    id: int
    email: EmailStr
    is_active: bool = True
    is_verified: bool = False
    role: UserRole

class UserCreate(schemas.BaseUserCreate):
    email: EmailStr  # email validation
    role: UserRole

class UserUpdate(schemas.BaseUserUpdate):
    role: UserRole
    location_id: int
