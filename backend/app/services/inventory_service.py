from typing import List, Optional
from fastapi import HTTPException, status
from app.api.deps import UnitOfWork
from app.schemas.inventory_schema import InventoryResponse, InventoryUpdate, StockAdjustment, AlertaStockResponse
from app.db.models import BitacoraAuditoria, Usuario
from datetime import datetime

class ConcreteInventoryService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def get_all_inventory(self, id_sucursal: Optional[int] = None, low_stock_only: bool = False) -> List[InventoryResponse]:
        items = await self.uow.inventory.get_all(id_sucursal=id_sucursal, low_stock_only=low_stock_only)
        responses = []
        for item in items:
            resp = InventoryResponse.model_validate(item)
            if item.variante:
                resp.variante_sku = item.variante.codigo_barras
                if item.variante.producto:
                    resp.producto_nombre = item.variante.producto.nombre
            if item.sucursal:
                resp.sucursal_nombre = item.sucursal.nombre
            responses.append(resp)
        return responses

    async def update_inventory(self, id_inventario: int, update_data: InventoryUpdate, current_user: Usuario) -> InventoryResponse:
        item = await self.uow.inventory.get_by_id(id_inventario)
        if not item:
            raise HTTPException(status_code=404, detail="Registro de inventario no encontrado")

        if update_data.stock_minimo is not None:
            item.stock_minimo = update_data.stock_minimo
        if update_data.id_area is not None:
            item.id_area = update_data.id_area

        # Auditoría
        auditoria = BitacoraAuditoria(
            id_usuario=current_user.id_usuario,
            tabla_afectada="inventario_sucursal",
            accion="UPDATE",
            descripcion=f"Actualización de inventario {id_inventario}",
            fecha_hora=datetime.utcnow()
        )
        self.uow.db.add(auditoria)

        await self.uow.commit()
        await self.uow.db.refresh(item)
        return await self._format_response(item)

    async def adjust_stock(self, id_inventario: int, adjustment: StockAdjustment, current_user: Usuario) -> InventoryResponse:
        # Bloqueo pesimista para evitar race conditions
        item = await self.uow.inventory.get_for_update(id_inventario)
        if not item:
            await self.uow.rollback()
            raise HTTPException(status_code=404, detail="Registro de inventario no encontrado")

        nuevo_stock = item.stock_actual + adjustment.cantidad
        if nuevo_stock < 0:
            await self.uow.rollback()
            raise HTTPException(status_code=400, detail="El ajuste resultaría en stock negativo")

        item.stock_actual = nuevo_stock

        # Validar alertas
        if item.stock_actual <= item.stock_minimo:
            await self.uow.inventory.create_alert(
                id_inventario=item.id_inventario,
                mensaje=f"Stock bajo en inventario {item.id_inventario}. Actual: {item.stock_actual}"
            )

        # Auditoría
        auditoria = BitacoraAuditoria(
            id_usuario=current_user.id_usuario,
            tabla_afectada="inventario_sucursal",
            accion="AJUSTE_STOCK",
            descripcion=f"Ajuste: {adjustment.cantidad}. Motivo: {adjustment.motivo}",
            fecha_hora=datetime.utcnow()
        )
        self.uow.db.add(auditoria)

        await self.uow.commit()
        # Para retornar los datos completos, lo buscamos sin for_update pero con relaciones
        item_full = await self.uow.inventory.get_by_id(id_inventario)
        return await self._format_response(item_full)

    async def _format_response(self, item) -> InventoryResponse:
        resp = InventoryResponse.model_validate(item)
        if item.variante:
            resp.variante_sku = item.variante.codigo_barras
            if item.variante.producto:
                resp.producto_nombre = item.variante.producto.nombre
        if item.sucursal:
            resp.sucursal_nombre = item.sucursal.nombre
        return resp

    async def get_alerts(self, id_sucursal: Optional[int] = None) -> List[AlertaStockResponse]:
        alertas = await self.uow.inventory.get_alerts(id_sucursal=id_sucursal)
        responses = []
        for alerta in alertas:
            resp = AlertaStockResponse.model_validate(alerta)
            inventario = alerta.inventario
            if inventario:
                resp.stock_actual = inventario.stock_actual
                resp.stock_minimo = inventario.stock_minimo
                if inventario.variante:
                    resp.variante_sku = inventario.variante.codigo_barras
                    if inventario.variante.producto:
                        resp.producto_nombre = inventario.variante.producto.nombre
            responses.append(resp)
        return responses
