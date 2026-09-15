from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Role
from app.interfaces.repositories import RoleRepository


class RoleRepositoryImpl(RoleRepository):
    """Repositorio de Roles. No hace commit: el Unit of Work controla la transacción."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, role_id: int) -> Optional[Role]:
        result = await self.db.execute(select(Role).where(Role.id == role_id))
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Role]:
        result = await self.db.execute(select(Role).where(Role.name == name))
        return result.scalar_one_or_none()

    async def list_all(self, include_inactive: bool = False) -> List[Role]:
        stmt = select(Role).order_by(Role.name)
        if not include_inactive:
            stmt = stmt.where(Role.is_active.is_(True))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, role: Role) -> Role:
        self.db.add(role)
        await self.db.flush()
        await self.db.refresh(role)
        return role

    async def update(self, role: Role) -> Role:
        await self.db.flush()
        await self.db.refresh(role)
        return role