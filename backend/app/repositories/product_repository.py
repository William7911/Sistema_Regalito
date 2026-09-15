from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Product
from app.interfaces.repositories import ProductRepository


class ProductRepositoryImpl(ProductRepository):
    """Implementación concreta del repositorio de Productos (SQLAlchemy async)."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, product_id: int) -> Optional[Product]:
        result = await self.db.execute(
            select(Product).options(selectinload(Product.category)).where(Product.id == product_id)
        )
        return result.scalar_one_or_none()

    async def get_by_barcode(self, barcode: str) -> Optional[Product]:
        result = await self.db.execute(select(Product).where(Product.barcode == barcode))
        return result.scalar_one_or_none()

    async def get_by_sku(self, sku: str) -> Optional[Product]:
        result = await self.db.execute(select(Product).where(Product.sku == sku))
        return result.scalar_one_or_none()

    def _build_filters(
        self,
        name: Optional[str],
        sku: Optional[str],
        barcode: Optional[str],
        is_active: Optional[bool],
        category_id: Optional[int],
        created_from: Optional[str],
        created_to: Optional[str],
    ):
        conditions = []
        if name:
            conditions.append(Product.name.ilike(f"%{name}%"))
        if sku:
            conditions.append(Product.sku.ilike(f"%{sku}%"))
        if barcode:
            conditions.append(Product.barcode.ilike(f"%{barcode}%"))
        if is_active is not None:
            conditions.append(Product.is_active.is_(is_active))
        if category_id is not None:
            conditions.append(Product.category_id == category_id)
        if created_from:
            conditions.append(Product.created_at >= created_from)
        if created_to:
            conditions.append(Product.created_at <= created_to)
        return conditions

    async def search(
        self,
        name: Optional[str] = None,
        sku: Optional[str] = None,
        barcode: Optional[str] = None,
        is_active: Optional[bool] = None,
        category_id: Optional[int] = None,
        created_from: Optional[str] = None,
        created_to: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Product]:
        conditions = self._build_filters(
            name, sku, barcode, is_active, category_id, created_from, created_to
        )
        stmt = select(Product).options(selectinload(Product.category))
        if conditions:
            stmt = stmt.where(*conditions)
        stmt = stmt.order_by(Product.name).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_search(
        self,
        name: Optional[str] = None,
        sku: Optional[str] = None,
        barcode: Optional[str] = None,
        is_active: Optional[bool] = None,
        category_id: Optional[int] = None,
        created_from: Optional[str] = None,
        created_to: Optional[str] = None,
    ) -> int:
        conditions = self._build_filters(
            name, sku, barcode, is_active, category_id, created_from, created_to
        )
        stmt = select(func.count()).select_from(Product)
        if conditions:
            stmt = stmt.where(*conditions)
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def create(self, product: Product) -> Product:
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def update(self, product: Product) -> Product:
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        return product