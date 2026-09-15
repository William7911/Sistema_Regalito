from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Category
from app.interfaces.repositories import CategoryRepository


class CategoryRepositoryImpl(CategoryRepository):
    """Implementación concreta del repositorio de Categorías (SQLAlchemy async)."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, category_id: int) -> Optional[Category]:
        result = await self.db.execute(select(Category).where(Category.id == category_id))
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Category]:
        result = await self.db.execute(select(Category).where(Category.name == name))
        return result.scalar_one_or_none()

    async def list_all(self, include_inactive: bool = False) -> List[Category]:
        stmt = select(Category).order_by(Category.name)
        if not include_inactive:
            stmt = stmt.where(Category.is_active.is_(True))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, category: Category) -> Category:
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        return category

    async def update(self, category: Category) -> Category:
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        return category