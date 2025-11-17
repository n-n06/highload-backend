from typing import List
from fastapi import APIRouter, Depends, status
from dishka.integrations.fastapi import FromDishka, inject

from src.domain.entities import User, UserRole
from src.application.schemas.locations import LocationCreate, BaseLocationUpdate
from src.application.schemas.locations import LocationUpdate,LocationResponse
from src.application.services.locations import LocationService, LocationAuthorizationService
from src.presentation.dependencies import get_current_active_user

router = APIRouter(
    prefix="/locations",
    tags=["locations"]
)


@router.post(
    "/",
    response_model=LocationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new location"
)
@inject
async def create_location(
        location_data: LocationCreate,
        service: FromDishka[LocationService],
        current_user: User = Depends(get_current_active_user)
):
    LocationAuthorizationService.require_admin(current_user)

    location = await service.create_location(location_data, current_user)
    return location


@router.get(
    "/",
    response_model=List[LocationResponse],
    summary="Get all locations"
)
@inject
async def get_all_locations(
        service: FromDishka[LocationService]
):
    locations = await service.get_all_locations()
    return locations


@router.get(
    "/{location_id}",
    response_model=LocationResponse,
    summary="Get location by ID"
)
@inject
async def get_location(
        location_id: int,
        service: FromDishka[LocationService]
):
    location = await service.get_location_by_id(location_id)
    return location


@router.patch(
    "/{location_id}",
    response_model=LocationResponse,
    summary="Update location information"
)
@inject
async def update_location(
        location_id: int,
        location_data: BaseLocationUpdate,
        service: FromDishka[LocationService],
        current_user: User = Depends(get_current_active_user)
):
    LocationAuthorizationService.require_manager(current_user)

    location = await service.update_location(location_id, location_data, current_user)
    return location


@router.delete(
    "/{location_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a location"
)
@inject
async def delete_location(
        location_id: int,
        service: FromDishka[LocationService],
        current_user: User = Depends(get_current_active_user)
):
    LocationAuthorizationService.require_superuser(current_user)

    result = await service.delete_location(location_id, current_user)
    return result