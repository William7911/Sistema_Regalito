from typing import Optional, List
from fastapi import HTTPException, status
from app.db.models import Product
from app.interfaces.repositories import ProductRepository, CategoryRepository
from app.interfaces.services import ProductService
from app.schemas import schemas


class ConcreteProductService(ProductService):
    """Lógica de negocio de Productos. La categoría siempre se valida contra la BD."""

    def __init__(
        self,
        product_repository: ProductRepository,
        category_repository: CategoryRepository,
    ):
        self.products = product_repository
        self.categories = category_repository

    async def list_products(self, filters: schemas.ProductFilter) -> List[schemas.Product]:
        products = await self.products.search(
            name=filters.name,
            sku=filters.sku,
            barcode=filters.barcode,
            is_active=filters.is_active,
            category_id=filters.category_id,
            created_from=filters.created_from,
            created_to=filters.created_to,
            limit=filters.limit,
            offset=filters.offset,
        )
        return [schemas.Product.model_validate(p) for p in products]

    async def count_products(self, filters: schemas.ProductFilter) -> int:
        return await self.products.count_search(
            name=filters.name,
            sku=filters.sku,
            barcode=filters.barcode,
            is_active=filters.is_active,
            category_id=filters.category_id,
            created_from=filters.created_from,
            created_to=filters.created_to,
        )

    async def get_product(self, product_id: int) -> schemas.Product:
        product = await self.products.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return schemas.Product.model_validate(product)

    async def get_by_barcode(self, barcode: str) -> schemas.Product:
        product = await self.products.get_by_barcode(barcode)
        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        if not product.is_active:
            raise HTTPException(status_code=400, detail="El producto está inactivo")
        return schemas.Product.model_validate(product)

    async def _validate_category(self, category_id: int):
        category = await self.categories.get_by_id(category_id)
        if not category:
            raise HTTPException(status_code=400, detail="La categoría especificada no existe")
        if not category.is_active:
            raise HTTPException(status_code=400, detail="La categoría especificada está inactiva")
        return category

    async def _validate_unique(self, product_id: Optional[int], barcode: Optional[str] = None, sku: Optional[str] = None):
        if barcode:
            existing = await self.products.get_by_barcode(barcode)
            if existing and existing.id != product_id:
                raise HTTPException(status_code=400, detail="Ya existe un producto con ese código de barras")
        if sku:
            existing = await self.products.get_by_sku(sku)
            if existing and existing.id != product_id:
                raise HTTPException(status_code=400, detail="Ya existe un producto con ese SKU")

    async def create_product(self, data: schemas.ProductCreate) -> schemas.Product:
        await self._validate_category(data.category_id)
        await self._validate_unique(None, data.barcode, data.sku)

        product = Product(
            name=data.name.strip(),
            sku=data.sku.strip() if data.sku else None,
            barcode=data.barcode.strip(),
            category_id=data.category_id,
            price=data.price,
            current_stock=data.current_stock,
            min_stock=data.min_stock,
        )
        created = await self.products.create(product)
        return schemas.Product.model_validate(created)

    async def update_product(
        self, product_id: int, data: schemas.ProductUpdate
    ) -> schemas.Product:
        product = await self.products.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        if data.category_id is not None:
            await self._validate_category(data.category_id)
            product.category_id = data.category_id
        if data.barcode is not None:
            barcode = data.barcode.strip()
            await self._validate_unique(product_id, barcode=barcode)
            product.barcode = barcode
        if data.sku is not None:
            sku = data.sku.strip() if data.sku else None
            await self._validate_unique(product_id, sku=sku)
            product.sku = sku
        if data.name is not None:
            product.name = data.name.strip()
        if data.price is not None:
            product.price = data.price
        if data.current_stock is not None:
            product.current_stock = data.current_stock
        if data.min_stock is not None:
            product.min_stock = data.min_stock
        if data.is_active is not None:
            product.is_active = data.is_active

        updated = await self.products.update(product)
        return schemas.Product.model_validate(updated)

    async def deactivate_product(self, product_id: int) -> schemas.Product:
        """Eliminación lógica (soft delete)."""
        product = await self.products.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        product.is_active = False
        updated = await self.products.update(product)
        return schemas.Product.model_validate(updated)