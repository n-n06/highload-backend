from fastapi import APIRouter

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


