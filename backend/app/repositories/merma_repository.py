from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.db.models import Merma, DetalleMerma, MotivoMerma, InventarioSucursal, VarianteProducto


class MermaRepositoryImpl:
    """Acceso a datos asíncrono para el módulo de Mermas (RF10).
    No realiza commit: la persistencia atómica es gobernada por el Unit of Work."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_motivos(self) -> List[MotivoMerma]:
        stmt = select(MotivoMerma).order_by(MotivoMerma.id_motivo.asc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_motivo_by_id(self, motivo_id: int) -> Optional[MotivoMerma]:
        stmt = select(MotivoMerma).where(MotivoMerma.id_motivo == motivo_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_variante(self, id_variante: int) -> Optional[VarianteProducto]:
        stmt = select(VarianteProducto).where(VarianteProducto.id_variante == id_variante)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_inventario(self, id_variante: int, id_sucursal: int) -> Optional[InventarioSucursal]:
        stmt = select(InventarioSucursal).where(
            InventarioSucursal.id_variante == id_variante,
            InventarioSucursal.id_sucursal == id_sucursal,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_merma(self, merma: Merma, detalles: List[DetalleMerma]) -> Merma:
        self.db.add(merma)
        await self.db.flush()
        await self.db.refresh(merma)

        for d in detalles:
            d.id_merma = merma.id_merma
            self.db.add(d)

        await self.db.flush()
        return merma

    async def get_merma_by_id(self, id_merma: int) -> Optional[Merma]:
        stmt = (
            select(Merma)
            .options(
                selectinload(Merma.detalles).selectinload(DetalleMerma.motivo),
                selectinload(Merma.detalles).selectinload(DetalleMerma.variante),
                selectinload(Merma.sucursal),
                selectinload(Merma.usuario),
            )
            .where(Merma.id_merma == id_merma)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    def _build_filters(
        self,
        id_sucursal: Optional[int] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
    ):
        conditions = []
        if id_sucursal is not None:
            conditions.append(Merma.id_sucursal == id_sucursal)
        if fecha_desde is not None:
            conditions.append(Merma.fecha_merma >= fecha_desde)
        if fecha_hasta is not None:
            conditions.append(Merma.fecha_merma <= fecha_hasta)
        return conditions

    async def search(
        self,
        id_sucursal: Optional[int] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Merma]:
        conditions = self._build_filters(id_sucursal, fecha_desde, fecha_hasta)
        stmt = (
            select(Merma)
            .options(
                selectinload(Merma.detalles).selectinload(DetalleMerma.motivo),
                selectinload(Merma.detalles).selectinload(DetalleMerma.variante),
            )
            .order_by(Merma.fecha_merma.desc())
        )
        if conditions:
            stmt = stmt.where(*conditions)
        stmt = stmt.limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_search(
        self,
        id_sucursal: Optional[int] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
    ) -> int:
        conditions = self._build_filters(id_sucursal, fecha_desde, fecha_hasta)
        stmt = select(func.count()).select_from(Merma)
        if conditions:
            stmt = stmt.where(*conditions)
        result = await self.db.execute(stmt)
        return result.scalar_one()

