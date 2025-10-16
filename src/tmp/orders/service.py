from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import Depends, HTTPException, status

from src.orders.schemas import BaseOrderUpdate
from src.auth.dependencies import current_active_user
from src.orders.models import Order
from src.locations.service import get_location_by_id


async def create_order(
    db: AsyncSession,
    delivery_guy_id: int,
    location_id: int,
    current_user=Depends(current_active_user),
):
    await get_location_by_id(db, location_id)  

    new_order = Order(
        manager_id=current_user.id,
        delivery_guy_id=delivery_guy_id,
        location_id=location_id,
        status="pending",
    )
    db.add(new_order)
    await db.commit()
    await db.refresh(new_order)
    return new_order


async def get_all_orders(
        db: AsyncSession, current_user=Depends(current_active_user)
):
    result = await db.execute(
        select(Order).where(Order.manager_id==current_user.id)
    )
    return result.scalars().all()


async def get_order_by_id(db: AsyncSession, order_id: int):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalars().first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found."
        )

    return order


async def update_order_info(
    db: AsyncSession,
    order_id: int,
    order_data: BaseOrderUpdate,
    current_user=Depends(current_active_user),
):
    order = await get_order_by_id(db, order_id)

    if order.manager_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: cannot update info for this order."
        )

    for key, value in order_data.model_dump().items():
        if value is None:
            continue # skip setting the value 
        setattr(order, key, value)

    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order


async def mark_order_delivered(
    db: AsyncSession,
    order_id: int,
    current_user=Depends(current_active_user),
):
    order = await get_order_by_id(db, order_id)

    if order.delivery_guy_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not assigned to deliver this order."
        )

    order.status = "delivered"

    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order
