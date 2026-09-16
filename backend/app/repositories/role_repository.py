from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Rol
from app.interfaces.repositories import RoleRepository


class RoleRepositoryImpl(RoleRepository):
    """Repositorio de Roles (modelo Rol). No hace commit: el Unit of Work controla la transacción."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, role_id: int) -> Optional[Rol]:
        result = await self.db.execute(select(Rol).where(Rol.id_rol == role_id))
        return result.scalar_one_or_none()

    async def get_by_name(self, nombre: str) -> Optional[Rol]:
        result = await self.db.execute(select(Rol).where(Rol.nombre == nombre))
        return result.scalar_one_or_none()

    async def list_all(self, include_inactive: bool = False) -> List[Rol]:
        stmt = select(Rol).order_by(Rol.nombre)
        if not include_inactive:
            stmt = stmt.where(Rol.estado == "Activo")
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, rol: Rol) -> Rol:
        self.db.add(rol)
        await self.db.flush()
        await self.db.refresh(rol)
        return rol

    async def update(self, rol: Rol) -> Rol:
        await self.db.flush()
        await self.db.refresh(rol)
        return rol