from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from aiocache import Cache, cached
from aiocache.serializers import JsonSerializer, PickleSerializer
from src.redis.utils import make_key
from src.config import settings

from src.db import get_db
from src.locations.service import (
    create_location,
    get_all_locations, 
    get_location_by_id, 
    update_location_info, delete_location
)
from src.locations.schemas import LocationCreate, LocationPartUpdate, LocationRead, LocationUpdate
from src.auth.dependencies import current_active_user, has_permissions
from src.auth.models import UserRole


location_router = APIRouter(prefix="/locations", tags=["Locations"])


@location_router.post("/", response_model=LocationRead)
async def create_new_location(
    location_data: LocationCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user),
    permissions=Depends(has_permissions([UserRole.ADMIN]))
):
    return await create_location(db, location_data)


@cached(
    ttl=1000,
    cache=Cache.REDIS,
    key_builder=make_key,
    serializer=PickleSerializer(),
    endpoint=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    namespace="main"
)
@location_router.get("/", response_model=list[LocationRead])
async def list_all_locations(
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user)
):
    return await get_all_locations(db)


@location_router.get("/{location_id}", response_model=LocationRead)
async def retrieve_location(
    location_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user)
):
    return await get_location_by_id(db, location_id)


@location_router.put("/{location_id}", response_model=LocationRead)
async def update_location(
    location_id: int,
    location_data: LocationUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user),
    permissions=Depends(has_permissions([UserRole.ADMIN]))
):
    return await update_location_info(db, location_id, location_data)


@location_router.patch("/{location_id}", response_model=LocationRead)
async def edit_location(
    location_id: int,
    location_data: LocationPartUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user),
    permissions=Depends(has_permissions([UserRole.ADMIN]))
):
    return await update_location_info(db, location_id, location_data)


@location_router.delete("/{location_id}", response_model=LocationRead)
async def remove_location(
    location_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user),
    permissions=Depends(has_permissions([UserRole.ADMIN]))
):
    return await delete_location(db, location_id)


# @location_router.get(
#     "/{location_id}/products",
#     response_model=list[ProductRead]
# )
# async def list_products_by_location(
#     location_id: int,
#     db: AsyncSession = Depends(get_db),
#     user = Depends(current_active_user)
# ):
#     return await get_products_by_location(
#         db=db,
#         location_id=location_id
#     )
