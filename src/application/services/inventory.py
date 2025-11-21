from typing import List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.models.inventory import LocationProduct
from src.infrastructure.db.repositories.base_repo import (
    LocationProductRepository, LocationRepository, ProductRepository
)


class InventoryService:
    def __init__(
        self,
        inventory_repo: LocationProductRepository,
        location_repo: LocationRepository,
        product_repo: ProductRepository,
        session: AsyncSession
    ):
        self.inventory_repo = inventory_repo
        self.location_repo = location_repo
        self.product_repo = product_repo
        self.session = session

    async def list_inventory(self, location_id: int) -> List[LocationProduct]:
        location = await self.location_repo.get(location_id)
        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Location {location_id} not found"
            )

        return await self.inventory_repo.list_by_location(location_id)

    async def get_inventory_entry(
        self,
        location_id: int,
        product_id: int
    ) -> LocationProduct:
        entry = await self.inventory_repo.get_by_location_and_product(
            location_id, product_id
        )
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inventory entry not found"
            )
        return entry

    async def create_inventory_entry(
        self,
        location_id: int,
        product_id: int,
        quantity: int
    ) -> LocationProduct:
        location = await self.location_repo.get(location_id)
        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Location {location_id} not found"
            )

        product = await self.product_repo.get(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {product_id} not found"
            )

        existing = await self.inventory_repo.get_by_location_and_product(
            location_id, product_id
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product is already registered for this location"
            )

        if quantity < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity cannot be negative"
            )

        entry = LocationProduct(
            location_id=location_id,
            product_id=product_id,
            stock=quantity
        )

        return await self.inventory_repo.create(entry)

    async def update_inventory_entry(
        self,
        location_id: int,
        product_id: int,
        quantity: int
    ) -> LocationProduct:
        entry = await self.get_inventory_entry(location_id, product_id)

        if quantity < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity cannot be negative"
            )

        entry.stock = quantity
        await self.session.commit()
        await self.session.refresh(entry)

        return entry

    async def adjust_inventory_stock(
        self,
        location_id: int,
        product_id: int,
        delta: int
    ) -> LocationProduct:
        entry = await self.get_inventory_entry(location_id, product_id)

        new_stock = entry.stock + delta
        if new_stock < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Adjustment would result in negative stock"
            )

        entry.stock = new_stock
        await self.session.commit()
        await self.session.refresh(entry)

        return entry

    async def transfer_products(
        self,
        from_location_id: int,
        to_location_id: int,
        items: List[dict]
    ) -> dict:
        if from_location_id == to_location_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Source and destination must be different"
            )

        from_location = await self.location_repo.get(from_location_id)
        if not from_location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Source location {from_location_id} not found"
            )

        to_location = await self.location_repo.get(to_location_id)
        if not to_location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Destination location {to_location_id} not found"
            )

        for item in items:
            product_id = item['product_id']
            quantity = item['quantity']

            if quantity <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Quantity for product {product_id} must be positive"
                )

            from_inventory = await self.inventory_repo.get_by_location_and_product(
                from_location_id, product_id
            )
            if not from_inventory:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product {product_id} not found at source location"
                )

            if from_inventory.stock < quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for product {product_id}"
                )


            from_inventory.stock -= quantity


            to_inventory = await self.inventory_repo.get_by_location_and_product(
                to_location_id, product_id
            )
            if to_inventory:
                to_inventory.stock += quantity
            else:

                new_entry = LocationProduct(
                    location_id=to_location_id,
                    product_id=product_id,
                    stock=quantity
                )
                self.session.add(new_entry)

        await self.session.commit()

        return {
            "detail": f"Successfully transferred {len(items)} products from location {from_location_id} to {to_location_id}"
        }

    async def delete_inventory_entry(
        self,
        location_id: int,
        product_id: int
    ) -> dict:

        entry = await self.get_inventory_entry(location_id, product_id)
        await self.inventory_repo.delete(entry.id)

        return {
            "detail": f"Inventory entry for product {product_id} at location {location_id} deleted"
        }
