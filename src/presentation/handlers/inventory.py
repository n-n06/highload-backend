from typing import List
from fastapi import APIRouter, Depends, status
from dishka.integrations.fastapi import FromDishka, inject

from src.domain.entities import User
from src.presentation.schemas.inventory import (
    LocationProductRead,
    LocationProductCreate,
    LocationProductUpdate,
    StockAdjustment,
    TransferRequest
)
from src.application.services.inventory import InventoryService
from src.presentation.dependencies import get_current_active_user

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"]
)


@router.get(
    "/locations/{location_id}",
    response_model=List[LocationProductRead],
    summary="Get inventory for a location"
)
@inject
async def list_inventory(
    location_id: int,
    service: FromDishka[InventoryService],
    current_user: User = Depends(get_current_active_user)
):
    inventory = await service.list_inventory(location_id)
    return inventory


@router.get(
    "/locations/{location_id}/products/{product_id}",
    response_model=LocationProductRead,
    summary="Get specific inventory entry"
)
@inject
async def get_inventory_entry(
    location_id: int,
    product_id: int,
    service: FromDishka[InventoryService],
    current_user: User = Depends(get_current_active_user)
):

    entry = await service.get_inventory_entry(location_id, product_id)
    return entry


@router.post(
    "/locations/{location_id}/products",
    response_model=LocationProductRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add product to location inventory"
)
@inject
async def create_inventory_entry(
    location_id: int,
    inventory_data: LocationProductCreate,
    service: FromDishka[InventoryService],
    current_user: User = Depends(get_current_active_user)
):

    entry = await service.create_inventory_entry(
        location_id,
        inventory_data.product_id,
        inventory_data.quantity
    )
    return entry


@router.put(
    "/locations/{location_id}/products/{product_id}",
    response_model=LocationProductRead,
    summary="Update inventory stock quantity"
)
@inject
async def update_inventory_entry(
    location_id: int,
    product_id: int,
    inventory_data: LocationProductUpdate,
    service: FromDishka[InventoryService],
    current_user: User = Depends(get_current_active_user)
):

    entry = await service.update_inventory_entry(
        location_id,
        product_id,
        inventory_data.quantity
    )
    return entry


@router.post(
    "/locations/{location_id}/products/{product_id}/adjust",
    response_model=LocationProductRead,
    summary="Adjust inventory stock"
)
@inject
async def adjust_inventory_stock(
    location_id: int,
    product_id: int,
    adjustment: StockAdjustment,
    service: FromDishka[InventoryService],
    current_user: User = Depends(get_current_active_user)
):
    entry = await service.adjust_inventory_stock(
        location_id,
        product_id,
        adjustment.delta
    )
    return entry


@router.post(
    "/locations/{from_location_id}/transfer",
    status_code=status.HTTP_200_OK,
    summary="Transfer products between locations"
)
@inject
async def transfer_products(
    from_location_id: int,
    transfer_data: TransferRequest,
    service: FromDishka[InventoryService],
    current_user: User = Depends(get_current_active_user)
):

    result = await service.transfer_products(
        from_location_id,
        transfer_data.to_location_id,
        [item.model_dump() for item in transfer_data.items]
    )
    return result


@router.delete(
    "/locations/{location_id}/products/{product_id}",
    status_code=status.HTTP_200_OK,
    summary="Remove product from location inventory"
)
@inject
async def delete_inventory_entry(
    location_id: int,
    product_id: int,
    service: FromDishka[InventoryService],
    current_user: User = Depends(get_current_active_user)
):

    result = await service.delete_inventory_entry(location_id, product_id)
    return result
