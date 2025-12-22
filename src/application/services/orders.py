from typing import List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import json

from src.domain.entities import User
from src.infrastructure.db.models import Order, OrderProduct
from src.infrastructure.db.repositories.base_repo import (
    OrderRepository, LocationRepository, LocationProductRepository
)
from src.infrastructure.redis.client import RedisClient
from src.infrastructure.redis.utils import make_key
from src.infrastructure.tasks.broker import broker


class OrderService:
    def __init__(
        self,
        order_repo: OrderRepository,
        location_repo: LocationRepository,
        inventory_repo: LocationProductRepository,
        session: AsyncSession,
        redis_client: RedisClient,
    ):
        self.order_repo = order_repo
        self.location_repo = location_repo
        self.inventory_repo = inventory_repo
        self.session = session
        self.redis_client = redis_client

    async def create_order(
        self,
        order_data: dict,
        current_user: User
    ) -> Order:
        if order_data['location_from_id'] == order_data['location_to_id']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Source and destination location must be different"
            )

        location_from = await self.location_repo.get(order_data['location_from_id'])
        if not location_from:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Source location {order_data['location_from_id']} not found"
            )

        location_to = await self.location_repo.get(order_data['location_to_id'])
        if not location_to:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Destination location {order_data['location_to_id']} not found"
            )

        if not order_data.get('products'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order must contain at least 1 product"
            )

        order = Order(
            manager_id=current_user.id,
            delivery_guy_id=order_data.get('delivery_guy_id'),
            location_from_id=order_data['location_from_id'],
            location_to_id=order_data['location_to_id'],
            status=order_data.get('status', 'pending').upper()
        )

        self.session.add(order)
        await self.session.flush()

        for item in order_data['products']:
            if item['quantity'] <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Quantity for product {item['product_id']} must be positive"
                )

            inventory = await self.inventory_repo.get_by_location_and_product(
                order_data['location_from_id'],
                item['product_id']
            )

            if not inventory:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product {item['product_id']} not found at location {order_data['location_from_id']}"
                )

            if inventory.stock < item['quantity']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for product {item['product_id']} at location {order_data['location_from_id']}"
                )


            order_product = OrderProduct(
                order_id=order.id,
                product_id=item['product_id'],
                quantity=item['quantity']
            )
            self.session.add(order_product)

            inventory.stock -= item['quantity']

        await self.session.commit()
        await self.session.refresh(order)

        await broker.kick(
            "process_order_delivery",
            order_id=order.id,
        )

        return order

    async def get_order_by_id(self, order_id: int) -> Order:
        cache_key = make_key("order", "get_by_id", order_id)
        try:
            cached_order = await self.redis_client.get(cache_key)
            if cached_order:
                return json.loads(cached_order)
        except Exception as e:
            print(f"Cache get error: {e}")

        order = await self.order_repo.get(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with ID {order_id} not found"
            )

        try:
            await self.redis_client.set(
                cache_key,
                json.dumps(order.to_dict() if hasattr(order, 'to_dict') else str(order)),
                ex=300
            )
        except Exception as e:
            print(f"Cache set error: {e}")

        return order

    async def get_all_orders(
        self,
        offset: int = 0,
        limit: int = 20
    ) -> List[Order]:
        return await self.order_repo.list(offset=offset, limit=limit)

    async def update_order(
        self,
        order_id: int,
        order_data: dict,
    ) -> Order:
        order = await self.get_order_by_id(order_id)

        if 'delivery_guy_id' in order_data:
            order.delivery_guy_id = order_data['delivery_guy_id']
        if 'status' in order_data:
            order.status = order_data['status']

        await self.session.commit()
        await self.session.refresh(order)

        cache_key = make_key("order", "get_by_id", order_id)
        try:
            await self.redis_client.delete(cache_key)
        except Exception as e:
            print(f"Cache invalidation error: {e}")

        return order

    async def delete_order(
        self,
        order_id: int,
    ) -> dict:
        await self.order_repo.delete(order_id)

        return {"detail": f"Order with ID {order_id} deleted successfully"}
