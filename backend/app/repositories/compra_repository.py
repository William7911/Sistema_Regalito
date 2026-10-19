from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.db.models import (
    OrdenCompra, DetalleOrdenCompra, Compra, DetalleCompra, 
    Proveedor, InventarioSucursal, VarianteProducto, BitacoraAuditoria
)

class CompraRepositoryImpl:
    """Acceso a datos asíncrono para Compras y Órdenes.
    Controlado por el Unit of Work para transacciones atómicas."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_proveedor(self, id_proveedor: int) -> Optional[Proveedor]:
        stmt = select(Proveedor).where(Proveedor.id_proveedor == id_proveedor)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_variante(self, id_variante: int) -> Optional[VarianteProducto]:
        stmt = select(VarianteProducto).where(VarianteProducto.id_variante == id_variante)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_inventario(self, id_variante: int, id_sucursal: int) -> Optional[InventarioSucursal]:
        stmt = (
            select(InventarioSucursal)
            .where(
                InventarioSucursal.id_variante == id_variante,
                InventarioSucursal.id_sucursal == id_sucursal,
            )
            .with_for_update()  # Bloqueo pesimista
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def create_orden(self, orden: OrdenCompra, detalles: List[DetalleOrdenCompra]) -> OrdenCompra:
        self.db.add(orden)
        await self.db.flush()

        for det in detalles:
            det.id_orden = orden.id_orden
            self.db.add(det)

        await self.db.flush()

        stmt = (
            select(OrdenCompra)
            .options(selectinload(OrdenCompra.detalles))
            .where(OrdenCompra.id_orden == orden.id_orden)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one()

    async def get_orden_by_id(self, id_orden: int) -> Optional[OrdenCompra]:
        stmt = (
            select(OrdenCompra)
            .options(selectinload(OrdenCompra.detalles))
            .where(OrdenCompra.id_orden == id_orden)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def add_compra(self, compra: Compra, detalles: List[DetalleCompra]) -> Compra:
        self.db.add(compra)
        await self.db.flush()
        await self.db.refresh(compra)

        for det in detalles:
            det.id_compra = compra.id_compra
            self.db.add(det)

        await self.db.flush()
        return compra

    async def add_auditoria(self, bitacora: BitacoraAuditoria):
        self.db.add(bitacora)
        await self.db.flush()
