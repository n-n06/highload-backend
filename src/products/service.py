from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.utils import require_superuser
from src.products.schemas import BaseProductUpdate, ProductUpdate
from src.products.models import Product
from auth.dependencies import current_active_user
from auth.schemas import UserRead


async def create_product(
        db: AsyncSession, product_data: ProductUpdate, 
        user: UserRead = Depends(current_active_user)
    ):

    if product_data.stock < 0 or product_data.threshold < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stock or threshold for the product cannot be less than 0"
        )

    new_product = Product(
        name=product_data.name, description=product_data.description, 
        stock=product_data.stock, threshold=product_data.threshold
    )
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return new_product


async def get_all_products(db: AsyncSession):
    # works for any user
    result = await db.execute(select(Product))
    return result.scalars().all()


async def get_product_by_id(db: AsyncSession, product_id: int):
    # everyone can get products by IDs
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalars().first()
    if not product:
        raise HTTPException(
            status_code=404, detail=f"Product with ID {product_id} not found."
        )
    return product


async def update_product_info(
        db: AsyncSession, product_id: int, product_data: BaseProductUpdate,
        user: UserRead = Depends(current_active_user)
    ):

    product = await get_product_by_id(db=db, product_id=product_id)

    for key, value in product_data.model_dump().items():
        if (key == "stock" and value < 0) or (key=="threshold" and value < 0):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Stock or threshold for the product cannot be less than 0"
            ) 
        if value is None:
            continue # skip setting the value 
        setattr(product, key, value)
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


async def delete_product(
        db: AsyncSession, product_id: int, 
        user: UserRead = Depends(current_active_user)
    ):

    product = await get_product_by_id(db, product_id)

    await db.delete(product)
    await db.commit()
