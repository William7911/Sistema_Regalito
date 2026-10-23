from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import FacturaFel


class FelRepositoryImpl:
    """Acceso a datos asíncrono para la tabla factura_fel.
    Controlado por el Unit of Work: no hace commit propio."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, factura: FacturaFel) -> FacturaFel:
        self.db.add(factura)
        await self.db.flush()
        await self.db.refresh(factura)
        return factura

    async def get_by_id(self, id_factura: int) -> Optional[FacturaFel]:
        stmt = select(FacturaFel).where(FacturaFel.id_factura == id_factura)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_venta(self, id_venta: int) -> Optional[FacturaFel]:
        stmt = select(FacturaFel).where(FacturaFel.id_venta == id_venta)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_numero_dte(self, numero_dte: str) -> Optional[FacturaFel]:
        stmt = select(FacturaFel).where(FacturaFel.numero_dte == numero_dte)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_pendientes(self, limit: int = 100) -> List[FacturaFel]:
        stmt = (
            select(FacturaFel)
            .where(FacturaFel.estado.in_(("Pendiente DTE", "Contingencia")))
            .order_by(FacturaFel.id_factura.asc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update(self, factura: FacturaFel) -> FacturaFel:
        await self.db.flush()
        await self.db.refresh(factura)
        return factura
