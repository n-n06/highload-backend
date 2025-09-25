from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import Depends, HTTPException, status

from src.utils import require_manager, require_delivery_person
from src.auth.dependencies import current_active_user
from src.orders.models import Order
from src.locations.service import get_location_by_id


async def create_order(
    db: AsyncSession,
    delivery_guy_id: int,
    location_id: int,
    current_user=Depends(current_active_user),
):
    require_manager(current_user) 

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


async def get_all_orders(db: AsyncSession):
    result = await db.execute(select(Order))
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


async def update_order(
    db: AsyncSession,
    order_id: int,
    delivery_guy_id: int | None = None,
    status: str | None = None,
    current_user=Depends(current_active_user),
):
    require_manager(current_user) 
    order = await get_order_by_id(db, order_id)

    if delivery_guy_id is not None:
        order.delivery_guy_id = delivery_guy_id
    if status is not None:
        order.status = status

    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order


async def mark_order_delivered(
    db: AsyncSession,
    order_id: int,
    current_user=Depends(current_active_user),
):
    require_delivery_person(current_user)  

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