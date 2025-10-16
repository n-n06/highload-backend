from fastapi import APIRouter, Depends
from dishka.integrations.fastapi import FromDishka
from fastapi_users import FastAPIUsers

from src.infrastructure.db.models import User as UserModel
from src.presentation.schemas.users import UserReadSchema, UserCreateSchema, UserUpdateSchema
from fastapi_users.authentication import AuthenticationBackend


auth_router = APIRouter(prefix="/auth", tags=["Auth"])


auth_router.include_router(
    fastapi_users.get_auth_router(AuthenticationBackend)
)
auth_router.include_router(
    fastapi_users.get_register_router(UserReadSchema, UserCreateSchema),
)
auth_router.include_router(
    fastapi_users.get_reset_password_router(),
)
auth_router.include_router(
    fastapi_users.get_verify_router(UserRead),
)
auth_router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
)


