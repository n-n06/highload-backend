from typing import List
from fastapi import APIRouter, Depends, status
from dishka.integrations.fastapi import FromDishka, inject

from src.domain.value_objects.user_roles import UserRole
from src.infrastructure.db.models.user import User
from src.presentation.dependencies import has_permissions, get_current_active_user
from src.presentation.schemas.inventory import (
    LocationProductRead,
    LocationProductCreate,
    LocationProductUpdate,
    StockAdjustment,
    TransferRequest
)
from src.application.services.inventory import InventoryService

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
    user: User = Depends(get_current_active_user)
):
    entries = await service.list_inventory(location_id)
    return [LocationProductRead.from_orm(e) for e in entries]


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
    user: User = Depends(get_current_active_user)
):
    entry = await service.get_inventory_entry(location_id, product_id)
    return LocationProductRead.from_orm(entry)


@router.post(
    "/locations/{location_id}/products",
    response_model=LocationProductRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add product to location inventory"
)
@inject
async def create_inventory_entry(
    location_id: int,
    payload: LocationProductCreate,
    service: FromDishka[InventoryService],
    user: User = Depends(get_current_active_user),
    permissions = Depends(has_permissions([UserRole.MANAGER, UserRole.SALESMAN, UserRole.ADMIN]))
):
    entry = await service.create_inventory_entry(location_id, payload)
    return LocationProductRead.from_orm(entry)


@router.put(
    "/locations/{location_id}/products/{product_id}",
    response_model=LocationProductRead,
    summary="Update inventory stock quantity"
)
@inject
async def update_inventory_entry(
    location_id: int,
    product_id: int,
    payload: LocationProductUpdate,
    service: FromDishka[InventoryService],
    user: User = Depends(get_current_active_user),
    permissions = Depends(has_permissions([UserRole.MANAGER, UserRole.SALESMAN, UserRole.ADMIN]))
):
    entry = await service.upsert_inventory_entry(location_id, product_id, payload)
    return LocationProductRead.from_orm(entry)


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
    user: User = Depends(get_current_active_user),
    permissions = Depends(has_permissions([UserRole.MANAGER, UserRole.SALESMAN, UserRole.ADMIN]))
):
    entry = await service.adjust_inventory(location_id, product_id, adjustment)
    return LocationProductRead.from_orm(entry)


@router.post(
    "/locations/{from_location_id}/transfer",
    status_code=status.HTTP_200_OK,
    summary="Transfer products between locations"
)
@inject
async def transfer_products(
    from_location_id: int,
    payload: TransferRequest,
    service: FromDishka[InventoryService],
    user: User = Depends(get_current_active_user),
    permissions = Depends(has_permissions([UserRole.MANAGER, UserRole.SALESMAN, UserRole.ADMIN]))
):
    result = await service.transfer_inventory(from_location_id, payload)
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
    user: User = Depends(get_current_active_user),
    permissions = Depends(has_permissions([UserRole.MANAGER, UserRole.SALESMAN, UserRole.ADMIN]))
):
    result = await service.delete_inventory_entry(location_id, product_id)
    return result
