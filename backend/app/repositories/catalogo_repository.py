"""
Repositorio para módulos de catálogos CRUD (Fase 2).
Cubre: TipoCliente, Cliente, Sucursal, AreaBodega, Subcategoria,
       UnidadMedida, MotivoMerma, MetodoPago, Proveedor,
       DepartamentoGeografico, Municipio, Permiso/RolPermiso,
       BitacoraAuditoria (R), HistorialPrecio (R).
Reglas: sin commit(), usa selectinload, select() async.
"""
from typing import Optional, List
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.db.models import (
    TipoCliente, Cliente, ClienteContacto,
    Sucursal, AreaBodega,
    Subcategoria, UnidadMedida, Producto, InventarioSucursal,
    MotivoMerma, DetalleMerma, MetodoPago,
    Proveedor, OrdenCompra,
    DepartamentoGeografico, Municipio,
    Permiso, RolPermiso,
    BitacoraAuditoria, HistorialPrecio,
    Venta, PagoVenta,
)


# ---------------------------------------------------------------------------
# TipoCliente
# ---------------------------------------------------------------------------

class TipoClienteRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, id_tipo: int) -> Optional[TipoCliente]:
        res = await self.db.execute(select(TipoCliente).where(TipoCliente.id_tipo_cliente == id_tipo))
        return res.scalar_one_or_none()

    async def list_all(self, only_active: bool = False) -> List[TipoCliente]:
        stmt = select(TipoCliente)
        if only_active:
            stmt = stmt.where(TipoCliente.estado == "Activo")
        stmt = stmt.order_by(TipoCliente.nombre)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def count(self, only_active: bool = False) -> int:
        stmt = select(func.count()).select_from(TipoCliente)
        if only_active:
            stmt = stmt.where(TipoCliente.estado == "Activo")
        res = await self.db.execute(stmt)
        return res.scalar_one()

    async def create(self, obj: TipoCliente) -> TipoCliente:
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def update(self, obj: TipoCliente) -> TipoCliente:
        await self.db.flush()
        await self.db.refresh(obj)
        return obj


# ---------------------------------------------------------------------------
# ClienteContacto
# ---------------------------------------------------------------------------

class ClienteContactoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, obj: ClienteContacto) -> ClienteContacto:
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def delete_by_cliente(self, id_cliente: int) -> None:
        stmt = select(ClienteContacto).where(ClienteContacto.id_cliente == id_cliente)
        res = await self.db.execute(stmt)
        for c in res.scalars().all():
            await self.db.delete(c)
        await self.db.flush()


# ---------------------------------------------------------------------------
# Cliente
# ---------------------------------------------------------------------------

_CLIENTE_LOADS = (
    selectinload(Cliente.tipo_cliente),
    selectinload(Cliente.municipio),
    selectinload(Cliente.contactos),
)


class ClienteRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, id_cliente: int) -> Optional[Cliente]:
        res = await self.db.execute(
            select(Cliente).options(*_CLIENTE_LOADS).where(Cliente.id_cliente == id_cliente)
        )
        return res.scalar_one_or_none()

    async def get_by_nit(self, nit: str) -> Optional[Cliente]:
        res = await self.db.execute(
            select(Cliente).options(*_CLIENTE_LOADS).where(Cliente.nit == nit)
        )
        return res.scalar_one_or_none()

    def _build_filters(
        self,
        nombre: Optional[str] = None,
        nit: Optional[str] = None,
        id_tipo_cliente: Optional[int] = None,
        is_active: Optional[bool] = None,
    ):
        conds = []
        if nombre:
            conds.append(Cliente.nombre_comercial.ilike(f"%{nombre}%"))
        if nit:
            conds.append(Cliente.nit.ilike(f"%{nit}%"))
        if id_tipo_cliente is not None:
            conds.append(Cliente.id_tipo_cliente == id_tipo_cliente)
        if is_active is not None:
            estado = "Activo" if is_active else "Inactivo"
            conds.append(Cliente.estado == estado)
        return conds

    async def search(
        self,
        nombre: Optional[str] = None,
        nit: Optional[str] = None,
        id_tipo_cliente: Optional[int] = None,
        is_active: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Cliente]:
        conds = self._build_filters(nombre, nit, id_tipo_cliente, is_active)
        stmt = select(Cliente).options(*_CLIENTE_LOADS)
        if conds:
            stmt = stmt.where(and_(*conds))
        stmt = stmt.order_by(Cliente.nombre_comercial).limit(limit).offset(offset)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def count_search(
        self,
        nombre: Optional[str] = None,
        nit: Optional[str] = None,
        id_tipo_cliente: Optional[int] = None,
        is_active: Optional[bool] = None,
    ) -> int:
        conds = self._build_filters(nombre, nit, id_tipo_cliente, is_active)
        stmt = select(func.count()).select_from(Cliente)
        if conds:
            stmt = stmt.where(and_(*conds))
        res = await self.db.execute(stmt)
        return res.scalar_one()

    async def create(self, obj: Cliente) -> Cliente:
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def update(self, obj: Cliente) -> Cliente:
        await self.db.flush()
        await self.db.refresh(obj)
        return obj


# ---------------------------------------------------------------------------
# Sucursal
# ---------------------------------------------------------------------------

class SucursalRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, id_sucursal: int) -> Optional[Sucursal]:
        stmt = select(Sucursal).options(selectinload(Sucursal.areas)).where(Sucursal.id_sucursal == id_sucursal)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_nombre(self, nombre: str) -> Optional[Sucursal]:
        stmt = select(Sucursal).where(func.lower(Sucursal.nombre) == nombre.strip().lower())
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def search(
        self,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        fecha_desde = None,
        fecha_hasta = None,
        sort_by: Optional[str] = "nombre",
        sort_order: Optional[str] = "asc",
        limit: int = 50,
        offset: int = 0,
    ) -> List[Sucursal]:
        conds = []
        if search:
            s = f"%{search.strip()}%"
            conds.append(or_(Sucursal.nombre.ilike(s), Sucursal.direccion.ilike(s), Sucursal.telefono.ilike(s)))
        if is_active is not None:
            conds.append(Sucursal.estado == ("Activo" if is_active else "Inactivo"))
        if fecha_desde:
            conds.append(Sucursal.fecha_creacion >= fecha_desde)
        if fecha_hasta:
            conds.append(Sucursal.fecha_creacion <= fecha_hasta)

        stmt = select(Sucursal).options(selectinload(Sucursal.areas))
        if conds:
            stmt = stmt.where(and_(*conds))

        # Ordenamiento dinámico seguro
        col_map = {
            "id_sucursal": Sucursal.id_sucursal,
            "nombre": Sucursal.nombre,
            "direccion": Sucursal.direccion,
            "estado": Sucursal.estado,
            "fecha_creacion": Sucursal.fecha_creacion,
        }
        order_col = col_map.get(sort_by, Sucursal.nombre)
        stmt = stmt.order_by(order_col.desc() if sort_order == "desc" else order_col.asc())
        stmt = stmt.limit(limit).offset(offset)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def count(
        self,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        fecha_desde = None,
        fecha_hasta = None,
    ) -> int:
        conds = []
        if search:
            s = f"%{search.strip()}%"
            conds.append(or_(Sucursal.nombre.ilike(s), Sucursal.direccion.ilike(s), Sucursal.telefono.ilike(s)))
        if is_active is not None:
            conds.append(Sucursal.estado == ("Activo" if is_active else "Inactivo"))
        if fecha_desde:
            conds.append(Sucursal.fecha_creacion >= fecha_desde)
        if fecha_hasta:
            conds.append(Sucursal.fecha_creacion <= fecha_hasta)

        stmt = select(func.count()).select_from(Sucursal)
        if conds:
            stmt = stmt.where(and_(*conds))
        res = await self.db.execute(stmt)
        return res.scalar_one()

    async def count_areas_activas(self, id_sucursal: int) -> int:
        """Cuenta áreas de bodega activas que dependen de la sucursal."""
        stmt = select(func.count()).select_from(AreaBodega).where(
            AreaBodega.id_sucursal == id_sucursal,
            AreaBodega.estado == "Activo",
        )
        res = await self.db.execute(stmt)
        return res.scalar_one()

    async def count_inventario_activo(self, id_sucursal: int) -> int:
        """Cuenta registros de inventario activos (stock > 0) asociados a la sucursal."""
        stmt = select(func.count()).select_from(InventarioSucursal).where(
            InventarioSucursal.id_sucursal == id_sucursal,
            InventarioSucursal.stock_actual > 0,
        )
        res = await self.db.execute(stmt)
        return res.scalar_one()

    async def create(self, obj: Sucursal) -> Sucursal:
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def update(self, obj: Sucursal) -> Sucursal:
        await self.db.flush()
        await self.db.refresh(obj)
        return obj


# ---------------------------------------------------------------------------
# AreaBodega
# ---------------------------------------------------------------------------

class AreaBodegaRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, id_area: int) -> Optional[AreaBodega]:
        stmt = select(AreaBodega).options(selectinload(AreaBodega.sucursal)).where(AreaBodega.id_area == id_area)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_nombre_sucursal(self, id_sucursal: int, nombre_area: str) -> Optional[AreaBodega]:
        stmt = select(AreaBodega).where(
            and_(
                AreaBodega.id_sucursal == id_sucursal,
                func.lower(AreaBodega.nombre_area) == nombre_area.strip().lower(),
            )
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def search(
        self,
        search: Optional[str] = None,
        id_sucursal: Optional[int] = None,
        is_active: Optional[bool] = None,
        sort_by: Optional[str] = "nombre_area",
        sort_order: Optional[str] = "asc",
        limit: int = 50,
        offset: int = 0,
    ) -> List[AreaBodega]:
        conds = []
        if search:
            conds.append(AreaBodega.nombre_area.ilike(f"%{search.strip()}%"))
        if id_sucursal is not None:
            conds.append(AreaBodega.id_sucursal == id_sucursal)
        if is_active is not None:
            conds.append(AreaBodega.estado == ("Activo" if is_active else "Inactivo"))

        stmt = select(AreaBodega).options(selectinload(AreaBodega.sucursal))
        if conds:
            stmt = stmt.where(and_(*conds))

        col_map = {
            "id_area": AreaBodega.id_area,
            "nombre_area": AreaBodega.nombre_area,
            "estado": AreaBodega.estado,
        }
        order_col = col_map.get(sort_by, AreaBodega.nombre_area)
        stmt = stmt.order_by(order_col.desc() if sort_order == "desc" else order_col.asc())
        stmt = stmt.limit(limit).offset(offset)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def count(
        self,
        search: Optional[str] = None,
        id_sucursal: Optional[int] = None,
        is_active: Optional[bool] = None,
    ) -> int:
        conds = []
        if search:
            conds.append(AreaBodega.nombre_area.ilike(f"%{search.strip()}%"))
        if id_sucursal is not None:
            conds.append(AreaBodega.id_sucursal == id_sucursal)
        if is_active is not None:
            conds.append(AreaBodega.estado == ("Activo" if is_active else "Inactivo"))

        stmt = select(func.count()).select_from(AreaBodega)
        if conds:
            stmt = stmt.where(and_(*conds))
        res = await self.db.execute(stmt)
        return res.scalar_one()

    async def count_inventario_activo(self, id_area: int) -> int:
        """Cuenta registros de inventario activos (stock > 0) asociados al área de bodega."""
        stmt = select(func.count()).select_from(InventarioSucursal).where(
            InventarioSucursal.id_area == id_area,
            InventarioSucursal.stock_actual > 0,
        )
        res = await self.db.execute(stmt)
        return res.scalar_one()

    async def list_by_sucursal(self, id_sucursal: Optional[int] = None, only_active: bool = False) -> List[AreaBodega]:
        stmt = select(AreaBodega).options(selectinload(AreaBodega.sucursal))
        if id_sucursal is not None:
            stmt = stmt.where(AreaBodega.id_sucursal == id_sucursal)
        if only_active:
            stmt = stmt.where(AreaBodega.estado == "Activo")
        stmt = stmt.order_by(AreaBodega.nombre_area)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def create(self, obj: AreaBodega) -> AreaBodega:
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def update(self, obj: AreaBodega) -> AreaBodega:
        await self.db.flush()
        await self.db.refresh(obj)
        return obj


# ---------------------------------------------------------------------------
# Subcategoria
# ---------------------------------------------------------------------------

class SubcategoriaRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, id_sub: int) -> Optional[Subcategoria]:
        stmt = select(Subcategoria).options(selectinload(Subcategoria.categoria)).where(Subcategoria.id_subcategoria == id_sub)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_cat_nombre(self, id_cat: int, nombre: str) -> Optional[Subcategoria]:
        stmt = select(Subcategoria).where(
            and_(
                Subcategoria.id_categoria == id_cat,
                func.lower(Subcategoria.nombre) == nombre.strip().lower(),
            )
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def search(
        self,
        search: Optional[str] = None,
        id_categoria: Optional[int] = None,
        is_active: Optional[bool] = None,
        sort_by: Optional[str] = "nombre",
        sort_order: Optional[str] = "asc",
        limit: int = 50,
        offset: int = 0,
    ) -> List[Subcategoria]:
        conds = []
        if search:
            conds.append(Subcategoria.nombre.ilike(f"%{search.strip()}%"))
        if id_categoria is not None:
            conds.append(Subcategoria.id_categoria == id_categoria)
        if is_active is not None:
            conds.append(Subcategoria.estado == ("Activo" if is_active else "Inactivo"))

        stmt = select(Subcategoria).options(selectinload(Subcategoria.categoria))
        if conds:
            stmt = stmt.where(and_(*conds))

        col_map = {
            "id_subcategoria": Subcategoria.id_subcategoria,
            "nombre": Subcategoria.nombre,
            "estado": Subcategoria.estado,
        }
        order_col = col_map.get(sort_by, Subcategoria.nombre)
        stmt = stmt.order_by(order_col.desc() if sort_order == "desc" else order_col.asc())
        stmt = stmt.limit(limit).offset(offset)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def count(
        self,
        search: Optional[str] = None,
        id_categoria: Optional[int] = None,
        is_active: Optional[bool] = None,
    ) -> int:
        conds = []
        if search:
            conds.append(Subcategoria.nombre.ilike(f"%{search.strip()}%"))
        if id_categoria is not None:
            conds.append(Subcategoria.id_categoria == id_categoria)
        if is_active is not None:
            conds.append(Subcategoria.estado == ("Activo" if is_active else "Inactivo"))

        stmt = select(func.count()).select_from(Subcategoria)
        if conds:
            stmt = stmt.where(and_(*conds))
        res = await self.db.execute(stmt)
        return res.scalar_one()

    async def count_productos_activos(self, id_sub: int) -> int:
        """Cuenta productos activos que dependen de la subcategoría."""
        stmt = select(func.count()).select_from(Producto).where(
            Producto.id_subcategoria == id_sub,
            Producto.estado == "Activo",
        )
        res = await self.db.execute(stmt)
        return res.scalar_one()

    async def list_all(self, id_categoria: Optional[int] = None, only_active: bool = False) -> List[Subcategoria]:
        stmt = select(Subcategoria).options(selectinload(Subcategoria.categoria))
        if id_categoria is not None:
            stmt = stmt.where(Subcategoria.id_categoria == id_categoria)
        if only_active:
            stmt = stmt.where(Subcategoria.estado == "Activo")
        stmt = stmt.order_by(Subcategoria.nombre)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def create(self, obj: Subcategoria) -> Subcategoria:
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def update(self, obj: Subcategoria) -> Subcategoria:
        await self.db.flush()
        await self.db.refresh(obj)
        return obj


# ---------------------------------------------------------------------------
# UnidadMedida
# ---------------------------------------------------------------------------

class UnidadMedidaRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, id_unidad: int) -> Optional[UnidadMedida]:
        res = await self.db.execute(select(UnidadMedida).where(UnidadMedida.id_unidad == id_unidad))
        return res.scalar_one_or_none()

    async def get_by_codigo(self, codigo: str) -> Optional[UnidadMedida]:
        res = await self.db.execute(
            select(UnidadMedida).where(func.upper(UnidadMedida.codigo) == codigo.strip().upper())
        )
        return res.scalar_one_or_none()

    async def search(
        self,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        sort_by: Optional[str] = "descripcion",
        sort_order: Optional[str] = "asc",
        limit: int = 50,
        offset: int = 0,
    ) -> List[UnidadMedida]:
        conds = []
        if search:
            s = f"%{search.strip()}%"
            conds.append(or_(UnidadMedida.codigo.ilike(s), UnidadMedida.descripcion.ilike(s)))
        if is_active is not None:
            conds.append(UnidadMedida.estado == ("Activo" if is_active else "Inactivo"))

        stmt = select(UnidadMedida)
        if conds:
            stmt = stmt.where(and_(*conds))

        col_map = {
            "id_unidad": UnidadMedida.id_unidad,
            "codigo": UnidadMedida.codigo,
            "descripcion": UnidadMedida.descripcion,
            "estado": UnidadMedida.estado,
        }
        order_col = col_map.get(sort_by, UnidadMedida.descripcion)
        stmt = stmt.order_by(order_col.desc() if sort_order == "desc" else order_col.asc())
        stmt = stmt.limit(limit).offset(offset)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def count(
        self,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> int:
        conds = []
        if search:
            s = f"%{search.strip()}%"
            conds.append(or_(UnidadMedida.codigo.ilike(s), UnidadMedida.descripcion.ilike(s)))
        if is_active is not None:
            conds.append(UnidadMedida.estado == ("Activo" if is_active else "Inactivo"))

        stmt = select(func.count()).select_from(UnidadMedida)
        if conds:
            stmt = stmt.where(and_(*conds))
        res = await self.db.execute(stmt)
        return res.scalar_one()

    async def count_productos_activos(self, id_unidad: int) -> int:
        """Cuenta productos activos que dependen de la unidad de medida."""
        stmt = select(func.count()).select_from(Producto).where(
            Producto.id_unidad == id_unidad,
            Producto.estado == "Activo",
        )
        res = await self.db.execute(stmt)
        return res.scalar_one()

    async def list_all(self, only_active: bool = False) -> List[UnidadMedida]:
        stmt = select(UnidadMedida)
        if only_active:
            stmt = stmt.where(UnidadMedida.estado == "Activo")
        stmt = stmt.order_by(UnidadMedida.descripcion)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def create(self, obj: UnidadMedida) -> UnidadMedida:
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def update(self, obj: UnidadMedida) -> UnidadMedida:
        await self.db.flush()
        await self.db.refresh(obj)
        return obj


# ---------------------------------------------------------------------------
# MotivoMerma
# ---------------------------------------------------------------------------

class MotivoMermaRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, id_motivo: int) -> Optional[MotivoMerma]:
        res = await self.db.execute(select(MotivoMerma).where(MotivoMerma.id_motivo == id_motivo))
        return res.scalar_one_or_none()

    async def get_by_descripcion(self, descripcion: str) -> Optional[MotivoMerma]:
        res = await self.db.execute(
            select(MotivoMerma).where(func.lower(MotivoMerma.descripcion) == descripcion.strip().lower())
        )
        return res.scalar_one_or_none()

    async def list_all(self, only_active: bool = False) -> List[MotivoMerma]:
        stmt = select(MotivoMerma)
        if only_active:
            stmt = stmt.where(MotivoMerma.estado == "Activo")
        stmt = stmt.order_by(MotivoMerma.descripcion)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def search(
        self,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        sort_by: Optional[str] = "descripcion",
        sort_order: Optional[str] = "asc",
        limit: int = 50,
        offset: int = 0,
    ) -> List[MotivoMerma]:
        conds = []
        if search:
            conds.append(MotivoMerma.descripcion.ilike(f"%{search.strip()}%"))
        if is_active is not None:
            conds.append(MotivoMerma.estado == ("Activo" if is_active else "Inactivo"))

        stmt = select(MotivoMerma)
        if conds:
            stmt = stmt.where(and_(*conds))
        col_map = {
            "id_motivo": MotivoMerma.id_motivo,
            "descripcion": MotivoMerma.descripcion,
            "estado": MotivoMerma.estado,
        }
        order_col = col_map.get(sort_by, MotivoMerma.descripcion)
        stmt = stmt.order_by(order_col.desc() if sort_order == "desc" else order_col.asc())
        stmt = stmt.limit(limit).offset(offset)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def count_search(
        self,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> int:
        conds = []
        if search:
            conds.append(MotivoMerma.descripcion.ilike(f"%{search.strip()}%"))
        if is_active is not None:
            conds.append(MotivoMerma.estado == ("Activo" if is_active else "Inactivo"))
        stmt = select(func.count()).select_from(MotivoMerma)
        if conds:
            stmt = stmt.where(and_(*conds))
        res = await self.db.execute(stmt)
        return res.scalar_one()

    async def count(self, only_active: bool = False) -> int:
        stmt = select(func.count()).select_from(MotivoMerma)
        if only_active:
            stmt = stmt.where(MotivoMerma.estado == "Activo")
        res = await self.db.execute(stmt)
        return res.scalar_one()

    async def count_registros_asociados(self, id_motivo: int) -> int:
        """Cuenta detalles de merma que dependen del motivo (para desactivación segura)."""
        stmt = select(func.count()).select_from(DetalleMerma).where(DetalleMerma.id_motivo == id_motivo)
        res = await self.db.execute(stmt)
        return res.scalar_one()

    async def create(self, obj: MotivoMerma) -> MotivoMerma:
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def update(self, obj: MotivoMerma) -> MotivoMerma:
        await self.db.flush()
        await self.db.refresh(obj)
        return obj


# ---------------------------------------------------------------------------
# MetodoPago
# ---------------------------------------------------------------------------

class MetodoPagoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, id_metodo: int) -> Optional[MetodoPago]:
        res = await self.db.execute(select(MetodoPago).where(MetodoPago.id_metodo_pago == id_metodo))
        return res.scalar_one_or_none()

    async def get_by_nombre(self, nombre: str) -> Optional[MetodoPago]:
        res = await self.db.execute(
            select(MetodoPago).where(func.lower(MetodoPago.nombre) == nombre.strip().lower())
        )
        return res.scalar_one_or_none()

    async def list_all(self, only_active: bool = False) -> List[MetodoPago]:
        stmt = select(MetodoPago)
        if only_active:
            stmt = stmt.where(MetodoPago.estado == "Activo")
        stmt = stmt.order_by(MetodoPago.nombre)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def search(
        self,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        sort_by: Optional[str] = "nombre",
        sort_order: Optional[str] = "asc",
        limit: int = 50,
        offset: int = 0,
    ) -> List[MetodoPago]:
        conds = []
        if search:
            conds.append(MetodoPago.nombre.ilike(f"%{search.strip()}%"))
        if is_active is not None:
            conds.append(MetodoPago.estado == ("Activo" if is_active else "Inactivo"))

        stmt = select(MetodoPago)
        if conds:
            stmt = stmt.where(and_(*conds))
        col_map = {
            "id_metodo_pago": MetodoPago.id_metodo_pago,
            "nombre": MetodoPago.nombre,
            "estado": MetodoPago.estado,
        }
        order_col = col_map.get(sort_by, MetodoPago.nombre)
        stmt = stmt.order_by(order_col.desc() if sort_order == "desc" else order_col.asc())
        stmt = stmt.limit(limit).offset(offset)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def count_search(
        self,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> int:
        conds = []
        if search:
            conds.append(MetodoPago.nombre.ilike(f"%{search.strip()}%"))
        if is_active is not None:
            conds.append(MetodoPago.estado == ("Activo" if is_active else "Inactivo"))
        stmt = select(func.count()).select_from(MetodoPago)
        if conds:
            stmt = stmt.where(and_(*conds))
        res = await self.db.execute(stmt)
        return res.scalar_one()

    async def count(self, only_active: bool = False) -> int:
        stmt = select(func.count()).select_from(MetodoPago)
        if only_active:
            stmt = stmt.where(MetodoPago.estado == "Activo")
        res = await self.db.execute(stmt)
        return res.scalar_one()

    async def count_pagos_ventas_completadas(self, id_metodo: int) -> int:
        """Cuenta pagos de ventas completadas que dependen del método de pago."""
        stmt = (
            select(func.count())
            .select_from(PagoVenta)
            .join(Venta, Venta.id_venta == PagoVenta.id_venta)
            .where(
                PagoVenta.id_metodo_pago == id_metodo,
                Venta.estado == "Completada",
            )
        )
        res = await self.db.execute(stmt)
        return res.scalar_one()

    async def create(self, obj: MetodoPago) -> MetodoPago:
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def update(self, obj: MetodoPago) -> MetodoPago:
        await self.db.flush()
        await self.db.refresh(obj)
        return obj


# ---------------------------------------------------------------------------
# Proveedor
# ---------------------------------------------------------------------------

class ProveedorRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, id_proveedor: int) -> Optional[Proveedor]:
        res = await self.db.execute(select(Proveedor).where(Proveedor.id_proveedor == id_proveedor))
        return res.scalar_one_or_none()

    async def get_by_distribuidora(self, distribuidora: str) -> Optional[Proveedor]:
        res = await self.db.execute(
            select(Proveedor).where(func.lower(Proveedor.distribuidora) == distribuidora.strip().lower())
        )
        return res.scalar_one_or_none()

    def _build_filters(
        self,
        search: Optional[str] = None,
        nombre: Optional[str] = None,
        distribuidora: Optional[str] = None,
        is_active: Optional[bool] = None,
        fecha_desde = None,
        fecha_hasta = None,
    ):
        conds = []
        if search:
            s = f"%{search.strip()}%"
            conds.append(or_(Proveedor.nombre_contacto.ilike(s), Proveedor.distribuidora.ilike(s)))
        if nombre:
            conds.append(Proveedor.nombre_contacto.ilike(f"%{nombre}%"))
        if distribuidora:
            conds.append(Proveedor.distribuidora.ilike(f"%{distribuidora}%"))
        if is_active is not None:
            conds.append(Proveedor.estado == ("Activo" if is_active else "Inactivo"))
        if fecha_desde:
            conds.append(Proveedor.fecha_creacion >= fecha_desde)
        if fecha_hasta:
            conds.append(Proveedor.fecha_creacion <= fecha_hasta)
        return conds

    async def search(
        self,
        search: Optional[str] = None,
        nombre: Optional[str] = None,
        distribuidora: Optional[str] = None,
        is_active: Optional[bool] = None,
        fecha_desde = None,
        fecha_hasta = None,
        sort_by: Optional[str] = "distribuidora",
        sort_order: Optional[str] = "asc",
        limit: int = 50,
        offset: int = 0,
    ) -> List[Proveedor]:
        conds = self._build_filters(search, nombre, distribuidora, is_active, fecha_desde, fecha_hasta)
        stmt = select(Proveedor)
        if conds:
            stmt = stmt.where(and_(*conds))
        col_map = {
            "id_proveedor": Proveedor.id_proveedor,
            "nombre_contacto": Proveedor.nombre_contacto,
            "distribuidora": Proveedor.distribuidora,
            "estado": Proveedor.estado,
            "fecha_creacion": Proveedor.fecha_creacion,
        }
        order_col = col_map.get(sort_by, Proveedor.distribuidora)
        stmt = stmt.order_by(order_col.desc() if sort_order == "desc" else order_col.asc())
        stmt = stmt.limit(limit).offset(offset)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def count_search(
        self,
        search: Optional[str] = None,
        nombre: Optional[str] = None,
        distribuidora: Optional[str] = None,
        is_active: Optional[bool] = None,
        fecha_desde = None,
        fecha_hasta = None,
    ) -> int:
        conds = self._build_filters(search, nombre, distribuidora, is_active, fecha_desde, fecha_hasta)
        stmt = select(func.count()).select_from(Proveedor)
        if conds:
            stmt = stmt.where(and_(*conds))
        res = await self.db.execute(stmt)
        return res.scalar_one()

    async def count_ordenes_activas(self, id_proveedor: int) -> int:
        """Cuenta órdenes de compra abiertas / no finalizadas (Emitida, Recibida Parcialmente, Pendiente, En Proceso, etc.) que dependen del proveedor."""
        stmt = select(func.count()).select_from(OrdenCompra).where(
            OrdenCompra.id_proveedor == id_proveedor,
            OrdenCompra.estado.notin_(["Recibida", "Cancelada", "Anulada"]),
        )
        res = await self.db.execute(stmt)
        return res.scalar_one()

    async def create(self, obj: Proveedor) -> Proveedor:
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def update(self, obj: Proveedor) -> Proveedor:
        await self.db.flush()
        await self.db.refresh(obj)
        return obj


# ---------------------------------------------------------------------------
# DepartamentoGeografico
# ---------------------------------------------------------------------------

class DepartamentoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, id_dep: int) -> Optional[DepartamentoGeografico]:
        res = await self.db.execute(
            select(DepartamentoGeografico)
            .options(selectinload(DepartamentoGeografico.municipios))
            .where(DepartamentoGeografico.id_departamento == id_dep)
        )
        return res.scalar_one_or_none()

    async def get_by_nombre(self, nombre: str) -> Optional[DepartamentoGeografico]:
        res = await self.db.execute(
            select(DepartamentoGeografico).where(func.lower(DepartamentoGeografico.nombre) == nombre.strip().lower())
        )
        return res.scalar_one_or_none()

    async def list_all(self, only_active: bool = False) -> List[DepartamentoGeografico]:
        stmt = select(DepartamentoGeografico).options(selectinload(DepartamentoGeografico.municipios))
        if only_active:
            stmt = stmt.where(DepartamentoGeografico.estado == "Activo")
        stmt = stmt.order_by(DepartamentoGeografico.nombre)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def search(
        self,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        sort_by: Optional[str] = "nombre",
        sort_order: Optional[str] = "asc",
        limit: int = 50,
        offset: int = 0,
    ) -> List[DepartamentoGeografico]:
        conds = []
        if search:
            conds.append(DepartamentoGeografico.nombre.ilike(f"%{search.strip()}%"))
        if is_active is not None:
            conds.append(DepartamentoGeografico.estado == ("Activo" if is_active else "Inactivo"))

        stmt = select(DepartamentoGeografico).options(selectinload(DepartamentoGeografico.municipios))
        if conds:
            stmt = stmt.where(and_(*conds))
        col_map = {
            "id_departamento": DepartamentoGeografico.id_departamento,
            "nombre": DepartamentoGeografico.nombre,
            "estado": DepartamentoGeografico.estado,
        }
        order_col = col_map.get(sort_by, DepartamentoGeografico.nombre)
        stmt = stmt.order_by(order_col.desc() if sort_order == "desc" else order_col.asc())
        stmt = stmt.limit(limit).offset(offset)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def count_search(
        self,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> int:
        conds = []
        if search:
            conds.append(DepartamentoGeografico.nombre.ilike(f"%{search.strip()}%"))
        if is_active is not None:
            conds.append(DepartamentoGeografico.estado == ("Activo" if is_active else "Inactivo"))
        stmt = select(func.count()).select_from(DepartamentoGeografico)
        if conds:
            stmt = stmt.where(and_(*conds))
        res = await self.db.execute(stmt)
        return res.scalar_one()

    async def count_municipios_activos(self, id_dep: int) -> int:
        """Cuenta municipios activos que dependen del departamento."""
        stmt = select(func.count()).select_from(Municipio).where(
            Municipio.id_departamento == id_dep,
            Municipio.estado == "Activo",
        )
        res = await self.db.execute(stmt)
        return res.scalar_one()

    async def create(self, obj: DepartamentoGeografico) -> DepartamentoGeografico:
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def update(self, obj: DepartamentoGeografico) -> DepartamentoGeografico:
        await self.db.flush()
        await self.db.refresh(obj)
        return obj


# ---------------------------------------------------------------------------
# Municipio
# ---------------------------------------------------------------------------

class MunicipioRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, id_municipio: int) -> Optional[Municipio]:
        res = await self.db.execute(
            select(Municipio).options(selectinload(Municipio.departamento)).where(Municipio.id_municipio == id_municipio)
        )
        return res.scalar_one_or_none()

    async def get_by_depto_nombre(self, id_dep: int, nombre: str) -> Optional[Municipio]:
        res = await self.db.execute(
            select(Municipio).where(
                and_(
                    Municipio.id_departamento == id_dep,
                    func.lower(Municipio.nombre) == nombre.strip().lower(),
                )
            )
        )
        return res.scalar_one_or_none()

    async def list_by_departamento(
        self, id_departamento: Optional[int] = None, only_active: bool = False
    ) -> List[Municipio]:
        stmt = select(Municipio)
        if id_departamento is not None:
            stmt = stmt.where(Municipio.id_departamento == id_departamento)
        if only_active:
            stmt = stmt.where(Municipio.estado == "Activo")
        stmt = stmt.order_by(Municipio.nombre)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def search(
        self,
        search: Optional[str] = None,
        id_departamento: Optional[int] = None,
        is_active: Optional[bool] = None,
        sort_by: Optional[str] = "nombre",
        sort_order: Optional[str] = "asc",
        limit: int = 50,
        offset: int = 0,
    ) -> List[Municipio]:
        conds = []
        if search:
            conds.append(Municipio.nombre.ilike(f"%{search.strip()}%"))
        if id_departamento is not None:
            conds.append(Municipio.id_departamento == id_departamento)
        if is_active is not None:
            conds.append(Municipio.estado == ("Activo" if is_active else "Inactivo"))

        stmt = select(Municipio).options(selectinload(Municipio.departamento))
        if conds:
            stmt = stmt.where(and_(*conds))
        col_map = {
            "id_municipio": Municipio.id_municipio,
            "nombre": Municipio.nombre,
            "id_departamento": Municipio.id_departamento,
            "estado": Municipio.estado,
        }
        order_col = col_map.get(sort_by, Municipio.nombre)
        stmt = stmt.order_by(order_col.desc() if sort_order == "desc" else order_col.asc())
        stmt = stmt.limit(limit).offset(offset)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def count_search(
        self,
        search: Optional[str] = None,
        id_departamento: Optional[int] = None,
        is_active: Optional[bool] = None,
    ) -> int:
        conds = []
        if search:
            conds.append(Municipio.nombre.ilike(f"%{search.strip()}%"))
        if id_departamento is not None:
            conds.append(Municipio.id_departamento == id_departamento)
        if is_active is not None:
            conds.append(Municipio.estado == ("Activo" if is_active else "Inactivo"))
        stmt = select(func.count()).select_from(Municipio)
        if conds:
            stmt = stmt.where(and_(*conds))
        res = await self.db.execute(stmt)
        return res.scalar_one()

    async def count_clientes_activos(self, id_municipio: int) -> int:
        """Cuenta clientes activos que dependen del municipio."""
        stmt = select(func.count()).select_from(Cliente).where(
            Cliente.id_municipio == id_municipio,
            Cliente.estado == "Activo",
        )
        res = await self.db.execute(stmt)
        return res.scalar_one()

    async def count(self, id_departamento: Optional[int] = None, only_active: bool = False) -> int:
        stmt = select(func.count()).select_from(Municipio)
        if id_departamento is not None:
            stmt = stmt.where(Municipio.id_departamento == id_departamento)
        if only_active:
            stmt = stmt.where(Municipio.estado == "Activo")
        res = await self.db.execute(stmt)
        return res.scalar_one()

    async def create(self, obj: Municipio) -> Municipio:
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def update(self, obj: Municipio) -> Municipio:
        await self.db.flush()
        await self.db.refresh(obj)
        return obj


# ---------------------------------------------------------------------------
# Permiso
# ---------------------------------------------------------------------------

class PermisoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, id_permiso: int) -> Optional[Permiso]:
        res = await self.db.execute(select(Permiso).where(Permiso.id_permiso == id_permiso))
        return res.scalar_one_or_none()

    async def get_by_codigo(self, codigo: str) -> Optional[Permiso]:
        res = await self.db.execute(select(Permiso).where(Permiso.codigo == codigo))
        return res.scalar_one_or_none()

    async def list_all(self) -> List[Permiso]:
        res = await self.db.execute(select(Permiso).order_by(Permiso.modulo, Permiso.codigo))
        return list(res.scalars().all())

    async def create(self, obj: Permiso) -> Permiso:
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def update(self, obj: Permiso) -> Permiso:
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def list_by_rol(self, id_rol: int) -> List[Permiso]:
        stmt = (
            select(Permiso)
            .join(RolPermiso, RolPermiso.id_permiso == Permiso.id_permiso)
            .where(RolPermiso.id_rol == id_rol)
            .order_by(Permiso.modulo, Permiso.codigo)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_rol_permiso(self, id_rol: int, id_permiso: int) -> Optional[RolPermiso]:
        res = await self.db.execute(
            select(RolPermiso).where(
                and_(RolPermiso.id_rol == id_rol, RolPermiso.id_permiso == id_permiso)
            )
        )
        return res.scalar_one_or_none()

    async def assign_to_rol(self, obj: RolPermiso) -> RolPermiso:
        self.db.add(obj)
        await self.db.flush()
        return obj

    async def remove_from_rol(self, rp: RolPermiso) -> None:
        await self.db.delete(rp)
        await self.db.flush()


# ---------------------------------------------------------------------------
# BitacoraAuditoria (solo lectura)
# ---------------------------------------------------------------------------

class BitacoraRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _build_filters(self, id_usuario=None, tabla=None, accion=None, fecha_desde=None, fecha_hasta=None):
        conds = []
        if id_usuario is not None:
            conds.append(BitacoraAuditoria.id_usuario == id_usuario)
        if tabla:
            conds.append(BitacoraAuditoria.tabla_afectada.ilike(f"%{tabla}%"))
        if accion:
            conds.append(BitacoraAuditoria.accion == accion.upper())
        if fecha_desde:
            conds.append(BitacoraAuditoria.fecha_hora >= fecha_desde)
        if fecha_hasta:
            conds.append(BitacoraAuditoria.fecha_hora <= fecha_hasta)
        return conds

    async def search(self, id_usuario=None, tabla=None, accion=None, fecha_desde=None, fecha_hasta=None, limit=50, offset=0) -> List[BitacoraAuditoria]:
        conds = self._build_filters(id_usuario, tabla, accion, fecha_desde, fecha_hasta)
        stmt = select(BitacoraAuditoria)
        if conds:
            stmt = stmt.where(and_(*conds))
        stmt = stmt.order_by(BitacoraAuditoria.fecha_hora.desc()).limit(limit).offset(offset)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def count(self, id_usuario=None, tabla=None, accion=None, fecha_desde=None, fecha_hasta=None) -> int:
        conds = self._build_filters(id_usuario, tabla, accion, fecha_desde, fecha_hasta)
        stmt = select(func.count()).select_from(BitacoraAuditoria)
        if conds:
            stmt = stmt.where(and_(*conds))
        res = await self.db.execute(stmt)
        return res.scalar_one()


# ---------------------------------------------------------------------------
# HistorialPrecio (solo lectura)
# ---------------------------------------------------------------------------

class HistorialPrecioRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _build_filters(self, id_variante=None, id_usuario=None, fecha_desde=None, fecha_hasta=None):
        conds = []
        if id_variante is not None:
            conds.append(HistorialPrecio.id_variante == id_variante)
        if id_usuario is not None:
            conds.append(HistorialPrecio.id_usuario == id_usuario)
        if fecha_desde:
            conds.append(HistorialPrecio.fecha_modificacion >= fecha_desde)
        if fecha_hasta:
            conds.append(HistorialPrecio.fecha_modificacion <= fecha_hasta)
        return conds

    async def search(self, id_variante=None, id_usuario=None, fecha_desde=None, fecha_hasta=None, limit=50, offset=0) -> List[HistorialPrecio]:
        conds = self._build_filters(id_variante, id_usuario, fecha_desde, fecha_hasta)
        stmt = select(HistorialPrecio)
        if conds:
            stmt = stmt.where(and_(*conds))
        stmt = stmt.order_by(HistorialPrecio.fecha_modificacion.desc()).limit(limit).offset(offset)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def count(self, id_variante=None, id_usuario=None, fecha_desde=None, fecha_hasta=None) -> int:
        conds = self._build_filters(id_variante, id_usuario, fecha_desde, fecha_hasta)
        stmt = select(func.count()).select_from(HistorialPrecio)
        if conds:
            stmt = stmt.where(and_(*conds))
        res = await self.db.execute(stmt)
        return res.scalar_one()

