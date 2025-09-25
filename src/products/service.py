from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.utils import require_superuser
from src.products.schemas import ProductUpdate
from src.products.models import Product
from auth.dependencies import current_active_user
from auth.schemas import UserRead

async def create_product(
        db: AsyncSession, name: str, description: str,
        stock: int, threshold: int,
        user: UserRead = Depends(current_active_user)
    ):
    # only superuser can create products in the system
    require_superuser(user)

    if stock < 0 or threshold < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stock or threshold for the product cannot be less than 0"
        )

    new_product = Product(
        name=name, description=description, 
        stock=stock, threshold=threshold
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
    return result.scalars().first()


async def update_product(
        db: AsyncSession, product: Product, product_data: ProductUpdate,
        user: UserRead = Depends(current_active_user)
    ):

    # only admins can edit product info
    require_superuser(user)

    for key, value in kwargs.items():
        if (key == "stock" and value < 0) or (key=="threshold" and value < 0):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Stock or threshold for the product cannot be less than 0"
            ) 
        setattr(product, key, value)
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


async def delete_product(
        db: AsyncSession, product: Product, 
        user: UserRead = Depends(current_active_user)
    ):
    require_superuser(user)

    await db.delete(product)
    await db.commit()