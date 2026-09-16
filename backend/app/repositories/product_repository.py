from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import (
    Producto, VarianteProducto, InventarioSucursal,
    Subcategoria, UnidadMedida, Sucursal, AreaBodega, Categoria,
)
from app.interfaces.repositories import ProductRepository


class ProductRepositoryImpl(ProductRepository):
    """Acceso a datos async de Productos (estructura relacional Producto -> Variante -> Inventario).

    Los métodos `add_*` solo hacen `flush()` (no commit) para permitir la inserción
    anidada atómica; la decisión de persistir la toma el servicio vía `commit()/rollback()`.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    def _load_options(self):
        return [
            selectinload(Producto.subcategoria).selectinload(Subcategoria.categoria),
            selectinload(Producto.unidad),
            selectinload(Producto.variantes).selectinload(VarianteProducto.inventarios),
        ]

    async def get_producto_by_id(self, producto_id: int) -> Optional[Producto]:
        result = await self.db.execute(
            select(Producto)
            .options(*self._load_options())
            .where(Producto.id_producto == producto_id)
        )
        return result.scalar_one_or_none()

    async def get_variante_by_barcode(self, codigo_barras: str) -> Optional[VarianteProducto]:
        result = await self.db.execute(
            select(VarianteProducto).where(VarianteProducto.codigo_barras == codigo_barras)
        )
        return result.scalar_one_or_none()

    async def get_variante_by_id(self, variante_id: int) -> Optional[VarianteProducto]:
        result = await self.db.execute(
            select(VarianteProducto).where(VarianteProducto.id_variante == variante_id)
        )
        return result.scalar_one_or_none()

    async def get_inventario_by_id(self, inventario_id: int) -> Optional[InventarioSucursal]:
        result = await self.db.execute(
            select(InventarioSucursal).where(InventarioSucursal.id_inventario == inventario_id)
        )
        return result.scalar_one_or_none()

    def _build_filters(
        self,
        name: Optional[str],
        barcode: Optional[str],
        is_active: Optional[bool],
        subcategoria_id: Optional[int],
        created_from=None,
        created_to=None,
    ):
        conditions = []
        if name:
            conditions.append(Producto.nombre.ilike(f"%{name}%"))
        if is_active is not None:
            estado = "Activo" if is_active else "Inactivo"
            conditions.append(Producto.estado == estado)
        if subcategoria_id is not None:
            conditions.append(Producto.id_subcategoria == subcategoria_id)
        if created_from is not None:
            conditions.append(Producto.fecha_creacion >= created_from)
        if created_to is not None:
            conditions.append(Producto.fecha_creacion <= created_to)
        return conditions, barcode

    _SORTABLE = {
        "id_producto": Producto.id_producto,
        "nombre": Producto.nombre,
        "subcategoria": Subcategoria.nombre,
        "precio_detalle": VarianteProducto.precio_detalle,
        "stock": InventarioSucursal.stock_actual,
        "estado": Producto.estado,
        "fecha_creacion": Producto.fecha_creacion,
    }

    def _apply_order_joins(self, stmt, sort_by):
        """Agrega los joins necesarios para ordenar por columnas de tablas relacionadas."""
        if sort_by == "subcategoria":
            stmt = stmt.outerjoin(Subcategoria, Producto.id_subcategoria == Subcategoria.id_subcategoria)
        elif sort_by == "precio_detalle":
            stmt = stmt.outerjoin(VarianteProducto, Producto.id_producto == VarianteProducto.id_producto)
        elif sort_by == "stock":
            stmt = (
                stmt
                .outerjoin(VarianteProducto, Producto.id_producto == VarianteProducto.id_producto)
                .outerjoin(InventarioSucursal, VarianteProducto.id_variante == InventarioSucursal.id_variante)
            )
        return stmt

    async def search(
        self,
        name: Optional[str] = None,
        barcode: Optional[str] = None,
        is_active: Optional[bool] = None,
        subcategoria_id: Optional[int] = None,
        created_from=None,
        created_to=None,
        sort_by: Optional[str] = None,
        sort_dir: str = "asc",
        limit: int = 100,
        offset: int = 0,
    ) -> List[Producto]:
        conditions, barcode = self._build_filters(
            name, barcode, is_active, subcategoria_id, created_from, created_to
        )
        stmt = select(Producto).options(*self._load_options())
        if barcode:
            stmt = stmt.join(VarianteProducto).where(
                VarianteProducto.codigo_barras.ilike(f"%{barcode}%")
            )
        if conditions:
            stmt = stmt.where(*conditions)
        column = self._SORTABLE.get(sort_by, Producto.nombre)
        stmt = self._apply_order_joins(stmt, sort_by)
        if sort_dir == "desc":
            column = column.desc()
        stmt = stmt.order_by(column).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_search(
        self,
        name: Optional[str] = None,
        barcode: Optional[str] = None,
        is_active: Optional[bool] = None,
        subcategoria_id: Optional[int] = None,
        created_from=None,
        created_to=None,
    ) -> int:
        conditions, barcode = self._build_filters(
            name, barcode, is_active, subcategoria_id, created_from, created_to
        )
        stmt = select(func.count()).select_from(Producto)
        if barcode:
            stmt = stmt.join(VarianteProducto).where(
                VarianteProducto.codigo_barras.ilike(f"%{barcode}%")
            )
        if conditions:
            stmt = stmt.where(*conditions)
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def add_producto(self, producto: Producto) -> Producto:
        self.db.add(producto)
        await self.db.flush()
        return producto

    async def add_variante(self, variante: VarianteProducto) -> VarianteProducto:
        self.db.add(variante)
        await self.db.flush()
        return variante

    async def add_inventario(self, inventario: InventarioSucursal) -> InventarioSucursal:
        self.db.add(inventario)
        await self.db.flush()
        return inventario

    async def get_subcategoria_by_id(self, subcategoria_id: int) -> Optional[Subcategoria]:
        result = await self.db.execute(
            select(Subcategoria).where(Subcategoria.id_subcategoria == subcategoria_id)
        )
        return result.scalar_one_or_none()

    async def get_unidad_by_id(self, unidad_id: int) -> Optional[UnidadMedida]:
        result = await self.db.execute(
            select(UnidadMedida).where(UnidadMedida.id_unidad == unidad_id)
        )
        return result.scalar_one_or_none()

    async def get_sucursal_by_id(self, sucursal_id: int) -> Optional[Sucursal]:
        result = await self.db.execute(
            select(Sucursal).where(Sucursal.id_sucursal == sucursal_id)
        )
        return result.scalar_one_or_none()

    async def get_area_by_id(self, area_id: int) -> Optional[AreaBodega]:
        result = await self.db.execute(
            select(AreaBodega).where(AreaBodega.id_area == area_id)
        )
        return result.scalar_one_or_none()

    async def list_subcategorias(self, include_inactive: bool = False) -> List[Subcategoria]:
        stmt = select(Subcategoria).options(
            selectinload(Subcategoria.categoria)
        ).order_by(Subcategoria.nombre)
        if not include_inactive:
            stmt = stmt.join(Categoria).where(Categoria.estado == "Activo")
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def list_unidades(self) -> List[UnidadMedida]:
        result = await self.db.execute(select(UnidadMedida).order_by(UnidadMedida.descripcion))
        return list(result.scalars().all())

    async def list_sucursales(self, include_inactive: bool = False) -> List[Sucursal]:
        stmt = select(Sucursal).order_by(Sucursal.nombre)
        if not include_inactive:
            stmt = stmt.where(Sucursal.estado == "Activo")
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def list_areas(self, sucursal_id: Optional[int] = None) -> List[AreaBodega]:
        stmt = select(AreaBodega).order_by(AreaBodega.nombre_area)
        if sucursal_id is not None:
            stmt = stmt.where(AreaBodega.id_sucursal == sucursal_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def commit(self) -> None:
        await self.db.commit()

    async def rollback(self) -> None:
        await self.db.rollback()