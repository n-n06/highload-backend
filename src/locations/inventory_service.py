from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


from src.products_stock.models import LocationProduct
from src.products.models import Product

from src.locations.service import get_location_by_id
from src.locations.schemas import (
    LocationProductCreate,
    LocationProductUpdate,
    StockAdjustment,
    TransferRequest,
)
from sqlalchemy import and_



async def list_inventory(
    db: AsyncSession,
    location_id: int
) -> list[LocationProduct]:
    location = await get_location_by_id(db, location_id)  # 
    stmt = (
        select(LocationProduct)
        .options(selectinload(LocationProduct.product))
        .where(LocationProduct.location_id == location.id)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_inventory_entry(
    db: AsyncSession,
    location_id: int,
    product_id: int,
) -> LocationProduct:
    stmt = (
        select(LocationProduct)
        .options(selectinload(LocationProduct.product))
        .where(
            LocationProduct.location_id == location_id,
            LocationProduct.product_id == product_id,
        )
    )
    result = await db.execute(stmt)
    entry = result.scalar_one_or_none()
    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory entry not found.",
        )
    return entry


async def create_inventory_entry(
    db: AsyncSession,
    location_id: int,
    payload: LocationProductCreate
) -> LocationProduct:
    await get_location_by_id(db, location_id)

    existing = await db.execute(
        select(LocationProduct).where(
            LocationProduct.location_id == location_id,
            LocationProduct.product_id == payload.product_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product is already registered for this location.",
        )

    if payload.quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity cannot be negative.",
        )

    entry = LocationProduct(
        location_id=location_id,
        product_id=payload.product_id,
        stock=payload.quantity,
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)

    await db.refresh(entry, attribute_names=["product"])
    return entry


async def upsert_inventory_entry(
    db: AsyncSession,
    location_id: int,
    product_id: int,
    payload: LocationProductUpdate,
) -> LocationProduct:
    await get_location_by_id(db, location_id)

    stmt = select(LocationProduct).where(
        and_(
            LocationProduct.location_id == location_id,
            LocationProduct.product_id == product_id,
        )
    )
    result = await db.execute(stmt)
    entry = result.scalar_one_or_none()

    if entry is None:
        entry = LocationProduct(
            location_id=location_id,
            product_id=product_id,
            stock=payload.quantity or 0,
        )
        db.add(entry)
    else:
        for field, value in payload.model_dump(exclude_unset=True).items():
            if field == "quantity" and value is not None and value < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Quantity cannot be negative.",
                )
            if field == "quantity" and value is not None:
                entry.stock = value

    await db.commit()
    await db.refresh(entry)
    await db.refresh(entry, attribute_names=["product"])
    return entry


async def adjust_inventory(
    db: AsyncSession,
    location_id: int,
    product_id: int,
    payload: StockAdjustment,
) -> LocationProduct:

    stmt = (
        select(LocationProduct)
        .where(
            LocationProduct.location_id == location_id,
            LocationProduct.product_id == product_id,
        )
        .with_for_update()
    )
    result = await db.execute(stmt)
    entry = result.scalar_one_or_none()
    if entry is None:
        raise HTTPException(status_code=404, detail="Inventory entry not found.")

    entry.stock += payload.delta
    if entry.stock < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stock cannot go below zero.",
        )

    await db.commit()
    await db.refresh(entry)
    await db.refresh(entry, attribute_names=["product"])
    return entry


async def delete_inventory_entry(
    db: AsyncSession,
    location_id: int,
    product_id: int
):
    entry = await get_inventory_entry(db, location_id, product_id)
    await db.delete(entry)
    await db.commit()
    return {"detail": "Inventory entry deleted."}


async def list_low_stock(
    db: AsyncSession,
    location_id: int,
    threshold: int | None = None,
) -> list[LocationProduct]:
    await get_location_by_id(db, location_id)

    stmt = (
        select(LocationProduct)
        .options(selectinload(LocationProduct.product))
        .where(LocationProduct.location_id == location_id)
    )

    if threshold is not None:
        stmt = stmt.where(LocationProduct.stock < threshold)
    else:
        stmt = stmt.where(LocationProduct.stock < Product.threshold)

    result = await db.execute(stmt)
    return list(result.scalars().unique().all())


async def transfer_inventory(
    db: AsyncSession,
    from_location_id: int,
    payload: TransferRequest,
):
    if from_location_id == payload.to_location_id:
        raise HTTPException(status_code=400, detail="Locations must be different.")

    await get_location_by_id(db, from_location_id)
    await get_location_by_id(db, payload.to_location_id)

    # Lock involved inventory rows
    for item in payload.items:
        stmt = (
            select(LocationProduct)
            .where(
                LocationProduct.location_id == from_location_id,
                LocationProduct.product_id == item.product_id,
            )
            .with_for_update()
        )
        result = await db.execute(stmt)
        entry = result.scalar_one_or_none()
        if entry is None or entry.stock < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for product {item.product_id}.",
            )

    # perform adjustments
    for item in payload.items:
        # decrement source
        stmt_src = (
            select(LocationProduct)
            .where(
                LocationProduct.location_id == from_location_id,
                LocationProduct.product_id == item.product_id,
            )
            .with_for_update()
        )
        entry_src = (await db.execute(stmt_src)).scalar_one()
        entry_src.stock -= item.quantity

        # increment (or create) destination
        stmt_dst = (
            select(LocationProduct)
            .where(
                LocationProduct.location_id == payload.to_location_id,
                LocationProduct.product_id == item.product_id,
            )
            .with_for_update()
        )
        entry_dst = (await db.execute(stmt_dst)).scalar_one_or_none()
        if entry_dst is None:
            entry_dst = LocationProduct(
                location_id=payload.to_location_id,
                product_id=item.product_id,
                stock=item.quantity,
            )
            db.add(entry_dst)
        else:
            entry_dst.stock += item.quantity

    await db.commit()
    return {"detail": "Transfer completed."}
