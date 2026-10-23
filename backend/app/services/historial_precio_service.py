"""Servicio de consulta (solo lectura) del historial de precios.

DERCAS: controlador delgado -> este servicio -> repositorio (sin commit).
Permite consultar cambios de precio por producto o por variante.
"""
from decimal import Decimal
from typing import List

from app.schemas import catalogo_schema as schemas


class ConcreteHistorialPrecioService:
    def __init__(self, uow):
        self.uow = uow

    @staticmethod
    def _to_out(h) -> schemas.HistorialPrecioOut:
        usuario = h.__dict__.get("usuario")
        usuario_nombre = usuario.nombre_completo if (usuario and hasattr(usuario, "nombre_completo")) else None
        variante = h.__dict__.get("variante")
        producto = variante.producto if (variante and hasattr(variante, "producto")) else None
        producto_id = producto.id_producto if (producto and hasattr(producto, "id_producto")) else None
        producto_nombre = producto.nombre if (producto and hasattr(producto, "nombre")) else None
        variante_codigo = variante.codigo_barras if (variante and hasattr(variante, "codigo_barras")) else None

        return schemas.HistorialPrecioOut(
            id_historial=h.id_historial,
            id_variante=h.id_variante,
            id_usuario=h.id_usuario,
            precio_anterior=Decimal(h.precio_anterior),
            precio_nuevo=Decimal(h.precio_nuevo),
            fecha_modificacion=h.fecha_modificacion,
            producto_id=producto_id,
            producto_nombre=producto_nombre,
            variante_codigo_barras=variante_codigo,
            usuario_nombre=usuario_nombre,
        )

    async def search(self, filt: schemas.HistorialPrecioFilter) -> List[schemas.HistorialPrecioOut]:
        items = await self.uow.historial_precios.search(
            id_producto=filt.id_producto,
            id_variante=filt.id_variante,
            id_usuario=filt.id_usuario,
            fecha_desde=filt.fecha_desde,
            fecha_hasta=filt.fecha_hasta,
            limit=filt.limit,
            offset=filt.offset,
        )
        return [self._to_out(h) for h in items]

    async def count(self, filt: schemas.HistorialPrecioFilter) -> int:
        return await self.uow.historial_precios.count(
            id_producto=filt.id_producto,
            id_variante=filt.id_variante,
            id_usuario=filt.id_usuario,
            fecha_desde=filt.fecha_desde,
            fecha_hasta=filt.fecha_hasta,
        )
