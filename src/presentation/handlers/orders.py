from typing import List
from fastapi import APIRouter, Depends, status
from dishka.integrations.fastapi import FromDishka, inject

from src.infrastructure.db.models.user import User
from src.presentation.schemas.orders import OrderCreate, OrderRead, OrderUpdate
from src.application.services.orders import OrderService
from src.presentation.dependencies import get_current_active_user

router = APIRouter(
    prefix="/orders",
    tags=["orders"]
)


@router.post(
    "/",
    response_model=OrderRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new order"
)
@inject
async def create_order(
    order_data: OrderCreate,
    service: FromDishka[OrderService],
    user = Depends(get_current_active_user)
    ):
    order = await service.create_order(
        order_data.model_dump(),
        user
    )
    return order


@router.get(
    "/",
    response_model=List[OrderRead],
    summary="Get all orders"
)
@inject
async def get_all_orders(
    service: FromDishka[OrderService],
    offset: int = 0,
    limit: int = 20,
    user = Depends(get_current_active_user)
):
    orders = await service.get_all_orders(offset=offset, limit=limit)
    return orders


@router.get(
    "/{order_id}",
    response_model=OrderRead,
    summary="Get order by ID"
)
@inject
async def get_order(
    order_id: int,
    service: FromDishka[OrderService],
    user = Depends(get_current_active_user)
):
    order = await service.get_order_by_id(order_id)
    return order


@router.patch(
    "/{order_id}",
    response_model=OrderRead,
    summary="Update order"
)
@inject
async def update_order(
    order_id: int,
    order_data: OrderUpdate,
    service: FromDishka[OrderService],
    user = Depends(get_current_active_user)
):
    order = await service.update_order(
        order_id,
        order_data.model_dump(exclude_unset=True),
    )
    return order


@router.delete(
    "/{order_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete an order"
)
@inject
async def delete_order(
    order_id: int,
    service: FromDishka[OrderService],
    user = Depends(get_current_active_user)
):
    result = await service.delete_order(order_id)
    return result
