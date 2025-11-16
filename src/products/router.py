from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from aiocache import Cache, cached
from aiocache.serializers import JsonSerializer, PickleSerializer
from src.redis.utils import make_key
from src.config import settings

from src.auth.dependencies import has_permissions
from src.auth.schemas import UserRole
from src.db import get_db
from src.products.schemas import ProductPartUpdate, ProductRead, ProductUpdate
from src.products.service import (
    create_product, get_all_products, get_product_by_id,
    update_product_info, delete_product
)


product_router = APIRouter(prefix="/products", tags=["Products"])


@product_router.post("/", response_model=ProductRead)
async def create_new_product(
    product_data: ProductUpdate, db: AsyncSession = Depends(get_db),
    permissions=Depends(has_permissions([UserRole.ADMIN]))
):
    return await create_product(db=db, product_data=product_data)

@cached(
    ttl=1000,
    cache=Cache.REDIS,
    key_builder=make_key,
    serializer=PickleSerializer(),
    endpoint=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    namespace="main"
)
@product_router.get("/", response_model=list[ProductRead])
async def list_all_products(db: AsyncSession = Depends(get_db)):
    return await get_all_products(db=db)


@product_router.get("/{product_id}", response_model=ProductRead)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    return await get_product_by_id(db=db, product_id=product_id)


@product_router.put("/{product_id}", response_model=ProductRead)
async def update_product(
    product_id: int, 
    product_data: ProductUpdate,
    db: AsyncSession = Depends(get_db), 
    permissions=Depends(has_permissions([UserRole.ADMIN]))
):
    return await update_product_info(
        db=db, product_id=product_id, product_data=product_data
    )


@product_router.patch("/{product_id}", response_model=ProductRead)
async def edit_product(
    product_id: int, 
    product_data: ProductPartUpdate,
    db: AsyncSession = Depends(get_db), 
    permissions=Depends(has_permissions([UserRole.ADMIN]))
):
    return await update_product_info(
        db=db, product_id=product_id, product_data=product_data
    )


@product_router.delete("/{product_id}")
async def delete_product_info(
    product_id: int, db: AsyncSession = Depends(get_db),
    permissions=Depends(has_permissions([UserRole.ADMIN]))
):
    await delete_product(db, product_id)
    return {"detail": f"Product with ID {product_id} deleted successfully."}
