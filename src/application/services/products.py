from typing import List
from fastapi import HTTPException, status

from src.infrastructure.db.repositories.base_repo import ProductRepository
from src.infrastructure.db.models.product import Product as ProductORM
from src.presentation.schemas.products import ProductCreate, ProductRead, ProductUpdate


class ProductService:
    def __init__(self, product_repo: ProductRepository):
        self.product_repo = product_repo

    async def create_product(self, product_data: ProductCreate) -> ProductRead:
        # Create ORM object
        orm_product = ProductORM(
            name=product_data.name,
            description=product_data.description,
        )

        # Persist and return Pydantic model
        created_product = await self.product_repo.create(orm_product)
        return ProductRead(
            id=created_product.id,
            name=created_product.name,
            description=created_product.description
        )

    async def get_all_products(self) -> List[ProductRead]:
        products = await self.product_repo.list()
        return [ProductRead(
            id=p.id,
            name=p.name,
            description=p.description
        ) for p in products]

    async def get_product_by_id(self, product_id: int) -> ProductRead:
        product = await self.product_repo.get(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found."
            )
        return ProductRead(
            id=product.id,
            name=product.name,
            description=product.description
        )

    async def update_product(self, product_id: int, product_data: ProductUpdate) -> ProductRead:
        # Fetch existing
        product = await self.product_repo.get(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found."
            )

        # Apply updates
        update_data = product_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(product, key, value)

        updated_product = await self.product_repo.update(product.id, product_data)
        return ProductRead(
            id=updated_product.id,
            name=updated_product.name,
            description=updated_product.description
        )

    async def delete_product(self, product_id: int) -> dict:
        product = await self.product_repo.get(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found."
            )

        await self.product_repo.delete(product_id)
        return {"detail": f"Product with ID {product_id} deleted successfully."}
