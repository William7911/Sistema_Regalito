from typing import Optional, List
from decimal import Decimal
from datetime import date, datetime
from fastapi import HTTPException
from sqlalchemy import select
from app.db.models import (
    OrdenCompra, DetalleOrdenCompra, Compra, DetalleCompra, BitacoraAuditoria, Usuario,
    Proveedor, InventarioSucursal
)
from app.schemas.compras_schema import (
    OrdenCompraCreate, IngresoMercaderiaCreate, IngresoDirectoCreate
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

    async def _validar_algun_permiso(self, user_id: int, permisos: List[str]):
        user = await self.uow.users.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        for p in permisos:
            if await check_user_permission(self.uow.db, user, p):
                return
        raise HTTPException(
            status_code=403,
            detail=f"No tiene permisos para realizar esta acción ({', '.join(permisos)})"
        )

    def _enrich_orden(self, orden: OrdenCompra) -> OrdenCompra:
        if getattr(orden, "proveedor", None):
            orden.nombre_proveedor = orden.proveedor.distribuidora or orden.proveedor.nombre_contacto
        if getattr(orden, "usuario", None):
            orden.nombre_usuario = orden.usuario.nombre_completo

        for d in getattr(orden, "detalles", []):
            if getattr(d, "variante", None):
                v = d.variante
                d.talla = v.talla
                d.color = v.color
                d.codigo_barras = v.codigo_barras
                if getattr(v, "producto", None):
                    d.nombre_producto = v.producto.nombre
        return orden

    async def listar_ordenes(
        self,
        user_id: int,
        estado: Optional[str] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        id_proveedor: Optional[int] = None,
    ) -> List[OrdenCompra]:
        await self._validar_algun_permiso(user_id, ["COMPRA_EMITIR_ORDEN", "INV_INGRESAR_MERCADERIA"])
        ordenes = await self.uow.compras.list_ordenes(
            estado=estado,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            id_proveedor=id_proveedor,
        )
        return [self._enrich_orden(o) for o in ordenes]

    async def obtener_orden(self, id_orden: int, user_id: int) -> OrdenCompra:
        await self._validar_algun_permiso(user_id, ["COMPRA_EMITIR_ORDEN", "INV_INGRESAR_MERCADERIA"])
        orden = await self.uow.compras.get_orden_by_id(id_orden)
        if not orden:
            raise HTTPException(status_code=404, detail="Orden de compra no encontrada")
        return self._enrich_orden(orden)

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
            self.uow.db, id_usuario=user_id, accion="CREAR", tabla="orden_compra",
            descripcion=f"Emisión de orden de compra (ID: {orden_creada.id_orden}) al proveedor {data.id_proveedor} por Q{total_estimado}",
        )
        await self.uow.commit()
        return self._enrich_orden(orden_creada)

    async def cancelar_orden(self, id_orden: int, user_id: int, motivo: Optional[str] = None) -> OrdenCompra:
        await self._validar_permiso(user_id, "COMPRA_EMITIR_ORDEN")

        orden = await self.uow.compras.get_orden_by_id(id_orden)
        if not orden:
            raise HTTPException(status_code=404, detail="Orden de compra no encontrada")

        if orden.estado != "Emitida":
            raise HTTPException(
                status_code=400,
                detail=f"No se puede cancelar una orden en estado {orden.estado}"
            )

        orden.estado = "Cancelada"

        desc = f"Cancelación de orden de compra (ID: {orden.id_orden})"
        if motivo:
            desc += f" - Motivo: {motivo}"

        await log_action(
            self.uow.db,
            id_usuario=user_id,
            accion="EDITAR",
            tabla="orden_compra",
            descripcion=desc,
        )
        await self.uow.commit()
        return self._enrich_orden(orden)

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

        await log_action(
            self.uow.db,
            id_usuario=user_id,
            accion="CREAR",
            tabla="compra",
            descripcion=f"Ingreso de mercadería factura {data.numero_factura_proveedor} por Q{total_compra}",
        )
        await log_action(
            self.uow.db,
            id_usuario=user_id,
            accion="EDITAR",
            tabla="orden_compra",
            descripcion=f"Recepción de orden {orden.id_orden} con total {total_compra}",
        )

        await self.uow.commit()
        return self._enrich_orden(orden)

    async def ingreso_directo(self, data: IngresoDirectoCreate, user_id: int) -> OrdenCompra:
        """Registra ingreso directo de mercadería a bodega en 1 solo paso:
        - Aumenta automáticamente el stock de cada producto.
        - Actualiza el precio de costo del producto si fue modificado.
        - Asigna proveedor general por defecto si no se especificó.
        - Guarda orden directamente en estado 'Recibida' y registra la compra."""
        await self._validar_algun_permiso(user_id, ["COMPRA_EMITIR_ORDEN", "INV_INGRESAR_MERCADERIA"])

        # 1. Determinar proveedor: si no viene o es inválido, buscar Proveedor General
        id_prov = data.id_proveedor
        proveedor = None
        if id_prov and id_prov > 0:
            proveedor = await self.uow.compras.get_proveedor(id_prov)
        
        if not proveedor:
            stmt = select(Proveedor).where(Proveedor.distribuidora.ilike("%general%"))
            res = await self.uow.db.execute(stmt)
            proveedor = res.scalars().first()
            if not proveedor:
                stmt_first = select(Proveedor).order_by(Proveedor.id_proveedor.asc())
                res_first = await self.uow.db.execute(stmt_first)
                proveedor = res_first.scalars().first()
            if not proveedor:
                raise HTTPException(status_code=404, detail="No se encontró un proveedor válido en el sistema")

        subtotal_mercaderia = Decimal("0.00")
        detalles_orden = []
        detalles_compra = []

        # 2. Procesar cada producto ingresado
        for item in data.detalles:
            if item.cantidad_recibida <= 0:
                raise HTTPException(status_code=400, detail="La cantidad debe ser mayor a 0")
            if item.costo_unitario < 0:
                raise HTTPException(status_code=400, detail="El costo unitario no puede ser negativo")

            subtotal_linea = Decimal(str(item.cantidad_recibida)) * Decimal(str(item.costo_unitario))
            subtotal_mercaderia += subtotal_linea

            # Sumar existencias al inventario de forma inmediata
            inventario = await self.uow.compras.get_inventario(item.id_variante, getattr(item, "id_sucursal", 1) or 1)
            if not inventario:
                inventario = InventarioSucursal(
                    id_variante=item.id_variante,
                    id_sucursal=1,
                    stock_actual=item.cantidad_recibida,
                    stock_minimo=5
                )
                self.uow.db.add(inventario)
            else:
                inventario.stock_actual += item.cantidad_recibida

            # Si el usuario modificó el costo unitario (> 0), actualizar el costo en base de datos
            variante = await self.uow.compras.get_variante(item.id_variante)
            if variante and item.costo_unitario > Decimal("0.00"):
                variante.costo_promedio = Decimal(str(item.costo_unitario))

            detalles_orden.append(
                DetalleOrdenCompra(
                    id_variante=item.id_variante,
                    cantidad_pedida=item.cantidad_recibida,
                    costo_pactado=Decimal(str(item.costo_unitario))
                )
            )
            detalles_compra.append(
                DetalleCompra(
                    id_variante=item.id_variante,
                    cantidad_recibida=item.cantidad_recibida,
                    costo_unitario=Decimal(str(item.costo_unitario)),
                    subtotal=subtotal_linea
                )
            )

        # 3. Guardar orden de compra directamente como 'Recibida'
        orden = OrdenCompra(
            id_proveedor=proveedor.id_proveedor,
            id_usuario=user_id,
            fecha_emision=date.today(),
            total_estimado=subtotal_mercaderia,
            estado="Recibida"
        )
        orden_creada = await self.uow.compras.create_orden(orden, detalles_orden)

        # 4. Crear registro en tabla compra
        factura_num = data.numero_factura_proveedor.strip() if data.numero_factura_proveedor else f"ING-{orden_creada.id_orden}"
        total_compra = subtotal_mercaderia + Decimal(str(data.gasto_flete)) + Decimal(str(data.gasto_cargadores))

        compra = Compra(
            id_orden=orden_creada.id_orden,
            id_proveedor=proveedor.id_proveedor,
            id_usuario=user_id,
            numero_factura_proveedor=factura_num,
            fecha_ingreso=date.today(),
            subtotal_mercaderia=subtotal_mercaderia,
            gasto_flete=Decimal(str(data.gasto_flete)),
            gasto_cargadores=Decimal(str(data.gasto_cargadores)),
            total_compra=total_compra
        )
        await self.uow.compras.add_compra(compra, detalles_compra)

        # 5. Auditoría
        await log_action(
            self.uow.db, id_usuario=user_id, accion="CREAR", tabla="compra",
            descripcion=f"Ingreso directo de mercadería (Orden #{orden_creada.id_orden}, Factura {factura_num}) por Q{total_compra}"
        )
        await log_action(
            self.uow.db, id_usuario=user_id, accion="CREAR", tabla="orden_compra",
            descripcion=f"Ingreso directo de orden de compra #{orden_creada.id_orden} por Q{total_compra}"
        )

        await self.uow.commit()
        return self._enrich_orden(orden_creada)
