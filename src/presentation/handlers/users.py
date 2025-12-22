from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi_users.authentication import AuthenticationBackend
from fastapi_users.exceptions import UserNotExists
from fastapi_users.router import ErrorCode


from src.domain.value_objects.user_roles import UserRole
from src.infrastructure.user.jwt_strategies import fastapi_users, auth_backend
from src.infrastructure.user.user_manager import UserManager, get_user_manager
from src.presentation.dependencies import get_current_active_user, has_permissions
from src.presentation.schemas.users import UserRead, UserCreate, UserUpdate

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def custom_register(
    user_create: UserCreate,
    user_manager: UserManager = Depends(get_user_manager),
    user=Depends(get_current_active_user),
    permissions=Depends(has_permissions([UserRole.ADMIN]))
):
    try:
        existing_user = await user_manager.get_by_email(user_create.email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS,
        )
    except UserNotExists:
        created_user = await user_manager.create(user_create, safe=True)
        return created_user



auth_router.include_router(
    fastapi_users.get_auth_router(auth_backend)
)
# auth_router.include_router(
#     fastapi_users.get_register_router(UserRead, UserCreate),
# )
auth_router.include_router(
    fastapi_users.get_reset_password_router(),
)
auth_router.include_router(
    fastapi_users.get_verify_router(UserRead),
)
auth_router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
)
