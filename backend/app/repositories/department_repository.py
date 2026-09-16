from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import DepartamentoGeografico
from app.interfaces.repositories import DepartmentRepository


class DepartmentRepositoryImpl(DepartmentRepository):
    """Repositorio de Departamentos (modelo DepartamentoGeografico).
    No hace commit: el Unit of Work controla la transacción."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, department_id: int) -> Optional[DepartamentoGeografico]:
        result = await self.db.execute(
            select(DepartamentoGeografico).where(DepartamentoGeografico.id_departamento == department_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, nombre: str) -> Optional[DepartamentoGeografico]:
        result = await self.db.execute(
            select(DepartamentoGeografico).where(DepartamentoGeografico.nombre == nombre)
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> List[DepartamentoGeografico]:
        stmt = select(DepartamentoGeografico).order_by(DepartamentoGeografico.nombre)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, department: DepartamentoGeografico) -> DepartamentoGeografico:
        self.db.add(department)
        await self.db.flush()
        await self.db.refresh(department)
        return department

    async def update(self, department: DepartamentoGeografico) -> DepartamentoGeografico:
        await self.db.flush()
        await self.db.refresh(department)
        return department