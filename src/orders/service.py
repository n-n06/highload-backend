from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import selectinload

from src.locations.inventory_service import adjust_inventory, get_inventory_entry
from src.locations.schemas import StockAdjustment
from src.orders.schemas import OrderCreate, OrderRead, OrderUpdate
from src.auth.dependencies import current_active_user
from src.orders.models import Order, OrderProduct
from src.locations.service import get_location_by_id


def _order_with_related_items_stmt():
    """
    Used to load related models (like location, products) later
    """
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



async def _get_order_or_404(
    db: AsyncSession,
    order_id: int
):
    """
    Utility function to get orders or raise HTTP_404_NOT_FOUND
    """
    result = await db.execute(
        _order_with_related_items_stmt().where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found.",
        )
    return order



async def create_order(
    db: AsyncSession,
    order_data: OrderCreate,
    current_user=Depends(current_active_user),
):
    if order_data.location_from_id == order_data.location_to_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Source and Destination location must be different"
        )

    await get_location_by_id(db, order_data.location_from_id)
    await get_location_by_id(db, order_data.location_to_id)

    if not order_data.products:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must contain at least 1 product"
        )

    order = Order(
        manager_id=current_user.id,
        delivery_guy_id=order_data.delivery_guy_id,
        location_from_id=order_data.location_from_id,
        location_to_id=order_data.location_to_id,
        status="pending"
    )

    db.add(order)
    await db.flush()

    # check if product count is sufficient for the order
    for item in order_data.products:
        if item.quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Quantity for product {item.product_id} must be positive.",
            )

        inventory = await get_inventory_entry(
            db,
            order_data.location_from_id,
            item.product_id,
        )
        if inventory.stock < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for product {item.product_id} at location {order_data.location_from_id}.",
            )

        order_item = OrderProduct(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
        )
        db.add(order_item)

    # reduce product count in location_rfom
    for item in order_data.products:
        await adjust_inventory(
            db,
            order_data.location_from_id,
            item.product_id,
            StockAdjustment(delta=-item.quantity),
        )

    await db.commit()

    order = await _get_order_or_404(db, order.id)
    return order



async def get_all_orders(
    db: AsyncSession
):
    result = await db.execute(
        _order_with_related_items_stmt()
    )
    return result.scalars().unique().all()



async def get_all_my_orders(
    db: AsyncSession, current_user=Depends(current_active_user)
):
    result = await db.execute(
        _order_with_related_items_stmt()
        .where(Order.manager_id==current_user.id)
    )
    return result.scalars().unique().all()



async def get_order_by_id(
    db: AsyncSession,
    order_id: int,
):
    order = await _get_order_or_404(db, order_id)
    return order



async def get_my_order_by_id(
    db: AsyncSession,
    order_id: int,
    current_user=Depends(current_active_user)
):
    order = await _get_order_or_404(db, order_id)
    if not (
        order.manager_id == current_user.id
        or order.delivery_guy_id == current_user.id
        or getattr(current_user, "is_admin", False)
    ):
        raise HTTPException(status_code=403, detail="Permission denied.")
    return order



async def update_order(
    db: AsyncSession,
    order_id: int,
    payload: OrderUpdate,
) -> OrderRead:
    order = await _get_order_or_404(db, order_id)

    if payload.location_from_id == payload.location_to_id and payload.location_from_id is not None:
        raise HTTPException(
            status_code=400,
            detail="Source and destination locations must differ.",
        )

    # Ensure new locations exist if provided
    if payload.location_from_id:
        await get_location_by_id(db, payload.location_from_id)
    if payload.location_to_id:
        await get_location_by_id(db, payload.location_to_id)

    # Update simple fields
    for field, value in payload.model_dump(exclude={"products"}, exclude_unset=True).items():
        setattr(order, field, value)

    # Replace order items if requested
    if payload.products is not None:
        current_items = await db.execute(
            select(OrderProduct).where(OrderProduct.order_id == order.id)
        )
        current_items = current_items.scalars().all()
        for item in current_items:
            await adjust_inventory(
                db,
                order.location_from_id, #type: ignore
                item.product_id, #type: ignore
                StockAdjustment(delta=item.quantity), #type: ignore
            )


        await db.execute(delete(OrderProduct).where(OrderProduct.order_id == order.id))
        await db.flush()

        # Add new items and re-deduct
        for item in payload.products:
            if item.quantity <= 0:
                raise HTTPException(
                    status_code=422,
                    detail=f"Quantity for product {item.product_id} must be positive.",
                )

            inventory = await get_inventory_entry(
                db,
                order.location_from_id, #type: ignore
                item.product_id,
            )
            if inventory.stock < item.quantity: #type: ignore
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock for product {item.product_id}.",
                )

            db.add(
                OrderProduct(
                    order_id=order.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                )
            )

        for item in payload.products:
            await adjust_inventory(
                db,
                order.location_from_id, #type: ignore
                item.product_id,
                StockAdjustment(delta=-item.quantity),
            )

    await db.commit()
    order = await _get_order_or_404(db, order.id)
    return OrderRead.model_validate(order)



async def mark_order_delivered(
    db: AsyncSession,
    order_id: int,
    current_user=Depends(current_active_user)
) -> OrderRead:

    order = await _get_order_or_404(db, order_id)
    
    if order.delivery_guy_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not assigned to deliver this order."
        )

    if order.status == "delivered":
        return OrderRead.model_validate(order)

    order.status = "delivered"

    # Add stock to destination location
    for item in order.products:
        await adjust_inventory(
            db,
            order.location_to_id, #type: ignore
            item.product_id,
            StockAdjustment(delta=item.quantity),
        )

    await db.commit()
    order = await _get_order_or_404(db, order.id)
    return OrderRead.model_validate(order)
