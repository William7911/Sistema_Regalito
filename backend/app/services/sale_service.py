from decimal import Decimal
from typing import List, Optional
from datetime import datetime
from fastapi import HTTPException
from app.db.models import Venta, DetalleVenta, PagoVenta, TurnoCaja, Usuario
from app.schemas import sale_schema
from app.core.permissions import check_user_permission


class ConcreteSaleService:
    """Lógica central de ventas y facturación (DERCAS Procesos 2 y 4).
    Aplica:
      - Validación de turno abierto (RF01)
      - Regla de mayoreo automática (RF05: cantidad >= 6 o tipo mayorista)
      - Descargo atómico de inventario
      - Validación y cuadre de pagos con cálculo de vuelto"""

    def __init__(self, uow):
        self.uow = uow

    async def registrar_venta(
        self,
        data: sale_schema.SaleCreate,
        user_id: int,
        active_shift: TurnoCaja,
        current_user: Optional[Usuario] = None,
    ) -> sale_schema.SaleResponse:
        # 1. Validar turno activo
        if not active_shift or active_shift.estado not in ("Abierto", "Abierta"):
            raise HTTPException(
                status_code=403,
                detail="Debe registrar el fondo inicial antes de vender",
            )

        # 2. Verificar si el cliente es mayorista
        is_client_wholesale = False
        if data.id_cliente:
            cliente = await self.uow.sales.get_cliente(data.id_cliente)
            if cliente and cliente.id_tipo_cliente == 2:  # 2: Mayorista según catálogo
                is_client_wholesale = True

        detalles_model: List[DetalleVenta] = []
        subtotal_bruto = Decimal("0.00")
        descuento_total = Decimal("0.00")
        total_venta = Decimal("0.00")

        # 3. Procesar líneas de venta y descargar stock atómicamente
        for item in data.items:
            variante = await self.uow.sales.get_variante(item.id_variante)
            if not variante:
                raise HTTPException(
                    status_code=404,
                    detail=f"La variante de producto con ID {item.id_variante} no existe.",
                )

            # Validar stock en la sucursal indicada
            inventario = await self.uow.sales.get_inventario(item.id_variante, data.id_sucursal)
            if not inventario:
                raise HTTPException(
                    status_code=400,
                    detail=f"No hay inventario registrado para la variante ID {item.id_variante} en la sucursal {data.id_sucursal}.",
                )

            if inventario.stock_actual < item.cantidad:
                nombre_p = variante.producto.nombre if variante.producto else f"ID {item.id_variante}"
                raise HTTPException(
                    status_code=400,
                    detail=f"Stock insuficiente para '{nombre_p}'. Disponible: {inventario.stock_actual}, Solicitado: {item.cantidad}.",
                )

            # Descargo atómico de inventario
            inventario.stock_actual -= item.cantidad

            precio_detalle = Decimal(str(variante.precio_detalle))
            precio_mayoreo = Decimal(str(variante.precio_mayoreo))
            cantidad = Decimal(item.cantidad)

            # RF05: Lógica de Mayoreo (cantidad >= 6 o cliente mayorista)
            aplica_mayoreo = item.cantidad >= 6 or is_client_wholesale
            if aplica_mayoreo:
                precio_aplicado = precio_mayoreo
                descuento_unitario = max(Decimal("0.00"), precio_detalle - precio_mayoreo)
            else:
                precio_aplicado = precio_detalle
                descuento_unitario = Decimal("0.00")

            descuento_item = descuento_unitario * cantidad
            subtotal_linea = precio_aplicado * cantidad
            linea_bruta = precio_detalle * cantidad

            subtotal_bruto += linea_bruta
            descuento_total += descuento_item
            total_venta += subtotal_linea

            detalles_model.append(
                DetalleVenta(
                    id_variante=item.id_variante,
                    cantidad=item.cantidad,
                    precio_unitario=precio_aplicado,
                    descuento_item=descuento_item,
                    subtotal=subtotal_linea,
                )
            )

        # 3.1 Validar permiso de descuento si aplica descuento
        if descuento_total > Decimal("0.00") and current_user is not None:
            has_discount = await check_user_permission(self.uow.db, current_user, "VENTA_APLICAR_DESCUENTO")
            if not has_discount:
                raise HTTPException(
                    status_code=403,
                    detail="No tiene permiso para aplicar descuentos en ventas (VENTA_APLICAR_DESCUENTO)",
                )

        # 4. Validar pagos y calcular vuelto
        total_recibido = sum(Decimal(str(p.monto_recibido)) for p in data.pagos)
        if total_recibido < total_venta:
            raise HTTPException(
                status_code=400,
                detail=f"Monto de pago insuficiente. Total venta: Q{total_venta:.2f}, Total recibido: Q{total_recibido:.2f}.",
            )

        cambio_total = max(Decimal("0.00"), total_recibido - total_venta)

        pagos_model: List[PagoVenta] = []
        # Asignar vuelto al primer pago en efectivo
        cambio_asignado = False
        for p in data.pagos:
            vuelto = Decimal("0.00")
            if p.id_metodo_pago == 1 and not cambio_asignado:
                vuelto = cambio_total
                cambio_asignado = True

            pagos_model.append(
                PagoVenta(
                    id_metodo_pago=p.id_metodo_pago,
                    monto_recibido=Decimal(str(p.monto_recibido)),
                    vuelto_entregado=vuelto,
                )
            )

        # 5. Crear cabecera de venta
        venta = Venta(
            id_turno=active_shift.id_turno,
            id_cliente=data.id_cliente,
            id_usuario=user_id,
            fecha_venta=datetime.now(),
            subtotal=subtotal_bruto,
            descuento_total=descuento_total,
            total_venta=total_venta,
            estado="Completada",
        )

        try:
            created = await self.uow.sales.create_sale(venta, detalles_model, pagos_model)
            await self.uow.commit()
        except Exception:
            await self.uow.rollback()
            raise

        fresh = await self.uow.sales.get_sale_by_id(created.id_venta)
        response = sale_schema.SaleResponse.model_validate(fresh)
        response.cambio = cambio_total
        return response

    async def list_sales(self, filters: sale_schema.SaleFilter) -> List[sale_schema.SaleResponse]:
        sales = await self.uow.sales.search(
            id_turno=filters.id_turno,
            id_cliente=filters.id_cliente,
            fecha_desde=filters.fecha_desde,
            fecha_hasta=filters.fecha_hasta,
            estado=filters.estado,
            limit=filters.limit,
            offset=filters.offset,
        )
        return [sale_schema.SaleResponse.model_validate(s) for s in sales]

    async def count_sales(self, filters: sale_schema.SaleFilter) -> int:
        return await self.uow.sales.count_search(
            id_turno=filters.id_turno,
            id_cliente=filters.id_cliente,
            fecha_desde=filters.fecha_desde,
            fecha_hasta=filters.fecha_hasta,
            estado=filters.estado,
        )

    async def get_sale(self, sale_id: int) -> sale_schema.SaleResponse:
        sale = await self.uow.sales.get_sale_by_id(sale_id)
        if not sale:
            raise HTTPException(status_code=404, detail="Venta no encontrada")
        return sale_schema.SaleResponse.model_validate(sale)

