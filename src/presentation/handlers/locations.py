from typing import List
from fastapi import APIRouter, Depends, status
from dishka.integrations.fastapi import FromDishka, inject

from src.domain.entities import User
from src.domain.value_objects.user_roles import UserRole
from src.presentation.schemas.locations import LocationCreate, BaseLocationUpdate, LocationRead
from src.application.services.locations import LocationService
from src.infrastructure.user.dependencies import get_current_active_user, has_permissions

router = APIRouter(
    prefix="/locations",
    tags=["locations"]
)

@router.post(
    "/",
    response_model=LocationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new location"
)
@inject
async def create_location(
        location_data: LocationCreate,
        service: FromDishka[LocationService],
        permissions=Depends(has_permissions([UserRole.ADMIN])),
        current_user: User = Depends(get_current_active_user)
):
    """
    Create a new location.

    Requires ADMIN role.
    """

    # LocationAuthorizationService.require_admin(current_user)

    location = await service.create_location(location_data, current_user)
    return location


@router.get(
    "/",
    response_model=List[LocationRead],
    summary="Get all locations"
)
@inject
async def get_all_locations(
        service: FromDishka[LocationService]
):
    """
    Retrieve all locations.

    Public endpoint - no authentication required.
    """
    locations = await service.get_all_locations()
    return locations


@router.get(
    "/{location_id}",
    response_model=LocationRead,
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
    response_model=LocationRead,
    summary="Update location information"
)
@inject
async def update_location(
        location_id: int,
        location_data: BaseLocationUpdate,
        service: FromDishka[LocationService],
        current_user: User = Depends(get_current_active_user),
        permissions=Depends(has_permissions([UserRole.ADMIN]))
):
    """
    Update location information.

    Requires MANAGER role or higher.
    """
    # Authorization check
    # LocationAuthorizationService.require_manager(current_user)

    # Business logic handled by service
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
        current_user: User = Depends(get_current_active_user),
        permissions=Depends(has_permissions([UserRole.ADMIN]))
):
    """
    Delete a location.

    Requires SUPERUSER role.
    """
    # Authorization check
    # LocationAuthorizationService.require_superuser(current_user)

    # Business logic handled by service
    result = await service.delete_location(location_id, current_user)
    return result
