from datetime import date, datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.models import Venta, Merma, Compra

class ReporteRepositoryImpl:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_ventas_by_date(self, inicio: date, fin: date) -> List[Venta]:
        # Para datetime, convertimos las fechas para incluir todo el día final
        dt_inicio = datetime.combine(inicio, datetime.min.time())
        dt_fin = datetime.combine(fin, datetime.max.time())
        stmt = select(Venta).where(Venta.fecha_venta >= dt_inicio, Venta.fecha_venta <= dt_fin)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_mermas_by_date(self, inicio: date, fin: date) -> List[Merma]:
        dt_inicio = datetime.combine(inicio, datetime.min.time())
        dt_fin = datetime.combine(fin, datetime.max.time())
        stmt = select(Merma).where(Merma.fecha_merma >= dt_inicio, Merma.fecha_merma <= dt_fin)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_compras_by_date(self, inicio: date, fin: date) -> List[Compra]:
        stmt = select(Compra).where(Compra.fecha_ingreso >= inicio, Compra.fecha_ingreso <= fin)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
