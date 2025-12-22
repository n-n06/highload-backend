from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_users.exceptions import UserNotExists
from sqlalchemy.exc import IntegrityError

from src.infrastructure.db.dependencies import async_session_maker, engine, get_user_db
from src.infrastructure.user.user_manager import get_user_manager
from src.bootstrap.config import settings
from src.infrastructure.db.models.user import UserRole
from src.presentation.schemas.users import UserCreate


@asynccontextmanager
async def create_admin_user_lifespan(app: FastAPI):
    async with async_session_maker() as session:
        async for user_db in get_user_db(session):
            break

        async for user_manager in get_user_manager(user_db):
            break

        try:
            admin = await user_manager.get_by_email(settings.ADMIN_EMAIL)

            updated = False

            if admin.role != UserRole.ADMIN:
                admin.role = UserRole.ADMIN
                updated = True

            if updated:
                await session.commit()

        except UserNotExists:
            user_create = UserCreate(
                email=settings.ADMIN_EMAIL,
                password=settings.ADMIN_PASS,
                role=UserRole.ADMIN,
                is_verified=True,
            )
            await user_manager.create(user_create, safe=False)

        except IntegrityError:
            await session.rollback()

    yield

    await engine.dispose()
