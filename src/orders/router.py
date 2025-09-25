from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db
from src.auth.dependencies import current_active_user
from src.orders.schemas import (
    OrderCreate, OrderRead, OrderUpdate, OrderPartUpdate
)
from src.orders.service import (
    create_order,
    get_all_orders,
    get_order_by_id,
    update_order_info,
    mark_order_delivered,
)

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderRead)
async def create_new_order(
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(current_active_user),
):
    return await create_order(
        db,
        delivery_guy_id=order_data.delivery_guy_id,
        location_id=order_data.location_id,
        current_user=current_user,
    )


@router.get("/", response_model=list[OrderRead])
async def list_all_orders(
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user)
):
    return await get_all_orders(db)


@router.get("/{order_id}", response_model=OrderRead)
async def retrieve_order(
    order_id: int, 
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user)
):
    return await get_order_by_id(db, order_id)


@router.put("/{order_id}", response_model=OrderRead)
async def update_order(
    order_id: int,
    order_data: OrderUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user),
):
    return await update_order_info(
        db,
        order_id,
        order_data,
        current_user=user
    )


@router.patch("/{order_id}", response_model=OrderRead)
async def edit_order(
    order_id: int,
    order_data: OrderPartUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user),
):
    return await update_order_info(
        db,
        order_id,
        order_data,
        current_user=user
    )


@router.post("/{order_id}/mark-delivered", response_model=OrderRead)
async def deliver_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user),
):
    return await mark_order_delivered(db, order_id, user)
