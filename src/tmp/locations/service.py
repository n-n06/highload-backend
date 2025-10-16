from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import Depends, HTTPException, status

from src import UserRole
from src import LocationCreate, BaseLocationUpdate
from src import require_manager, require_superuser
from src import current_active_user, has_permissions
from src import Location


async def create_location(
    db: AsyncSession,
    location_data: LocationCreate,
    user=Depends(current_active_user),
    permissions=Depends(has_permissions([UserRole.ADMIN]))
):

    result = await db.execute(
        select(Location).where(Location.name == location_data.name)
    )
    existing_location = result.scalars().first()
    if existing_location:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A location with this name already exists"
        )

    location = Location(
        name=location_data.name, address=location_data.address, 
        location_type=location_data.location_type
    )
    db.add(location)
    await db.commit()
    await db.refresh(location)
    return location


async def get_all_locations(db: AsyncSession):
    result = await db.execute(select(Location))
    return result.scalars().all()


async def get_location_by_id(db: AsyncSession, location_id: int):
    result = await db.execute(select(Location).where(Location.id == location_id))
    location = result.scalars().first()

    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with ID {location_id} not found."
        )

    return location


async def update_location_info(
    db: AsyncSession,
    location_id: int,
    location_data: BaseLocationUpdate,
    user=Depends(current_active_user),
    permissions=Depends(has_permissions([UserRole.ADMIN]))
):
    require_manager(user) 

    location = await get_location_by_id(db, location_id)

    for key, value in location_data.model_dump().items():
        if value is None:
            continue # skip setting the value 
        setattr(location, key, value)

    db.add(location)
    await db.commit()
    await db.refresh(location)
    return location


async def delete_location(
    db: AsyncSession,
    location_id: int,
    user=Depends(current_active_user),
    permissions=Depends(has_permissions([UserRole.ADMIN]))
):
    require_superuser(user)  
    location = await get_location_by_id(db, location_id)

    await db.delete(location)
    await db.commit()
    return {"detail": f"Location with ID {location_id} deleted successfully."}
