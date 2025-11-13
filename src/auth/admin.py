from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import async_session_maker
from src.config import settings
from src.auth.manager import get_user_manager  
from src.auth.schemas import UserCreate, UserRole

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_session_maker() as session:
        user_manager_dep = get_user_manager(session)
        user_manager = await anext(user_manager_dep)  

        existing_admin = await user_manager.get_by_email("admin@example.com")
        if not existing_admin:
            user_create = UserCreate(
                email=settings.ADMIN_EMAIL,
                password=settings.ADMIN_PASS,
                role=UserRole.ADMIN,
                is_verified=True,
            )
            await user_manager.create(user_create, safe=False)

    yield