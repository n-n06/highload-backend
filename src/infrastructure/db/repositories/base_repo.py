from src.infrastructure.db.models import Product, User, Order, Location

from typing import TypeVar, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.infrastructure.db.repositories.protocol import BaseRepositoryProtocol


T = TypeVar("T")


class BaseRepository(BaseRepositoryProtocol):
    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model

    async def get(self, id: int) -> T | None:
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def list(self, offset: int = 0, limit: int = 20) -> list[T]:
        result = await self.session.execute(
            select(self.model).offset(offset).limit(limit)
        )
        return result.scalars().all()

    async def create(self, obj: T) -> T:
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def update(self, obj: T) -> T:
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def delete(self, id: int) -> None:
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        obj = result.scalar_one_or_none()
        if obj:
            await self.session.delete(obj)
            await self.session.commit()


class ProductRepository(BaseRepository[Product]):
    def __init__(self, session):
        super().__init__(session, Product)


class UserRepository(BaseRepository[User]):
    def __init__(self, session):
        super().__init__(session, User)


class OrderRepository(BaseRepository[Order]):
    def __init__(self, session):
        super().__init__(session, Order)

class LocationRepository(BaseRepository[Location]):
    def __init__(self, session):
        super().__init__(session, Order)