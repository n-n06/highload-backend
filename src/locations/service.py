from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import Depends, HTTPException, status

from src.utils import require_manager, require_superuser
from src.auth.dependencies import current_active_user
from src.locations.models import Location, LocationType


async def create_location(
    db: AsyncSession,
    name: str,
    address: str,
    location_type: LocationType,
    user=Depends(current_active_user)
):
    require_superuser(user)  

    result = await db.execute(select(Location).where(Location.name == name))
    existing_location = result.scalars().first()
    if existing_location:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A location with this name already exists."
        )

    location = Location(name=name, address=address, location_type=location_type)
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


async def update_location(
    db: AsyncSession,
    location_id: int,
    name: str = None,
    address: str = None,
    location_type: LocationType = None,
    user=Depends(current_active_user)
):
    require_manager(user) 

    location = await get_location_by_id(db, location_id)

    if name:
        location.name = name
    if address:
        location.address = address
    if location_type:
        location.location_type = location_type

    db.add(location)
    await db.commit()
    await db.refresh(location)
    return location


async def delete_location(
    db: AsyncSession,
    location_id: int,
    user=Depends(current_active_user)
):
    require_superuser(user)  
    location = await get_location_by_id(db, location_id)

    await db.delete(location)
    await db.commit()
    return {"detail": f"Location with ID {location_id} deleted successfully."}