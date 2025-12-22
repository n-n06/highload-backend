from typing import List
from fastapi import APIRouter, status, Depends
from dishka.integrations.fastapi import inject, FromDishka

from src.application.services.products import ProductService
from src.presentation.schemas.products import ProductCreate, ProductRead, ProductUpdate
from src.presentation.dependencies import get_current_active_user, has_permissions
from src.infrastructure.db.models.user import UserRole, User


router = APIRouter(
    prefix="/products",
    tags=["products"]
)


@router.post(
    "/",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product"
)
@inject
async def create_product(
    product_data: ProductCreate,
    service: FromDishka[ProductService],
    user = Depends(get_current_active_user),
    permissions = Depends(has_permissions([UserRole.MANAGER, UserRole.ADMIN]))
):
    product = await service.create_product(product_data)
    return product


@router.get(
    "/",
    response_model=List[ProductRead],
    summary="Get all products"
)
@inject
async def get_all_products(
    service: FromDishka[ProductService],
    user = Depends(get_current_active_user),
):
    products = await service.get_all_products()
    return products


@router.get(
    "/{product_id}",
    response_model=ProductRead,
    summary="Get product by ID"
)
@inject
async def get_product(
    product_id: int,
    service: FromDishka[ProductService],
    user = Depends(get_current_active_user),
):
    product = await service.get_product_by_id(product_id)
    return product


@router.patch(
    "/{product_id}",
    response_model=ProductRead,
    summary="Update product information"
)
@inject
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    service: FromDishka[ProductService],
    user = Depends(get_current_active_user),
    permissions = Depends(has_permissions([UserRole.MANAGER, UserRole.ADMIN]))
):
    product = await service.update_product(product_id, product_data)
    return product


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a product"
)
@inject
async def delete_product(
    product_id: int,
    service: FromDishka[ProductService],
    user = Depends(get_current_active_user),
    permissions = Depends(has_permissions([UserRole.ADMIN]))
):
    result = await service.delete_product(product_id)
    return result
