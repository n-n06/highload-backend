from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import UserRole
from src.db import get_db
from src.auth.dependencies import current_active_user, has_permissions
from src.locations.schemas import (
    LocationProductRead,
    LocationProductCreate,
    LocationProductUpdate,
    StockAdjustment,
    TransferRequest,
)
from src.locations.inventory_service import (
    list_inventory,
    get_inventory_entry,
    create_inventory_entry,
    upsert_inventory_entry,
    adjust_inventory,
    delete_inventory_entry,
    list_low_stock,
    transfer_inventory,
)

inventory_router = APIRouter(
    prefix="/locations/{location_id}/products", tags=["Location Inventory"]
)

@inventory_router.get("/", response_model=list[LocationProductRead])
async def list_products_by_location(
    location_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user),
):
    entries = await list_inventory(db, location_id)
    return [LocationProductRead.model_validate(entry) for entry in entries]


@inventory_router.get(
    "/low-stock",
    response_model=list[LocationProductRead],
    summary="List products below threshold",
)
async def low_stock_alerts(
    location_id: int,
    threshold: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user),
):
    entries = await list_low_stock(db, location_id, threshold)
    return [LocationProductRead.model_validate(entry) for entry in entries]


@inventory_router.get("/{product_id:int}", response_model=LocationProductRead)
async def get_product_inventory_entry(
    location_id: int,
    product_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user),
):
    entry = await get_inventory_entry(db, location_id, product_id)
    return LocationProductRead.model_validate(entry)


@inventory_router.post("/", response_model=LocationProductRead, status_code=201)
async def add_product_to_location(
    location_id: int,
    payload: LocationProductCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user),
    permissions=Depends(has_permissions([UserRole.MANAGER, UserRole.ADMIN])),
):
    entry = await create_inventory_entry(db, location_id, payload)
    return LocationProductRead.model_validate(entry)


@inventory_router.put("/{product_id}", response_model=LocationProductRead)
async def upsert_product_at_location(
    location_id: int,
    product_id: int,
    payload: LocationProductUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user),
    permissions=Depends(has_permissions([UserRole.MANAGER, UserRole.ADMIN]))
):
    entry = await upsert_inventory_entry(db, location_id, product_id, payload)
    return LocationProductRead.model_validate(entry)


@inventory_router.patch("/{product_id}", response_model=LocationProductRead)
async def adjust_product_stock(
    location_id: int,
    product_id: int,
    payload: StockAdjustment,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user),
    permissions=Depends(has_permissions([UserRole.MANAGER, UserRole.ADMIN]))
):
    entry = await adjust_inventory(db, location_id, product_id, payload)
    return LocationProductRead.model_validate(entry)


@inventory_router.delete("/{product_id}")
async def remove_product_from_location(
    location_id: int,
    product_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user),
    permissions=Depends(has_permissions([UserRole.MANAGER, UserRole.ADMIN])),
):
    return await delete_inventory_entry(db, location_id, product_id, user)


@inventory_router.post("/transfer", summary="Transfer stock to another location")
async def transfer_stock(
    location_id: int,
    payload: TransferRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user),
    permissions=Depends(has_permissions([UserRole.MANAGER, UserRole.ADMIN])),
):
    return await transfer_inventory(db, location_id, payload)
