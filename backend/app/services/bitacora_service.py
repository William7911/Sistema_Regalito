"""Servicio de consulta (solo lectura) de la bitácora de auditoría.

DERCAS: controlador delgado -> este servicio -> repositorio (sin commit).
No realiza escrituras; solo consultas filtradas por usuario, tabla, acción y
rango de fechas, con paginación.
"""
from typing import List

from app.schemas import catalogo_schema as schemas


class ConcreteBitacoraService:
    def __init__(self, uow):
        self.uow = uow

    @staticmethod
    def _to_out(b) -> schemas.BitacoraOut:
        usuario = b.__dict__.get("usuario")
        nombre = usuario.nombre_completo if (usuario and hasattr(usuario, "nombre_completo")) else None
        return schemas.BitacoraOut(
            id_bitacora=b.id_bitacora,
            id_usuario=b.id_usuario,
            tabla_afectada=b.tabla_afectada,
            accion=b.accion,
            descripcion=b.descripcion,
            fecha_hora=b.fecha_hora,
            usuario_nombre=nombre,
        )

    async def search(self, filt: schemas.BitacoraFilter) -> List[schemas.BitacoraOut]:
        items = await self.uow.bitacora.search(
            id_usuario=filt.id_usuario,
            tabla=filt.tabla,
            accion=filt.accion,
            fecha_desde=filt.fecha_desde,
            fecha_hasta=filt.fecha_hasta,
            limit=filt.limit,
            offset=filt.offset,
        )
        return [self._to_out(b) for b in items]

    async def count(self, filt: schemas.BitacoraFilter) -> int:
        return await self.uow.bitacora.count(
            id_usuario=filt.id_usuario,
            tabla=filt.tabla,
            accion=filt.accion,
            fecha_desde=filt.fecha_desde,
            fecha_hasta=filt.fecha_hasta,
        )
