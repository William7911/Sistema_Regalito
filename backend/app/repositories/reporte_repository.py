from datetime import date, datetime, time
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.db.models import Venta, Merma, Compra, Usuario, Cliente, Municipio, ClienteContacto


class ReporteRepositoryImpl:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_ventas_by_date(self, inicio: date, fin: date) -> List[Venta]:
        dt_inicio = datetime.combine(inicio, datetime.min.time())
        dt_fin = datetime.combine(fin, datetime.max.time())
        stmt = select(Venta).where(Venta.fecha_venta >= dt_inicio, Venta.fecha_venta <= dt_fin)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_mermas_by_date(self, inicio: date, fin: date) -> List[Merma]:
        dt_inicio = datetime.combine(inicio, datetime.min.time())
        dt_fin = datetime.combine(fin, datetime.max.time())
        stmt = select(Merma).where(Merma.fecha_merma >= dt_inicio, Merma.fecha_merma <= dt_fin)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_compras_by_date(self, inicio: date, fin: date) -> List[Compra]:
        stmt = select(Compra).where(Compra.fecha_ingreso >= inicio, Compra.fecha_ingreso <= fin)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # ---------------------------------------------------------------------------
    # Consultas para Reportes de Usuarios y Clientes
    # ---------------------------------------------------------------------------

    async def get_usuarios_reporte(
        self,
        estado: Optional[str] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
    ) -> List[Usuario]:
        stmt = (
            select(Usuario)
            .options(selectinload(Usuario.rol))
            .order_by(Usuario.id_usuario.asc())
        )
        if estado:
            stmt = stmt.where(func.lower(Usuario.estado) == func.lower(estado))
        if fecha_desde:
            stmt = stmt.where(Usuario.fecha_creacion >= datetime.combine(fecha_desde, time.min))
        if fecha_hasta:
            stmt = stmt.where(Usuario.fecha_creacion <= datetime.combine(fecha_hasta, time.max))

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_usuario_by_id(self, id_usuario: int) -> Optional[Usuario]:
        stmt = (
            select(Usuario)
            .options(selectinload(Usuario.rol))
            .where(Usuario.id_usuario == id_usuario)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_clientes_reporte(
        self,
        estado: Optional[str] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
    ) -> List[Cliente]:
        stmt = (
            select(Cliente)
            .options(
                selectinload(Cliente.tipo_cliente),
                selectinload(Cliente.municipio).selectinload(Municipio.departamento),
                selectinload(Cliente.contactos),
            )
            .order_by(Cliente.id_cliente.asc())
        )
        if estado:
            stmt = stmt.where(func.lower(Cliente.estado) == func.lower(estado))
        if fecha_desde:
            stmt = stmt.where(Cliente.fecha_creacion >= datetime.combine(fecha_desde, time.min))
        if fecha_hasta:
            stmt = stmt.where(Cliente.fecha_creacion <= datetime.combine(fecha_hasta, time.max))

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_cliente_by_id(self, id_cliente: int) -> Optional[Cliente]:
        stmt = (
            select(Cliente)
            .options(
                selectinload(Cliente.tipo_cliente),
                selectinload(Cliente.municipio).selectinload(Municipio.departamento),
                selectinload(Cliente.contactos),
            )
            .where(Cliente.id_cliente == id_cliente)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
