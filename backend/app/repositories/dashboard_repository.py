from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import (
    Caja,
    Compra,
    DetalleMerma,
    DetalleVenta,
    InventarioSucursal,
    Merma,
    MetodoPago,
    OrdenCompra,
    PagoVenta,
    Producto,
    TrasladoInventario,
    TurnoCaja,
    Venta,
    VarianteProducto,
)
from app.interfaces.repositories import DashboardRepository

# Guatemala es UTC-6 (sin horario de verano). Los timestamps se guardan en UTC,
# por lo que el día calendario local inicia a las 06:00 UTC y termina a las 06:00 UTC
# del día siguiente.
GUATEMALA_OFFSET = timedelta(hours=6)


def guatemala_today() -> date:
    """Fecha del día actual en la zona America/Guatemala."""
    return (datetime.utcnow() - GUATEMALA_OFFSET).date()


def _utc_bounds(d: date) -> Tuple[datetime, datetime]:
    """Rango UTC [inicio, fin] que corresponde al día calendario local `d`."""
    inicio = datetime.combine(d, time.min) + GUATEMALA_OFFSET
    fin = datetime.combine(d, time.max) + GUATEMALA_OFFSET
    return inicio, fin


def _month_bounds(hoy: date) -> Tuple[datetime, datetime]:
    """Rango UTC [inicio, fin] del mes calendario local al que pertenece `hoy`."""
    first_gt = hoy.replace(day=1)
    if first_gt.month == 12:
        next_month = date(first_gt.year + 1, 1, 1)
    else:
        next_month = date(first_gt.year, first_gt.month + 1, 1)
    inicio, _ = _utc_bounds(first_gt)
    _, fin = _utc_bounds(next_month)
    return inicio, fin


class DashboardRepositoryImpl(DashboardRepository):
    """Único punto de acceso a datos de las métricas del Panel Principal.
    No hace commit: el Unit of Work controla la transacción.
    Carga ansiosamente (selectinload) las relaciones que se serializan para
    evitar MissingGreenlet en SQLAlchemy asincrono."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_turno_actual(self, user_id: int) -> Optional[TurnoCaja]:
        stmt = (
            select(TurnoCaja)
            .options(
                selectinload(TurnoCaja.caja).selectinload(Caja.sucursal),
                selectinload(TurnoCaja.usuario),
            )
            .where(
                TurnoCaja.id_usuario == user_id,
                TurnoCaja.estado.in_(["Abierto", "Abierta"]),
            )
            .order_by(TurnoCaja.fecha_apertura.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_ventas_hoy(self) -> Tuple[Decimal, int]:
        inicio, fin = _utc_bounds(guatemala_today())
        stmt = select(
            func.coalesce(func.sum(Venta.total_venta), 0),
            func.count(Venta.id_venta),
        ).where(Venta.fecha_venta >= inicio, Venta.fecha_venta <= fin, Venta.estado == "Completada")
        row = (await self.db.execute(stmt)).one()
        return Decimal(str(row[0])), int(row[1])

    async def get_ventas_por_dia(self, desde: date, hasta: date) -> List[Tuple[date, Decimal]]:
        """Total de ventas completadas por día calendario local del rango [desde, hasta]."""
        resultados: List[Tuple[date, Decimal]] = []
        dia = desde
        while dia <= hasta:
            inicio, fin = _utc_bounds(dia)
            stmt = select(func.coalesce(func.sum(Venta.total_venta), 0)).where(
                Venta.fecha_venta >= inicio,
                Venta.fecha_venta <= fin,
                Venta.estado == "Completada",
            )
            total = (await self.db.execute(stmt)).scalar_one()
            resultados.append((dia, Decimal(str(total))))
            dia += timedelta(days=1)
        return resultados

    async def get_ventas_por_metodo_hoy(self) -> List[Tuple[str, Decimal]]:
        inicio, fin = _utc_bounds(guatemala_today())
        stmt = (
            select(
                MetodoPago.nombre,
                func.coalesce(func.sum(PagoVenta.monto_recibido - PagoVenta.vuelto_entregado), 0),
            )
            .select_from(PagoVenta)
            .join(Venta, PagoVenta.id_venta == Venta.id_venta)
            .join(MetodoPago, PagoVenta.id_metodo_pago == MetodoPago.id_metodo_pago)
            .where(
                Venta.fecha_venta >= inicio,
                Venta.fecha_venta <= fin,
                Venta.estado == "Completada",
            )
            .group_by(MetodoPago.nombre)
            .order_by(func.sum(PagoVenta.monto_recibido - PagoVenta.vuelto_entregado).desc())
        )
        result = await self.db.execute(stmt)
        return [(row[0], Decimal(str(row[1]))) for row in result.all()]

    async def get_mermas_mes(self) -> Decimal:
        inicio, fin = _month_bounds(guatemala_today())
        stmt = (
            select(func.coalesce(func.sum(DetalleMerma.costo_perdida), 0))
            .select_from(Merma)
            .join(DetalleMerma, Merma.id_merma == DetalleMerma.id_merma)
            .where(Merma.fecha_merma >= inicio, Merma.fecha_merma < fin)
        )
        result = await self.db.execute(stmt)
        return Decimal(str(result.scalar_one()))

    async def get_ventas_top_productos(self, desde: date, hasta: date, limit: int = 5) -> List[Tuple[int, str, int, Decimal]]:
        inicio, fin = _utc_bounds(desde), _utc_bounds(hasta)
        stmt = (
            select(
                Producto.id_producto,
                Producto.nombre,
                func.sum(DetalleVenta.cantidad),
                func.sum(DetalleVenta.subtotal),
            )
            .select_from(DetalleVenta)
            .join(Venta, DetalleVenta.id_venta == Venta.id_venta)
            .join(VarianteProducto, DetalleVenta.id_variante == VarianteProducto.id_variante)
            .join(Producto, VarianteProducto.id_producto == Producto.id_producto)
            .where(
                Venta.fecha_venta >= inicio[0],
                Venta.fecha_venta <= fin[1],
                Venta.estado == "Completada",
            )
            .group_by(Producto.id_producto, Producto.nombre)
            .order_by(func.sum(DetalleVenta.cantidad).desc(), func.sum(DetalleVenta.subtotal).desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return [
            (int(row[0]), row[1], int(row[2]), Decimal(str(row[3])))
            for row in result.all()
        ]

    async def count_stock_critico(self) -> int:
        stmt = select(func.count(InventarioSucursal.id_inventario)).where(
            InventarioSucursal.stock_actual <= InventarioSucursal.stock_minimo
        )
        result = await self.db.execute(stmt)
        return int(result.scalar_one())

    async def get_stock_critico(self, limit: int = 5) -> List[InventarioSucursal]:
        stmt = (
            select(InventarioSucursal)
            .options(
                selectinload(InventarioSucursal.variante).selectinload(VarianteProducto.producto),
                selectinload(InventarioSucursal.sucursal),
            )
            .where(InventarioSucursal.stock_actual <= InventarioSucursal.stock_minimo)
            .order_by(
                (InventarioSucursal.stock_minimo - InventarioSucursal.stock_actual).desc(),
                InventarioSucursal.stock_actual.asc(),
            )
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

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

    async def get_ordenes_pendientes(self, limit: int = 5) -> List[OrdenCompra]:
        stmt = (
            select(OrdenCompra)
            .options(selectinload(OrdenCompra.proveedor))
            .where(func.lower(OrdenCompra.estado) == "emitida")
            .order_by(OrdenCompra.fecha_emision.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_traslados_pendientes(self, limit: int = 5) -> List[TrasladoInventario]:
        stmt = (
            select(TrasladoInventario)
            .options(
                selectinload(TrasladoInventario.variante).selectinload(VarianteProducto.producto),
                selectinload(TrasladoInventario.sucursal_origen),
                selectinload(TrasladoInventario.sucursal_destino),
            )
            .where(func.lower(TrasladoInventario.estado) == "en tránsito")
            .order_by(TrasladoInventario.fecha_traslado.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_ultimas_ventas(self, limit: int = 5) -> List[Venta]:
        stmt = (
            select(Venta)
            .options(selectinload(Venta.usuario))
            .where(Venta.estado == "Completada")
            .order_by(Venta.fecha_venta.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())