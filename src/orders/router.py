from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from aiocache import Cache, cached
from aiocache.serializers import JsonSerializer, PickleSerializer

from src.redis.utils import make_key
from src.config import settings
from src.auth.schemas import UserRole
from src.db import get_db
from src.auth.dependencies import current_active_user, has_permissions
from src.orders.schemas import (
    OrderCreate, OrderRead, OrderUpdate
)
from src.orders.service import (
    create_order,
    get_all_my_orders,
    get_all_orders,
    get_my_order_by_id,
    get_order_by_id,
    mark_order_delivered,
)

order_router = APIRouter(prefix="/orders", tags=["Orders"])


@order_router.post("/", response_model=OrderRead)
async def create_new_order(
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(current_active_user),
    permissions=Depends(has_permissions([UserRole.ADMIN, UserRole.MANAGER]))
):
    return await create_order(db, order_data)


@cached(
    ttl=1000,
    cache=Cache.REDIS,
    key_builder=make_key,
    serializer=PickleSerializer(),
    endpoint=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    namespace="main"
)
@order_router.get("/all/", response_model=list[OrderRead])
async def list_all_orders(
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user),
    permissions=Depends(has_permissions([UserRole.ADMIN, UserRole.DELIVERY]))
):
    return await get_all_orders(db)


@order_router.get("/all/{order_id}", response_model=OrderRead)
async def retrieve_from_all_orders(
    order_id: int, 
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user),
    permissions=Depends(has_permissions([UserRole.ADMIN, UserRole.DELIVERY]))
):
    return await get_order_by_id(db, order_id)


@order_router.get("/", response_model=list[OrderRead])
async def list_all_my_orders(
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user)
):
    return await get_all_my_orders(db, user)



@order_router.get("/{order_id}", response_model=OrderRead)
async def retrieve_order(
    order_id: int, 
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user),
):
    return await get_my_order_by_id(db, order_id)



@order_router.patch("/{order_id}", response_model=OrderRead)
async def update_order(
    order_id: int,
    order_data: OrderUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user),
    permissions=Depends(has_permissions([UserRole.ADMIN, UserRole.MANAGER]))
):
    return await update_order(
        db=db,
        order_id=order_id,
        order_data=order_data
    )



@order_router.post("/{order_id}/mark-delivered", response_model=OrderRead)
async def deliver_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user),
    permissions=Depends(has_permissions([UserRole.DELIVERY]))
):
    return await mark_order_delivered(db, order_id, user)
