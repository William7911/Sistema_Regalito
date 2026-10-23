from typing import Optional
from decimal import Decimal
from datetime import date, datetime
from fastapi import HTTPException
from app.db.models import (
    OrdenCompra, DetalleOrdenCompra, Compra, DetalleCompra, BitacoraAuditoria, Usuario
)
from app.schemas.compras_schema import (
    OrdenCompraCreate, IngresoMercaderiaCreate
)
from app.core.permissions import check_user_permission
from app.services.audit_service import log_action

class ConcreteComprasService:
    """Servicio para Módulo de Compras (DERCAS).
    Maneja la lógica de negocio usando Unit of Work."""

    def __init__(self, uow):
        self.uow = uow

    async def _validar_permiso(self, user_id: int, permiso: str):
        # Defensa en profundidad en capa de servicio (además de los controladores)
        user = await self.uow.users.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        allowed = await check_user_permission(self.uow.db, user, permiso)
        if not allowed:
            raise HTTPException(status_code=403, detail=f"No tiene permisos para realizar esta acción ({permiso})")

    async def crear_orden(self, data: OrdenCompraCreate, user_id: int) -> OrdenCompra:
        await self._validar_permiso(user_id, "COMPRA_EMITIR_ORDEN")

        proveedor = await self.uow.compras.get_proveedor(data.id_proveedor)
        if not proveedor:
            raise HTTPException(status_code=404, detail="Proveedor no encontrado")

        total_estimado = Decimal("0.00")
        detalles_model = []

        for item in data.detalles:
            if item.cantidad_pedida <= 0:
                raise HTTPException(status_code=400, detail="La cantidad debe ser mayor a 0")
            if item.costo_pactado < 0:
                raise HTTPException(status_code=400, detail="El costo pactado no puede ser negativo")

            variante = await self.uow.compras.get_variante(item.id_variante)
            if not variante:
                raise HTTPException(status_code=404, detail=f"Variante {item.id_variante} no existe")

            subtotal = Decimal(str(item.cantidad_pedida)) * Decimal(str(item.costo_pactado))
            total_estimado += subtotal

            detalles_model.append(
                DetalleOrdenCompra(
                    id_variante=item.id_variante,
                    cantidad_pedida=item.cantidad_pedida,
                    costo_pactado=Decimal(str(item.costo_pactado))
                )
            )

        orden = OrdenCompra(
            id_proveedor=data.id_proveedor,
            id_usuario=user_id,
            fecha_emision=date.today(),
            total_estimado=total_estimado,
            estado="Emitida"
        )

        orden_creada = await self.uow.compras.create_orden(orden, detalles_model)
        await log_action(
            self.uow.db, id_usuario=user_id, accion="CREATE", tabla="orden_compra",
            descripcion=f"Emisión de orden de compra (ID: {orden_creada.id_orden}) al proveedor {data.id_proveedor} por Q{total_estimado}",
        )
        await self.uow.commit()
        return orden_creada

    async def ingresar_mercaderia(self, data: IngresoMercaderiaCreate, user_id: int) -> OrdenCompra:
        await self._validar_permiso(user_id, "INV_INGRESAR_MERCADERIA")

        if not data.id_orden:
            raise HTTPException(status_code=400, detail="Se requiere el ID de la orden de compra")
            
        orden = await self.uow.compras.get_orden_by_id(data.id_orden)
        if not orden:
            raise HTTPException(status_code=404, detail="Orden de compra no encontrada")

        if orden.estado != "Emitida":
            raise HTTPException(status_code=400, detail=f"No se puede ingresar sobre una orden en estado {orden.estado}")

        proveedor = await self.uow.compras.get_proveedor(data.id_proveedor)
        if not proveedor:
            raise HTTPException(status_code=404, detail="Proveedor no encontrado")

        subtotal_mercaderia = Decimal("0.00")
        detalles_compra = []

        for item in data.detalles:
            if item.cantidad_recibida <= 0:
                raise HTTPException(status_code=400, detail="La cantidad recibida debe ser mayor a 0")

            subtotal_linea = Decimal(str(item.cantidad_recibida)) * Decimal(str(item.costo_unitario))
            subtotal_mercaderia += subtotal_linea

            inventario = await self.uow.compras.get_inventario(item.id_variante, getattr(item, "id_sucursal", 1) or 1)
            if not inventario:
                raise HTTPException(status_code=400, detail=f"Inventario no encontrado para variante {item.id_variante}")

            inventario.stock_actual += item.cantidad_recibida

            detalles_compra.append(
                DetalleCompra(
                    id_variante=item.id_variante,
                    cantidad_recibida=item.cantidad_recibida,
                    costo_unitario=Decimal(str(item.costo_unitario)),
                    subtotal=subtotal_linea
                )
            )

        total_compra = subtotal_mercaderia + Decimal(str(data.gasto_flete)) + Decimal(str(data.gasto_cargadores))

        compra = Compra(
            id_orden=orden.id_orden,
            id_proveedor=data.id_proveedor,
            id_usuario=user_id,
            numero_factura_proveedor=data.numero_factura_proveedor,
            fecha_ingreso=date.today(),
            subtotal_mercaderia=subtotal_mercaderia,
            gasto_flete=Decimal(str(data.gasto_flete)),
            gasto_cargadores=Decimal(str(data.gasto_cargadores)),
            total_compra=total_compra
        )

        await self.uow.compras.add_compra(compra, detalles_compra)
        
        orden.estado = "Recibida"

        auditoria = BitacoraAuditoria(
            fecha_hora=datetime.now(),
            id_usuario=user_id,
            accion="INGRESO_COMPRA",
            tabla_afectada="orden_compra",
            descripcion=f"Ingreso de orden {orden.id_orden} con total {total_compra}"
        )
        await self.uow.compras.add_auditoria(auditoria)

        await self.uow.commit()
        return orden
