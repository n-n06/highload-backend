from fastapi_users import schemas
from pydantic import EmailStr

from src.domain.value_objects.user_roles import UserRole
from src.application.schemas.locations import LocationRead

class UserRead(schemas.BaseUser[int]):
    id: int
    email: EmailStr
    is_active: bool = True
    is_verified: bool = False
    role: UserRole
    location: LocationRead | None

class UserCreate(schemas.BaseUserCreate):
    email: EmailStr  # email validation
    password: str
    is_active: bool | None = True
    is_verified: bool | None = False
    role: UserRole

class UserUpdate(schemas.BaseUserUpdate):
    role: UserRole
    location_id: int
