from fastapi_users import schemas
from pydantic import EmailStr
from src.domain.value_objects.user_roles import UserRole


class UserReadSchema(schemas.BaseUser[int]):
    id: int
    email: EmailStr
    is_active: bool = True
    is_verified: bool = False
    role: UserRole


class UserCreateSchema(schemas.BaseUserCreate):

    email: EmailStr
    password: str
    is_active: bool | None = True
    is_verified: bool | None = False
    role: UserRole = UserRole.SALESMAN


class UserUpdateSchema(schemas.BaseUserUpdate):

    role: UserRole | None = None