from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Categoria
from app.interfaces.repositories import CategoryRepository


class CategoryRepositoryImpl(CategoryRepository):
    """Implementación concreta del repositorio de Categorías (modelo relacional)."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, categoria_id: int) -> Optional[Categoria]:
        result = await self.db.execute(
            select(Categoria).where(Categoria.id_categoria == categoria_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, nombre: str) -> Optional[Categoria]:
        result = await self.db.execute(select(Categoria).where(Categoria.nombre == nombre))
        return result.scalar_one_or_none()

    async def list_all(self, include_inactive: bool = False) -> List[Categoria]:
        stmt = select(Categoria).order_by(Categoria.nombre)
        if not include_inactive:
            stmt = stmt.where(Categoria.estado == "Activo")
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, categoria: Categoria) -> Categoria:
        self.db.add(categoria)
        await self.db.flush()
        return categoria

    async def update(self, categoria: Categoria) -> Categoria:
        self.db.add(categoria)
        await self.db.flush()
        return categoria

    async def commit(self) -> None:
        await self.db.commit()