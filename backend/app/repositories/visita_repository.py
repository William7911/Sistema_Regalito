from typing import Optional, List
from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import VisitaSeguimiento, VisitaModuloEvaluacion, Usuario


class VisitaRepositoryImpl:
    """Acceso a datos asíncrono para Visitas de Seguimiento y Evaluación de Módulos."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, visita: VisitaSeguimiento) -> VisitaSeguimiento:
        self.db.add(visita)
        await self.db.flush()
        return await self.get_by_id(visita.id_visita)

    async def get_by_id(self, id_visita: int) -> Optional[VisitaSeguimiento]:
        stmt = (
            select(VisitaSeguimiento)
            .execution_options(populate_existing=True)
            .options(
                selectinload(VisitaSeguimiento.modulos),
                selectinload(VisitaSeguimiento.usuario),
            )
            .where(VisitaSeguimiento.id_visita == id_visita)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_all(
        self,
        estado: Optional[str] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
    ) -> List[VisitaSeguimiento]:
        stmt = (
            select(VisitaSeguimiento)
            .execution_options(populate_existing=True)
            .options(
                selectinload(VisitaSeguimiento.modulos),
                selectinload(VisitaSeguimiento.usuario),
            )
            .order_by(VisitaSeguimiento.id_visita.desc())
        )
        if estado:
            stmt = stmt.where(VisitaSeguimiento.estado == estado)
        if fecha_desde:
            stmt = stmt.where(VisitaSeguimiento.fecha_visita >= fecha_desde)
        if fecha_hasta:
            stmt = stmt.where(VisitaSeguimiento.fecha_visita <= fecha_hasta)

        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def update(self, visita: VisitaSeguimiento) -> VisitaSeguimiento:
        self.db.add(visita)
        await self.db.flush()
        return await self.get_by_id(visita.id_visita)

    async def sync_modulos(self, id_visita: int, modulos_data: list) -> List[VisitaModuloEvaluacion]:
        """Sincroniza la lista de módulos de evaluación para una visita específica."""
        stmt = select(VisitaModuloEvaluacion).where(VisitaModuloEvaluacion.id_visita == id_visita)
        res = await self.db.execute(stmt)
        existentes = {m.nombre_modulo: m for m in res.scalars().all()}

        for m_in in modulos_data:
            nombre = m_in.get("nombre_modulo") if isinstance(m_in, dict) else m_in.nombre_modulo
            resultado = m_in.get("resultado") if isinstance(m_in, dict) else m_in.resultado
            calificacion = m_in.get("calificacion") if isinstance(m_in, dict) else getattr(m_in, "calificacion", None)
            comentario = m_in.get("comentario") if isinstance(m_in, dict) else m_in.comentario

            if nombre in existentes:
                existente = existentes[nombre]
                existente.resultado = resultado
                existente.calificacion = calificacion
                existente.comentario = comentario
                self.db.add(existente)
            else:
                nuevo = VisitaModuloEvaluacion(
                    id_visita=id_visita,
                    nombre_modulo=nombre,
                    resultado=resultado,
                    calificacion=calificacion,
                    comentario=comentario,
                )
                self.db.add(nuevo)

        await self.db.flush()

        # Invalidar la relación en cualquier instancia de VisitaSeguimiento en la sesión
        for obj in list(self.db.identity_map.values()):
            if isinstance(obj, VisitaSeguimiento) and obj.id_visita == id_visita:
                self.db.expire(obj, ["modulos"])

        stmt_updated = (
            select(VisitaModuloEvaluacion)
            .where(VisitaModuloEvaluacion.id_visita == id_visita)
            .order_by(VisitaModuloEvaluacion.id_modulo_eval.asc())
        )
        res_updated = await self.db.execute(stmt_updated)
        return list(res_updated.scalars().all())
