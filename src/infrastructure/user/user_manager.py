from typing import Any
import logging
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.exceptions import InvalidPasswordException

from src.infrastructure.db import User
from src.infrastructure.db.dependencies import get_user_db
from src.bootstrap.config import settings

logger = logging.getLogger(__name__)



class UserManager(IntegerIDMixin, BaseUserManager[User, int]):

    def __init__(
        self, 
        user_db, 
        reset_password_token_secret: str = settings.SECRET_KEY, 
        verification_token_secret: str = settings.SECRET_KEY
    ):
        super().__init__(user_db)
        self.reset_password_token_secret = reset_password_token_secret
        self.verification_token_secret = verification_token_secret

    async def create_superuser(
            self,
            user_create_dict: dict,
            safe: bool = False
    ) -> User:

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


async def get_user_manager(
        user_db: SQLAlchemyUserDatabase = Depends(get_user_db)
):
    yield UserManager(user_db)
