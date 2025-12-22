from typing import TypeVar, Type
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import object_mapper, selectinload

from src.domain.entities.locations import Location
from src.domain.protocols.db import BaseRepositoryProtocol
from src.infrastructure.db.models.location import Location as LocationModel
from src.infrastructure.db.models.user import User
from src.infrastructure.db.models.order import Order, OrderProduct
from src.infrastructure.db.models.product import Product as ProductModel
from src.infrastructure.db.models.inventory import LocationProduct
from src.presentation.schemas.inventory import LocationProductRead
from src.presentation.schemas.locations import BaseLocationUpdate, LocationRead
from src.presentation.schemas.products import BaseProductUpdate, ProductCreate, ProductRead 

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
        super().__init__(session, ProductModel)

    async def create(self, data: ProductCreate) -> ProductRead:
        orm_obj = ProductModel(
            name=data.name,
            description=data.description
        )

        self.session.add(orm_obj)
        await self.session.commit()
        await self.session.refresh(orm_obj)

        # convert ORM object to Pydantic
        return ProductRead(
            id=orm_obj.id,
            name=orm_obj.name,
            description=orm_obj.description
        )

    async def list(self, offset: int = 0, limit: int = 20) -> list[ProductRead]:
        stmt = select(ProductModel).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        orm_objs = result.scalars().all()

        # convert each ORM object to Pydantic
        return [ProductRead(
            id=orm_obj.id,
            name=orm_obj.name,
            description=orm_obj.description
        ) for orm_obj in orm_objs]


    async def get(self, id: int) -> ProductRead:
        stmt = select(ProductModel).where(ProductModel.id == id)
        result = await self.session.execute(stmt)
        orm_obj = result.scalar_one_or_none()

        if orm_obj is None:
            raise HTTPException(404, f"Product with id {id} not found")

        return ProductRead(
            id=orm_obj.id,
            name=orm_obj.name,
            description=orm_obj.description
        )

    async def update(self, id: int, update_data: BaseProductUpdate) -> ProductRead:
        stmt = select(ProductModel).where(ProductModel.id == id)
        result = await self.session.execute(stmt)
        product = result.scalar_one()

        for key, value in update_data.model_dump().items():
            if value is None:
                continue # skip setting the value 
            setattr(product, key, value)
        
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return ProductRead(
            id=product.id,
            name=product.name,
            description=product.description
        )


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
        super().__init__(session, LocationModel)

    async def create(self, location_data: Location) -> LocationRead:
        """
        Create a new Location and return a Pydantic LocationRead
        """
        orm_obj = LocationModel(
            name=location_data.name,
            address=location_data.address,
            location_type=location_data.location_type,
        )

        self.session.add(orm_obj)
        await self.session.commit()
        await self.session.refresh(orm_obj)

        # convert ORM object to Pydantic
        return LocationRead(
            id=orm_obj.id,
            name=orm_obj.name,
            address=orm_obj.address,
            location_type=orm_obj.location_type
        )

    async def list(self, offset: int = 0, limit: int = 20) -> list[LocationRead]:
        stmt = select(LocationModel).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        orm_objs = result.scalars().all()

        # convert each ORM object to Pydantic
        return [LocationRead(
            id=orm_obj.id,
            name=orm_obj.name,
            address=orm_obj.address,
            location_type=orm_obj.location_type
        ) for orm_obj in orm_objs]


    async def get(self, id: int) -> LocationRead:
        stmt = select(LocationModel).where(LocationModel.id == id)
        result = await self.session.execute(stmt)
        orm_obj = result.scalar_one()

        return LocationRead(
            id=orm_obj.id,
            name=orm_obj.name,
            address=orm_obj.address,
            location_type=orm_obj.location_type
        )

    async def update(self, id: int, update_data: BaseLocationUpdate) -> LocationRead:
        stmt = select(LocationModel).where(LocationModel.id == id)
        result = await self.session.execute(stmt)
        location = result.scalar_one()

        for key, value in update_data.model_dump().items():
            if value is None:
                continue # skip setting the value 
            setattr(location, key, value)
        
        self.session.add(location)
        await self.session.commit()
        await self.session.refresh(location)
        return LocationRead(
            id=location.id,
            name=location.name,
            address=location.address,
            location_type=location.location_type
        )


class LocationProductRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

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
        return result.scalars().all()

    async def create(self, location_id: int, product_id: int, quantity: int) -> LocationProduct:
        existing_entry = await self.get_by_location_and_product(location_id, product_id)
        if existing_entry:
            existing_entry.stock += quantity
            await self.session.commit()
            await self.session.refresh(existing_entry)
            return existing_entry

        new_entry = LocationProduct(
            location_id=location_id,
            product_id=product_id,
            stock=quantity
        )
        self.session.add(new_entry)
        await self.session.commit()
        await self.session.refresh(new_entry)
        return new_entry

    async def get_inventory_entry(self, location_id: int, product_id: int) -> LocationProduct:
        entry = await self.get_by_location_and_product(location_id, product_id)
        if not entry:
            raise HTTPException(
                status_code=404,
                detail="Inventory entry not found"
            )
        return entry
