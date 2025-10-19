from typing import Any
from fastapi import Request
from fastapi_users import BaseUserManager, IntegerIDMixin
from fastapi_users.exceptions import InvalidPasswordException


from ..persistence.models import UserModel
from ..schemas import UserCreateSchema


class UserManager(IntegerIDMixin, BaseUserManager[UserModel, int]):
    """
    fastapi-users UserManager
    Адаптер между fastapi-users и нашей domain логикой
    """

    def __init__(self, user_db, reset_password_token_secret: str, verification_token_secret: str):
        super().__init__(user_db)
        self.reset_password_token_secret = reset_password_token_secret
        self.verification_token_secret = verification_token_secret

    async def create_superuser(
            self,
            user_create_dict: dict,
            safe: bool = False
    ) -> UserModel:

        user_create_dict["is_superuser"] = True
        user_create_dict["role"] = "admin"
        user = await self.create(user_create_dict, safe)
        return user


    async def on_after_register(
            self, user: UserModel, request: Request | None = None
    ) -> None:
        print(f"User {user.email} registered")

    async def on_after_verify(
            self, user: UserModel, request: Request | None = None
    ) -> None:
        print(f"User {user.email} verified")

    async def on_after_forgot_password(
            self, user: UserModel, token: str, request: Request | None = None
    ) -> None:
        print(f"Password reset requested for {user.email}")

    async def on_after_reset_password(
            self, user: UserModel, request: Request | None = None
    ) -> None:
        print(f"Password reset for {user.email}")