from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_users.exceptions import UserNotExists
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.db import get_user_db
from src.db import AsyncSessionLocal
from src.config import settings
from src.auth.manager import get_user_manager  
from src.auth.schemas import UserCreate, UserRole

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncSessionLocal() as session:
        user_db_gen = get_user_db(session)
        user_db = await anext(user_db_gen)

        user_manager_gen = get_user_manager(user_db)
        user_manager = await anext(user_manager_gen)

        try:
            admin = await user_manager.get_by_email(settings.ADMIN_EMAIL)

            updated = False

            if not admin.is_superuser:
                admin.is_superuser = True
                updated = True
            if admin.role != UserRole.ADMIN:
                admin.role = UserRole.ADMIN
                updated = True

            if updated:
                await session.commit()
        except:
            user_create = UserCreate(
                email=settings.ADMIN_EMAIL,
                password=settings.ADMIN_PASS,
                role=UserRole.ADMIN,
                is_verified=True,
                is_superuser=True,
            )
            await user_manager.create(user_create, safe=False)
            await session.commit()
        finally:
            await user_manager_gen.aclose()
            await user_db_gen.aclose()

    yield
