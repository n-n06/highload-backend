from typing import Any
import logging
from fastapi import Request
from fastapi_users import BaseUserManager, IntegerIDMixin
from fastapi_users.exceptions import InvalidPasswordException

from src.infrastructure.db import User

logger = logging.getLogger(__name__)


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):

    def __init__(self, user_db, reset_password_token_secret: str, verification_token_secret: str):
        super().__init__(user_db)
        self.reset_password_token_secret = reset_password_token_secret
        self.verification_token_secret = verification_token_secret

    async def create_superuser(
            self,
            user_create_dict: dict,
            safe: bool = False
    ) -> User:

        user_create_dict["is_superuser"] = True
        user_create_dict["role"] = "admin"
        user = await self.create(User(**user_create_dict), safe)
        return user


    async def on_after_register(
            self, user: User, request: Request | None = None
    ) -> None:
        logger.info(f"User {user.email} registered")

    async def on_after_verify(
            self, user: User, request: Request | None = None
    ) -> None:
        logger.info(f"User {user.email} verified")

    async def on_after_forgot_password(
            self, user: User, token: str, request: Request | None = None
    ) -> None:
        logger.info(f"Password reset requested for {user.email}")

    async def on_after_reset_password(
            self, user: User, request: Request | None = None
    ) -> None:
        logger.info(f"Password reset for {user.email}")