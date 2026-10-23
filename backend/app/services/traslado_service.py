from typing import Optional, List
from datetime import date, datetime
from fastapi import HTTPException

from app.db.models import TrasladoInventario
from app.schemas.traslado_schema import TrasladoCreate
from app.core.permissions import check_user_permission
from app.services.audit_service import log_action


class ConcreteTrasladoService:
    """Servicio para Traslados de Inventario entre sucursales (DERCAS).
    Aplica Unit of Work para consistencia transaccional."""

    def __init__(self, uow):
        self.uow = uow

    async def _validar_permiso(self, user_id: int, permiso: str):
        user = await self.uow.users.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        allowed = await check_user_permission(self.uow.db, user, permiso)
        if not allowed:
            raise HTTPException(
                status_code=403,
                detail=f"No tiene permisos para realizar esta acción ({permiso})"
            )

    def _enrich_traslado(self, traslado: TrasladoInventario) -> TrasladoInventario:
        if getattr(traslado, "sucursal_origen", None):
            traslado.nombre_origen = traslado.sucursal_origen.nombre
        if getattr(traslado, "sucursal_destino", None):
            traslado.nombre_destino = traslado.sucursal_destino.nombre
        if getattr(traslado, "usuario_envia", None):
            traslado.nombre_usuario_envia = traslado.usuario_envia.nombre_completo
        if getattr(traslado, "usuario_recibe", None):
            traslado.nombre_usuario_recibe = traslado.usuario_recibe.nombre_completo

        if getattr(traslado, "variante", None):
            v = traslado.variante
            traslado.codigo_barras = v.codigo_barras
            parts = [p for p in [v.talla, v.color] if p]
            traslado.variante_info = " · ".join(parts) if parts else None
            if getattr(v, "producto", None):
                traslado.nombre_producto = v.producto.nombre

        return traslado

    async def listar_traslados(
        self,
        user_id: int,
        estado: Optional[str] = None,
        id_sucursal_origen: Optional[int] = None,
        id_sucursal_destino: Optional[int] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
    ) -> List[TrasladoInventario]:
        await self._validar_permiso(user_id, "INV_INGRESAR_MERCADERIA")
        items = await self.uow.traslados.list_all(
            estado=estado,
            id_sucursal_origen=id_sucursal_origen,
            id_sucursal_destino=id_sucursal_destino,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
        )
        return [self._enrich_traslado(t) for t in items]

    async def obtener_traslado(self, id_traslado: int, user_id: int) -> TrasladoInventario:
        await self._validar_permiso(user_id, "INV_INGRESAR_MERCADERIA")
        traslado = await self.uow.traslados.get_by_id(id_traslado)
        if not traslado:
            raise HTTPException(status_code=404, detail="Traslado no encontrado")
        return self._enrich_traslado(traslado)

    async def crear_envio(self, data: TrasladoCreate, user_id: int) -> TrasladoInventario:
        await self._validar_permiso(user_id, "INV_INGRESAR_MERCADERIA")

        if data.id_sucursal_origen == data.id_sucursal_destino:
            raise HTTPException(
                status_code=400,
                detail="La sucursal origen y la sucursal destino deben ser distintas"
            )

        if data.cantidad <= 0:
            raise HTTPException(status_code=400, detail="La cantidad debe ser mayor a 0")

        # Bloqueo pesimista sobre el inventario origen
        inv_origen = await self.uow.traslados.get_inventario_for_update(
            data.id_variante, data.id_sucursal_origen
        )
        if not inv_origen or inv_origen.stock_actual < data.cantidad:
            disp = inv_origen.stock_actual if inv_origen else 0
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuficiente en sucursal origen. Disponible: {disp}, Solicitado: {data.cantidad}"
            )

        # Descontar inmediatamente del origen
        inv_origen.stock_actual -= data.cantidad
        inv_origen.fecha_actualizacion = datetime.utcnow()

        traslado = TrasladoInventario(
            id_variante=data.id_variante,
            id_sucursal_origen=data.id_sucursal_origen,
            id_sucursal_destino=data.id_sucursal_destino,
            cantidad=data.cantidad,
            fecha_traslado=datetime.utcnow(),
            estado="En tránsito",
            id_usuario_envia=user_id,
            observaciones=data.observaciones,
        )

        traslado_creado = await self.uow.traslados.create(traslado)

        await log_action(
            self.uow.db,
            id_usuario=user_id,
            tabla="traslado_inventario",
            accion="CREAR",
            descripcion=f"Despacho de traslado #{traslado_creado.id_traslado} ({data.cantidad} un.) hacia sucursal {data.id_sucursal_destino}",
        )

        await self.uow.commit()
        return self._enrich_traslado(traslado_creado)

    async def recibir_traslado(self, id_traslado: int, user_id: int) -> TrasladoInventario:
        await self._validar_permiso(user_id, "INV_INGRESAR_MERCADERIA")

        traslado = await self.uow.traslados.get_by_id(id_traslado)
        if not traslado:
            raise HTTPException(status_code=404, detail="Traslado no encontrado")

        if traslado.estado != "En tránsito":
            raise HTTPException(
                status_code=400,
                detail=f"No se puede recibir un traslado en estado {traslado.estado}"
            )

        # Sumar existencias en el inventario destino
        inv_destino = await self.uow.traslados.get_or_create_inventario(
            traslado.id_variante, traslado.id_sucursal_destino
        )
        inv_destino.stock_actual += traslado.cantidad
        inv_destino.fecha_actualizacion = datetime.utcnow()

        # Actualizar traslado
        traslado.estado = "Recibido"
        traslado.id_usuario_recibe = user_id
        traslado.fecha_recepcion = datetime.utcnow()

        await log_action(
            self.uow.db,
            id_usuario=user_id,
            tabla="traslado_inventario",
            accion="EDITAR",
            descripcion=f"Recepción de traslado #{traslado.id_traslado} en destino (sucursal {traslado.id_sucursal_destino})",
        )

        await self.uow.commit()
        return self._enrich_traslado(traslado)

    async def cancelar_traslado(self, id_traslado: int, user_id: int, motivo: Optional[str] = None) -> TrasladoInventario:
        await self._validar_permiso(user_id, "INV_INGRESAR_MERCADERIA")

        traslado = await self.uow.traslados.get_by_id(id_traslado)
        if not traslado:
            raise HTTPException(status_code=404, detail="Traslado no encontrado")

        if traslado.estado != "En tránsito":
            raise HTTPException(
                status_code=400,
                detail=f"No se puede cancelar un traslado en estado {traslado.estado}"
            )

        # Devolver existencias al inventario origen
        inv_origen = await self.uow.traslados.get_or_create_inventario(
            traslado.id_variante, traslado.id_sucursal_origen
        )
        inv_origen.stock_actual += traslado.cantidad
        inv_origen.fecha_actualizacion = datetime.utcnow()

        traslado.estado = "Cancelado"
        if motivo:
            traslado.observaciones = (traslado.observaciones or "") + f" [Cancelado: {motivo}]"

        await log_action(
            self.uow.db,
            id_usuario=user_id,
            tabla="traslado_inventario",
            accion="EDITAR",
            descripcion=f"Cancelación de traslado #{traslado.id_traslado} y devolución de stock a sucursal origen ({traslado.id_sucursal_origen})",
        )

        await self.uow.commit()
        return self._enrich_traslado(traslado)

