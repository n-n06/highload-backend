from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src import get_db
from src import (
    create_location, get_all_locations, get_location_by_id, 
    update_location_info, delete_location
)
from src import LocationCreate, LocationPartUpdate, LocationRead, LocationUpdate
from src import current_active_user, has_permissions
from src import UserRole


router = APIRouter(prefix="/locations", tags=["Locations"])


@router.post("/", response_model=LocationRead)
async def create_new_location(
    location_data: LocationCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user),
    permissions=Depends(has_permissions([UserRole.ADMIN]))
):
    return await create_location(db, location_data, user)


@router.get("/", response_model=list[LocationRead])
async def list_all_locations(
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user)
):
    return await get_all_locations(db)


@router.get("/{location_id}", response_model=LocationRead)
async def retrieve_location(
    location_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user)
):
    return await get_location_by_id(db, location_id)


@router.put("/{location_id}", response_model=LocationRead)
async def update_location(
    location_id: int,
    location_data: LocationUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user),
    permissions=Depends(has_permissions([UserRole.ADMIN]))
):
    return await update_location_info(db, location_id, location_data, user)


@router.patch("/{location_id}", response_model=LocationRead)
async def edit_location(
    location_id: int,
    location_data: LocationPartUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user),
    permissions=Depends(has_permissions([UserRole.ADMIN]))
):
    return await update_location_info(db, location_id, location_data, user)


@router.delete("/{location_id}", response_model=LocationRead)
async def remove_location(
    location_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user),
    permissions=Depends(has_permissions([UserRole.ADMIN]))
):
    return await delete_location(db, location_id, user)
