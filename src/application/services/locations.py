from typing import List, Optional
from fastapi import HTTPException, status

from src.domain.entities import Location, User
from src.domain.value_objects.user_roles import UserRole
from src.application.schemas.locations import LocationCreate, BaseLocationUpdate
from src.infrastructure.db.repositories.base_repo import LocationRepository



class LocationService:
    def __init__(self, location_repo: LocationRepository):
        self.location_repo = location_repo

    async def create_location(
            self,
            location_data: LocationCreate,
            current_user: User
    ) -> Location:

        location = Location(
            name=location_data.name,
            address=location_data.address,
            location_type=location_data.location_type
        )

        created_location = await self.location_repo.create(location)
        return created_location

    async def get_all_locations(self) -> List[Location]:
        return await self.location_repo.list()

    async def get_location_by_id(self, location_id: int) -> Location:
        location = await self.location_repo.get(location_id)

        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Location with ID {location_id} not found."
            )

        return location

    async def update_location(
            self,
            location_id: int,
            location_data: BaseLocationUpdate,
            current_user: User
    ) -> Location:
        location = await self.get_location_by_id(location_id)

        update_data = location_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(location, key, value)

        updated_location = await self.location_repo.update(location)
        return updated_location


    async def delete_location(
            self,
            location_id: int,
            current_user: User
    ) -> dict:
        location = await self.get_location_by_id(location_id)
        await self.location_repo.delete(location_id)

        return {"detail": f"Location with ID {location_id} deleted successfully."}