from fastapi.routing import APIRouter

from src.presentation.schemas.users import (
    UserCreate, UserRead, UserUpdate
)
from src.infrastructure.user.jwt_strategies import (
    fastapi_users, auth_backend
)

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


auth_router.include_router(
    fastapi_users.get_auth_router(auth_backend)
)
auth_router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
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

