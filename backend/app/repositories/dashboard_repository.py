from datetime import date, datetime
from decimal import Decimal
from typing import Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Compra, InventarioSucursal, TurnoCaja, Venta
from app.interfaces.repositories import DashboardRepository


class DashboardRepositoryImpl(DashboardRepository):
    """Único punto de acceso a datos de las métricas del Panel Principal."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_ventas_hoy(self) -> Tuple[Decimal, int]:
        dt_inicio = datetime.combine(date.today(), datetime.min.time())
        stmt = select(
            func.coalesce(func.sum(Venta.total_venta), 0),
            func.count(Venta.id_venta),
        ).where(Venta.fecha_venta >= dt_inicio, Venta.estado == "Completada")
        row = (await self.db.execute(stmt)).one()
        return Decimal(str(row[0])), int(row[1])

    async def count_stock_critico(self) -> int:
        stmt = select(func.count(InventarioSucursal.id_inventario)).where(
            InventarioSucursal.stock_actual <= InventarioSucursal.stock_minimo
        )
        result = await self.db.execute(stmt)
        return int(result.scalar_one())

    async def get_compras_mes(self) -> Tuple[Decimal, int]:
        first_day = date.today().replace(day=1)
        stmt = select(
            func.coalesce(func.sum(Compra.total_compra), 0),
            func.count(Compra.id_compra),
        ).where(Compra.fecha_ingreso >= first_day)
        row = (await self.db.execute(stmt)).one()
        return Decimal(str(row[0])), int(row[1])

    async def count_turnos_activos(self) -> int:
        stmt = select(func.count(TurnoCaja.id_turno)).where(
            TurnoCaja.estado.in_(["Abierto", "Abierta"])
        )
        result = await self.db.execute(stmt)
        return int(result.scalar_one())