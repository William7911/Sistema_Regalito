from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.db.models import Venta, DetalleVenta, PagoVenta, VarianteProducto, InventarioSucursal, Cliente


class SaleRepositoryImpl:
    """Acceso a datos asíncrono para Ventas y Pagos.
    Controlado por el Unit of Work para transacciones atómicas."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_variante(self, id_variante: int) -> Optional[VarianteProducto]:
        stmt = (
            select(VarianteProducto)
            .options(selectinload(VarianteProducto.producto))
            .where(VarianteProducto.id_variante == id_variante)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_inventario(self, id_variante: int, id_sucursal: int) -> Optional[InventarioSucursal]:
        stmt = select(InventarioSucursal).where(
            InventarioSucursal.id_variante == id_variante,
            InventarioSucursal.id_sucursal == id_sucursal,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_cliente(self, id_cliente: int) -> Optional[Cliente]:
        stmt = select(Cliente).where(Cliente.id_cliente == id_cliente)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_sale(
        self, venta: Venta, detalles: List[DetalleVenta], pagos: List[PagoVenta]
    ) -> Venta:
        self.db.add(venta)
        await self.db.flush()
        await self.db.refresh(venta)

        for det in detalles:
            det.id_venta = venta.id_venta
            self.db.add(det)

        for p in pagos:
            p.id_venta = venta.id_venta
            self.db.add(p)

        await self.db.flush()
        return venta

    async def get_sale_by_id(self, id_venta: int) -> Optional[Venta]:
        stmt = (
            select(Venta)
            .options(
                selectinload(Venta.detalles).selectinload(DetalleVenta.variante),
                selectinload(Venta.pagos),
                selectinload(Venta.cliente),
                selectinload(Venta.usuario),
                selectinload(Venta.turno),
            )
            .where(Venta.id_venta == id_venta)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    def _build_filters(
        self,
        id_turno: Optional[int] = None,
        id_cliente: Optional[int] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        estado: Optional[str] = None,
    ):
        conditions = []
        if id_turno is not None:
            conditions.append(Venta.id_turno == id_turno)
        if id_cliente is not None:
            conditions.append(Venta.id_cliente == id_cliente)
        if fecha_desde is not None:
            conditions.append(Venta.fecha_venta >= fecha_desde)
        if fecha_hasta is not None:
            conditions.append(Venta.fecha_venta <= fecha_hasta)
        if estado:
            conditions.append(Venta.estado == estado)
        return conditions

    async def search(
        self,
        id_turno: Optional[int] = None,
        id_cliente: Optional[int] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        estado: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Venta]:
        conditions = self._build_filters(id_turno, id_cliente, fecha_desde, fecha_hasta, estado)
        stmt = (
            select(Venta)
            .options(
                selectinload(Venta.detalles),
                selectinload(Venta.pagos),
            )
            .order_by(Venta.fecha_venta.desc())
        )
        if conditions:
            stmt = stmt.where(*conditions)
        stmt = stmt.limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_search(
        self,
        id_turno: Optional[int] = None,
        id_cliente: Optional[int] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        estado: Optional[str] = None,
    ) -> int:
        conditions = self._build_filters(id_turno, id_cliente, fecha_desde, fecha_hasta, estado)
        stmt = select(func.count()).select_from(Venta)
        if conditions:
            stmt = stmt.where(*conditions)
        result = await self.db.execute(stmt)
        return result.scalar_one()

