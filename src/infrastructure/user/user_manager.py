from fastapi import Request, Depends
from fastapi_users import BaseUserManager, IntegerIDMixin
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.exceptions import InvalidPasswordException

from src.bootstrap.config import settings
from src.infrastructure.db.models.user import User
from src.infrastructure.user.user_db import get_user_db
from src.presentation.schemas.users import UserCreate


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):

    def __init__(self, user_db):
        super().__init__(user_db)
        self.reset_password_token_secret = settings.SECRET
        self.verification_token_secret = settings.SECRET


    async def create_superuser(
            self,
            user_create_dict: dict,
            safe: bool = False
    ) -> User:

        user_create_dict["is_superuser"] = True
        user_create_dict["role"] = "admin"
        user = await self.create(User(**user_create_dict), safe)
        return user


    async def validate_password(
            self, 
            password: str, 
            user: UserCreate | User
    ) -> None:
        if len(password) < 8:
            raise InvalidPasswordException(
                reason="Password should be at least 8 characters long!"
            )
        if user.email.lower() in password.lower():
            raise InvalidPasswordException(
                reason="Password should not contain the email"
            )
        if any((
            password.isalpha(),
            password.islower(),
            password.isupper(),
            password.isnumeric(),
            password.isspace(),
        )):
            raise InvalidPasswordException(
                reason="Password should contain a mix of uppercase " + 
                " and lowercase letters, numbers and symbols"
            )


    async def on_after_register(
            self, user: User, request: Request | None = None
    ) -> None:
        print(f"User {user.email} registered")

    async def on_after_verify(
            self, user: User, request: Request | None = None
    ) -> None:
        print(f"User {user.email} verified")

    async def on_after_forgot_password(
            self, user: User, token: str, request: Request | None = None
    ) -> None:
        print(f"Password reset requested for {user.email}")

    async def on_after_reset_password(
            self, user: User, request: Request | None = None
    ) -> None:
        print(f"Password reset for {user.email}")


# get user manager
async def get_user_manager(
        user_db: SQLAlchemyUserDatabase = Depends(get_user_db)
):
    yield UserManager(user_db)
