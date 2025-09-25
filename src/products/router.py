from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


from src.db import get_db
from src.products.schemas import ProductPartUpdate, ProductRead, ProductUpdate
from src.products.service import (
    create_product, get_all_products, get_product_by_id,
    update_product_info, delete_product
)


router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductRead)
async def create_new_product(
    product_data: ProductUpdate, db: AsyncSession = Depends(get_db)
):
    return await create_product(db=db, product_data=product_data)


@router.get("/", response_model=list[ProductRead])
async def list_all_products(db: AsyncSession = Depends(get_db)):
    return await get_all_products(db=db)


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    return await get_product_by_id(db=db, product_id=product_id)


@router.put("/{product_id}", response_model=ProductRead)
async def update_product(
    product_id: int, 
    product_data: ProductUpdate,
    db: AsyncSession = Depends(get_db), 
):
    return await update_product_info(
        db=db, product_id=product_id, product_data=product_data
    )


@router.patch("/{product_id}", response_model=ProductRead)
async def edit_product(
    product_id: int, 
    product_data: ProductPartUpdate,
    db: AsyncSession = Depends(get_db), 
):
    return await update_product_info(
        db=db, product_id=product_id, product_data=product_data
    )


@router.delete("/{product_id}")
async def delete_product_info(
    product_id: int, db: AsyncSession = Depends(get_db)
):
    await delete_product(db, product_id)
    return {"detail": f"Product with ID {product_id} deleted successfully."}
