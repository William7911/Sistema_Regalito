from typing import Optional, List
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.db.models import Cliente, ClienteContacto, TipoCliente


_CLIENTE_LOADS = (
    selectinload(Cliente.tipo_cliente),
    selectinload(Cliente.municipio),
    selectinload(Cliente.contactos),
)


class ClienteRepositoryImpl:
    """Repositorio asíncrono para el modelo Cliente.
    No realiza commit: la persistencia atómica la controla UnitOfWork."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, id_cliente: int) -> Optional[Cliente]:
        stmt = select(Cliente).options(*_CLIENTE_LOADS).where(Cliente.id_cliente == id_cliente)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_nit(self, nit: str) -> Optional[Cliente]:
        # Busca por NIT (ignorando mayúsculas/minúsculas y espacios)
        stmt = (
            select(Cliente)
            .options(*_CLIENTE_LOADS)
            .where(func.upper(Cliente.nit) == nit.strip().upper())
            .order_by(Cliente.id_cliente.asc())
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    def _build_filters(
        self,
        nombre: Optional[str] = None,
        nit: Optional[str] = None,
        id_tipo_cliente: Optional[int] = None,
        is_active: Optional[bool] = None,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
    ):
        conditions = []
        if nombre:
            conditions.append(Cliente.nombre_comercial.ilike(f"%{nombre.strip()}%"))
        if nit:
            conditions.append(Cliente.nit.ilike(f"%{nit.strip()}%"))
        if id_tipo_cliente is not None:
            conditions.append(Cliente.id_tipo_cliente == id_tipo_cliente)
        if is_active is not None:
            estado = "Activo" if is_active else "Inactivo"
            conditions.append(Cliente.estado == estado)
        if fecha_desde:
            try:
                conditions.append(func.date(Cliente.fecha_creacion) >= fecha_desde.strip())
            except Exception:
                pass
        if fecha_hasta:
            try:
                conditions.append(func.date(Cliente.fecha_creacion) <= fecha_hasta.strip())
            except Exception:
                pass
        return conditions

    async def search(
        self,
        nombre: Optional[str] = None,
        nit: Optional[str] = None,
        id_tipo_cliente: Optional[int] = None,
        is_active: Optional[bool] = None,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
        sort_by: Optional[str] = "id_cliente",
        sort_order: Optional[str] = "asc",
        limit: int = 50,
        offset: int = 0,
    ) -> List[Cliente]:
        conditions = self._build_filters(
            nombre, nit, id_tipo_cliente, is_active, fecha_desde, fecha_hasta
        )
        stmt = select(Cliente).options(*_CLIENTE_LOADS)
        if conditions:
            stmt = stmt.where(and_(*conditions))

        col_map = {
            "id_cliente": Cliente.id_cliente,
            "nit": Cliente.nit,
            "nombre_comercial": Cliente.nombre_comercial,
            "fecha_creacion": Cliente.fecha_creacion,
            "estado": Cliente.estado,
        }
        order_col = col_map.get(sort_by, Cliente.id_cliente)
        if sort_order and sort_order.lower() == "desc":
            stmt = stmt.order_by(order_col.desc())
        else:
            stmt = stmt.order_by(order_col.asc())

        stmt = stmt.limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_search(
        self,
        nombre: Optional[str] = None,
        nit: Optional[str] = None,
        id_tipo_cliente: Optional[int] = None,
        is_active: Optional[bool] = None,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
    ) -> int:
        conditions = self._build_filters(
            nombre, nit, id_tipo_cliente, is_active, fecha_desde, fecha_hasta
        )
        stmt = select(func.count()).select_from(Cliente)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def create(self, cliente: Cliente) -> Cliente:
        self.db.add(cliente)
        await self.db.flush()
        await self.db.refresh(cliente)
        return cliente

    async def update(self, cliente: Cliente) -> Cliente:
        await self.db.flush()
        await self.db.refresh(cliente)
        return cliente

    async def delete_contactos(self, id_cliente: int) -> None:
        stmt = select(ClienteContacto).where(ClienteContacto.id_cliente == id_cliente)
        result = await self.db.execute(stmt)
        for c in result.scalars().all():
            await self.db.delete(c)
        await self.db.flush()

    async def add_contacto(self, contacto: ClienteContacto) -> ClienteContacto:
        self.db.add(contacto)
        await self.db.flush()
        return contacto


class TipoClienteRepositoryImpl:
    """Repositorio asíncrono para el catálogo TipoCliente."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, id_tipo: int) -> Optional[TipoCliente]:
        stmt = select(TipoCliente).where(TipoCliente.id_tipo_cliente == id_tipo)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_nombre(self, nombre: str) -> Optional[TipoCliente]:
        stmt = select(TipoCliente).where(func.upper(TipoCliente.nombre) == nombre.strip().upper())
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self, only_active: bool = False) -> List[TipoCliente]:
        stmt = select(TipoCliente)
        if only_active:
            stmt = stmt.where(TipoCliente.estado == "Activo")
        stmt = stmt.order_by(TipoCliente.id_tipo_cliente.asc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, tipo: TipoCliente) -> TipoCliente:
        self.db.add(tipo)
        await self.db.flush()
        await self.db.refresh(tipo)
        return tipo

    async def update(self, tipo: TipoCliente) -> TipoCliente:
        await self.db.flush()
        await self.db.refresh(tipo)
        return tipo

