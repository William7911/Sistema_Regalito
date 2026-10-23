from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.db.models import InventarioSucursal, VarianteProducto, Producto, Sucursal, AlertaStock
from datetime import datetime

class InventoryRepositoryImpl:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get_all(self, id_sucursal: Optional[int] = None, low_stock_only: bool = False) -> List[InventarioSucursal]:
        stmt = select(InventarioSucursal).options(
            selectinload(InventarioSucursal.variante).selectinload(VarianteProducto.producto),
            selectinload(InventarioSucursal.sucursal),
            selectinload(InventarioSucursal.area)
        )
        if id_sucursal:
            stmt = stmt.where(InventarioSucursal.id_sucursal == id_sucursal)
        if low_stock_only:
            stmt = stmt.where(InventarioSucursal.stock_actual <= InventarioSucursal.stock_minimo)
            
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, id_inventario: int) -> Optional[InventarioSucursal]:
        stmt = select(InventarioSucursal).options(
            selectinload(InventarioSucursal.variante).selectinload(VarianteProducto.producto),
            selectinload(InventarioSucursal.sucursal)
        ).where(InventarioSucursal.id_inventario == id_inventario)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_for_update(self, id_inventario: int) -> Optional[InventarioSucursal]:
        # Bloqueo pesimista: with_for_update evita condiciones de carrera
        stmt = (
            select(InventarioSucursal)
            .options(
                selectinload(InventarioSucursal.variante).selectinload(VarianteProducto.producto)
            )
            .where(InventarioSucursal.id_inventario == id_inventario)
            .with_for_update()
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_alert(self, id_inventario: int, mensaje: str) -> AlertaStock:
        alerta = AlertaStock(
            id_inventario=id_inventario,
            mensaje=mensaje,
            fecha_generacion=datetime.utcnow(),
            estado="Pendiente"
        )
        self.db.add(alerta)
        return alerta

    async def get_alerts(self, id_sucursal: Optional[int] = None, estado: str = "Pendiente") -> List[AlertaStock]:
        stmt = select(AlertaStock).options(
            selectinload(AlertaStock.inventario).selectinload(
                InventarioSucursal.variante
            ).selectinload(VarianteProducto.producto)
        ).where(AlertaStock.estado == estado)
        
        if id_sucursal:
            stmt = stmt.join(InventarioSucursal).where(InventarioSucursal.id_sucursal == id_sucursal)
            
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_alert_by_id(self, id_alerta: int) -> Optional[AlertaStock]:
        stmt = (
            select(AlertaStock)
            .options(
                selectinload(AlertaStock.inventario)
                .selectinload(InventarioSucursal.variante)
                .selectinload(VarianteProducto.producto)
            )
            .where(AlertaStock.id_alerta == id_alerta)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
