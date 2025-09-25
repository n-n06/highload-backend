from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


from src.db import get_db
from src.products.schemas import ProductRead, ProductUpdate
from src.products.service import (
    create_product, get_all_products, get_product_by_id,
    update_product, delete_product
)


router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductRead)
async def create_new_product(
    name: str, description: str, stock: int, 
    threshold: int, db: AsyncSession = Depends(get_db)
):
    return await create_product(db, name, description, stock, threshold)


@router.get("/", response_model=list[ProductRead])
async def list_all_products(db: AsyncSession = Depends(get_db)):
    return await get_all_products(db)


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    product = await get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=404, detail=f"Product with ID {product_id} not found."
        )
    return product


@router.put("/{product_id}", response_model=ProductRead)
async def update_product_info(
    product_id: int, 
    product_data: ProductUpdate,
    db: AsyncSession = Depends(get_db), 
):
    product = await get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=404, detail=f"Product with ID {product_id} not found."
        )
    return await update_product(db, product, product_data)


@router.delete("/{product_id}")
async def delete_product_info(
    product_id: int, db: AsyncSession = Depends(get_db)
):
    product = await get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=404, detail=f"Product with ID {product_id} not found."
        )
    await delete_product(db, product)
    return {"detail": f"Product with ID {product_id} deleted successfully."}