from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import selectinload

from src.auth.schemas import UserRole
from src.locations.schemas import LocationCreate, BaseLocationUpdate, LocationRead
from src.products_stock.models import LocationProduct
from src.utils import require_manager, require_superuser
from src.auth.dependencies import current_active_user, has_permissions
from src.locations.models import Location



async def _get_location_or_404(db: AsyncSession, location_id: int) -> Location:
    result = await db.execute(
        select(Location)
        .options(selectinload(Location.products).selectinload(LocationProduct.product))
        .where(Location.id == location_id)
    )
    location = result.scalar_one_or_none()
    if location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    return location


async def get_location_by_id(db: AsyncSession, location_id: int):
    return await _get_location_or_404(db, location_id)



async def get_all_locations(db: AsyncSession):
    result = await db.execute(
        select(Location)
        .options(selectinload(Location.products).selectinload(LocationProduct.product))
    )
    locations = result.scalars().all()
    if locations is None:
        return []

    return list(locations)



async def create_location(
    db: AsyncSession,
    location_data: LocationCreate,
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
        name=location_data.name, 
        address=location_data.address, 
        location_type=location_data.location_type
    )
    db.add(location)
    await db.commit()
    await db.refresh(location)
    return await get_location_by_id(db, location.id)


async def update_location_info(
    db: AsyncSession,
    location_id: int,
    location_data: BaseLocationUpdate,
):

    location = await get_location_by_id(db, location_id)

    for key, value in location_data.model_dump().items():
        if value is None:
            continue # skip setting the value 
        setattr(location, key, value)

    db.add(location)
    await db.commit()
    await db.refresh(location)
    return await get_location_by_id(db, location_id)


async def delete_location(
    db: AsyncSession,
    location_id: int,
):
    location = await get_location_by_id(db, location_id)

    await db.delete(location)
    await db.commit()
    return {"detail": f"Location with ID {location_id} deleted successfully."}



