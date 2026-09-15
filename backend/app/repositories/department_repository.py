from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Department
from app.interfaces.repositories import DepartmentRepository


class DepartmentRepositoryImpl(DepartmentRepository):
    """Repositorio de Departamentos. No hace commit: el Unit of Work controla la transacción."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, department_id: int) -> Optional[Department]:
        result = await self.db.execute(select(Department).where(Department.id == department_id))
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Department]:
        result = await self.db.execute(select(Department).where(Department.name == name))
        return result.scalar_one_or_none()

    async def list_all(self, include_inactive: bool = False) -> List[Department]:
        stmt = select(Department).order_by(Department.name)
        if not include_inactive:
            stmt = stmt.where(Department.is_active.is_(True))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, department: Department) -> Department:
        self.db.add(department)
        await self.db.flush()
        await self.db.refresh(department)
        return department

    async def update(self, department: Department) -> Department:
        await self.db.flush()
        await self.db.refresh(department)
        return department