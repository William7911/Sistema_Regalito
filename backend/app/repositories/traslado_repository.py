from typing import Optional, List
from datetime import date, datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import (
    TrasladoInventario, InventarioSucursal, VarianteProducto, Producto, Sucursal, Usuario
)


class TrasladoRepositoryImpl:
    """Acceso a datos asíncrono para Traslados de Inventario entre sucursales."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, traslado: TrasladoInventario) -> TrasladoInventario:
        self.db.add(traslado)
        await self.db.flush()
        return await self.get_by_id(traslado.id_traslado)

    async def get_by_id(self, id_traslado: int) -> Optional[TrasladoInventario]:
        stmt = (
            select(TrasladoInventario)
            .options(
                selectinload(TrasladoInventario.variante).selectinload(VarianteProducto.producto),
                selectinload(TrasladoInventario.sucursal_origen),
                selectinload(TrasladoInventario.sucursal_destino),
                selectinload(TrasladoInventario.usuario_envia),
                selectinload(TrasladoInventario.usuario_recibe),
            )
            .where(TrasladoInventario.id_traslado == id_traslado)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_all(
        self,
        estado: Optional[str] = None,
        id_sucursal_origen: Optional[int] = None,
        id_sucursal_destino: Optional[int] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
    ) -> List[TrasladoInventario]:
        stmt = (
            select(TrasladoInventario)
            .options(
                selectinload(TrasladoInventario.variante).selectinload(VarianteProducto.producto),
                selectinload(TrasladoInventario.sucursal_origen),
                selectinload(TrasladoInventario.sucursal_destino),
                selectinload(TrasladoInventario.usuario_envia),
                selectinload(TrasladoInventario.usuario_recibe),
            )
            .order_by(TrasladoInventario.id_traslado.desc())
        )
        if estado:
            stmt = stmt.where(TrasladoInventario.estado == estado)
        if id_sucursal_origen:
            stmt = stmt.where(TrasladoInventario.id_sucursal_origen == id_sucursal_origen)
        if id_sucursal_destino:
            stmt = stmt.where(TrasladoInventario.id_sucursal_destino == id_sucursal_destino)
        if fecha_desde:
            stmt = stmt.where(func.date(TrasladoInventario.fecha_traslado) >= fecha_desde)
        if fecha_hasta:
            stmt = stmt.where(func.date(TrasladoInventario.fecha_traslado) <= fecha_hasta)

        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_inventario_for_update(self, id_variante: int, id_sucursal: int) -> Optional[InventarioSucursal]:
        stmt = (
            select(InventarioSucursal)
            .where(
                InventarioSucursal.id_variante == id_variante,
                InventarioSucursal.id_sucursal == id_sucursal,
            )
            .with_for_update()
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_or_create_inventario(self, id_variante: int, id_sucursal: int) -> InventarioSucursal:
        inv = await self.get_inventario_for_update(id_variante, id_sucursal)
        if inv is not None:
            return inv

        inv = InventarioSucursal(
            id_variante=id_variante,
            id_sucursal=id_sucursal,
            stock_actual=0,
            stock_minimo=5,
            fecha_actualizacion=datetime.utcnow(),
        )
        self.db.add(inv)
        await self.db.flush()
        return inv

