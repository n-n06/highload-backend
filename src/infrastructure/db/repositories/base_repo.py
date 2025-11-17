from typing import TypeVar, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.domain.protocols.db import BaseRepositoryProtocol
from src.infrastructure.db.models.location import Location
from src.infrastructure.db.models.user import User
from src.infrastructure.db.models.order import Order
from src.infrastructure.db.models.product import Product

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
        return list(result.scalars().all())

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


class ProductRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Product)


class UserRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)


class OrderRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Order)

    def _order_with_related_stmt(self):
        return (
            select(Order)
            .options(
                selectinload(Order.manager),
                selectinload(Order.delivery_guy),
                selectinload(Order.location_from),
                selectinload(Order.location_to),
                selectinload(Order.products).selectinload(OrderProduct.product)
            )
        )

    async def get(self, id: int) -> Order | None:
        result = await self.session.execute(
            self._order_with_related_stmt().where(Order.id == id)
        )
        return result.scalar_one_or_none()

    async def list(self, offset: int = 0, limit: int = 20) -> list[Order]:
        result = await self.session.execute(
            self._order_with_related_stmt().offset(offset).limit(limit)
        )
        return list(result.scalars().all())


class LocationRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Location)


class LocationProductRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, LocationProduct)

    async def get_by_location_and_product(
        self, location_id: int, product_id: int
    ) -> LocationProduct | None:
        result = await self.session.execute(
            select(LocationProduct)
            .options(selectinload(LocationProduct.product))
            .where(
                LocationProduct.location_id == location_id,
                LocationProduct.product_id == product_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_location(self, location_id: int) -> list[LocationProduct]:
        result = await self.session.execute(
            select(LocationProduct)
            .options(selectinload(LocationProduct.product))
            .where(LocationProduct.location_id == location_id)
        )
        return list(result.scalars().all())
