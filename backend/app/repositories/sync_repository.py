import os
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy import select, delete, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.config import settings
from app.db.models import (
    Base,
    Rol, Permiso, RolPermiso, Usuario,
    Categoria, Subcategoria, UnidadMedida,
    Producto, VarianteProducto, InventarioSucursal,
    Sucursal, AreaBodega, Caja, MetodoPago,
    DenominacionEfectivo, TipoMovimientoCaja, MotivoMerma,
    TipoCliente, Cliente, ParametroSistema,
    SyncCacheMetadata,
)
from app.interfaces.repositories import SyncRepository


class SyncRepositoryImpl(SyncRepository):
    """Implementación del repositorio de sincronización y réplica de datos maestros hacia SQLite local."""

    def __init__(self, cloud_db: AsyncSession, sqlite_url: str = None, sqlite_path: str = None):
        self.cloud_db = cloud_db
        self.sqlite_url = sqlite_url or settings.LOCAL_SQLITE_URL
        self.sqlite_path = sqlite_path or settings.LOCAL_SQLITE_PATH
        self._local_engine = None

    def _get_local_engine(self):
        if self._local_engine is None:
            self._local_engine = create_async_engine(self.sqlite_url, echo=False)
        return self._local_engine

    async def fetch_cloud_snapshot(self) -> Dict[str, List[Dict[str, Any]]]:
        """Extrae el snapshot maestro actual desde PostgreSQL (nube)."""
        snapshot = {}

        # 1. Seguridad e Identidad
        res = await self.cloud_db.execute(select(Rol))
        snapshot["rol"] = [{"id_rol": r.id_rol, "nombre": r.nombre, "descripcion": r.descripcion, "estado": r.estado} for r in res.scalars().all()]

        res = await self.cloud_db.execute(select(Permiso))
        snapshot["permiso"] = [{"id_permiso": p.id_permiso, "modulo": p.modulo, "codigo": p.codigo, "descripcion": p.descripcion} for p in res.scalars().all()]

        res = await self.cloud_db.execute(select(RolPermiso))
        snapshot["rol_permiso"] = [{"id_rol": rp.id_rol, "id_permiso": rp.id_permiso} for rp in res.scalars().all()]

        res = await self.cloud_db.execute(select(Usuario))
        snapshot["usuario"] = [
            {
                "id_usuario": u.id_usuario,
                "id_rol": u.id_rol,
                "nombre_completo": u.nombre_completo,
                "username": u.username,
                "password_hash": u.password_hash,
                "estado": u.estado,
                "fecha_creacion": u.fecha_creacion,
            }
            for u in res.scalars().all()
        ]

        # 2. Catálogo y Clasificación
        res = await self.cloud_db.execute(select(Categoria))
        snapshot["categoria"] = [{"id_categoria": c.id_categoria, "nombre": c.nombre, "estado": c.estado} for c in res.scalars().all()]

        res = await self.cloud_db.execute(select(Subcategoria))
        snapshot["subcategoria"] = [{"id_subcategoria": s.id_subcategoria, "id_categoria": s.id_categoria, "nombre": s.nombre} for s in res.scalars().all()]

        res = await self.cloud_db.execute(select(UnidadMedida))
        snapshot["unidad_medida"] = [{"id_unidad": u.id_unidad, "codigo": u.codigo, "descripcion": u.descripcion} for u in res.scalars().all()]

        res = await self.cloud_db.execute(select(Producto))
        snapshot["producto"] = [
            {
                "id_producto": p.id_producto,
                "id_subcategoria": p.id_subcategoria,
                "id_unidad": p.id_unidad,
                "nombre": p.nombre,
                "descripcion": p.descripcion,
                "imagen_url": p.imagen_url,
                "estado": p.estado,
                "fecha_creacion": p.fecha_creacion,
            }
            for p in res.scalars().all()
        ]

        res = await self.cloud_db.execute(select(VarianteProducto))
        snapshot["variante_producto"] = [
            {
                "id_variante": v.id_variante,
                "id_producto": v.id_producto,
                "codigo_barras": v.codigo_barras,
                "talla": v.talla,
                "color": v.color,
                "precio_detalle": v.precio_detalle,
                "precio_mayoreo": v.precio_mayoreo,
                "costo_promedio": v.costo_promedio,
            }
            for v in res.scalars().all()
        ]

        res = await self.cloud_db.execute(select(InventarioSucursal))
        snapshot["inventario_sucursal"] = [
            {
                "id_inventario": inv.id_inventario,
                "id_variante": inv.id_variante,
                "id_sucursal": inv.id_sucursal,
                "id_area": inv.id_area,
                "stock_actual": inv.stock_actual,
                "stock_minimo": inv.stock_minimo,
                "fecha_actualizacion": inv.fecha_actualizacion,
            }
            for inv in res.scalars().all()
        ]

        # 3. Auxiliares y Parámetros
        res = await self.cloud_db.execute(select(Sucursal))
        snapshot["sucursal"] = [{"id_sucursal": s.id_sucursal, "nombre": s.nombre, "direccion": s.direccion, "telefono": s.telefono, "estado": s.estado} for s in res.scalars().all()]

        res = await self.cloud_db.execute(select(AreaBodega))
        snapshot["area_bodega"] = [{"id_area": a.id_area, "id_sucursal": a.id_sucursal, "nombre_area": a.nombre_area} for a in res.scalars().all()]

        res = await self.cloud_db.execute(select(Caja))
        snapshot["caja"] = [{"id_caja": c.id_caja, "id_sucursal": c.id_sucursal, "descripcion": c.descripcion, "estado": c.estado} for c in res.scalars().all()]

        res = await self.cloud_db.execute(select(MetodoPago))
        snapshot["metodo_pago"] = [{"id_metodo_pago": m.id_metodo_pago, "nombre": m.nombre} for m in res.scalars().all()]

        res = await self.cloud_db.execute(select(DenominacionEfectivo))
        snapshot["denominacion_efectivo"] = [{"id_denominacion": d.id_denominacion, "valor": d.valor, "tipo": d.tipo} for d in res.scalars().all()]

        res = await self.cloud_db.execute(select(TipoMovimientoCaja))
        snapshot["tipo_movimiento_caja"] = [{"id_tipo_movimiento": tm.id_tipo_movimiento, "nombre": tm.nombre} for tm in res.scalars().all()]

        res = await self.cloud_db.execute(select(MotivoMerma))
        snapshot["motivo_merma"] = [{"id_motivo": mm.id_motivo, "descripcion": mm.descripcion} for mm in res.scalars().all()]

        res = await self.cloud_db.execute(select(TipoCliente))
        snapshot["tipo_cliente"] = [{"id_tipo_cliente": tc.id_tipo_cliente, "nombre": tc.nombre, "descuento_predeterminado": tc.descuento_predeterminado} for tc in res.scalars().all()]

        res = await self.cloud_db.execute(select(Cliente))
        snapshot["cliente"] = [{"id_cliente": cl.id_cliente, "id_tipo_cliente": cl.id_tipo_cliente, "nit": cl.nit, "nombre_comercial": cl.nombre_comercial, "direccion": cl.direccion} for cl in res.scalars().all()]

        res = await self.cloud_db.execute(select(ParametroSistema))
        snapshot["parametro_sistema"] = [{"id_parametro": ps.id_parametro, "clave": ps.clave, "valor": ps.valor} for ps in res.scalars().all()]

        return snapshot

    async def replicate_to_sqlite(self, snapshot: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Crea el esquema si no existe y vuelca atómicamente el snapshot en SQLite local."""
        engine = self._get_local_engine()

        # 1. Asegurar que el DDL existe en SQLite
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        session_maker = async_sessionmaker(engine, expire_on_commit=False)
        counts = {}
        ahora = datetime.now()

        async with session_maker() as session:
            async with session.begin():
                # Borrado en orden inverso de dependencias para evitar violaciones de clave foránea
                await session.execute(delete(InventarioSucursal))
                await session.execute(delete(VarianteProducto))
                await session.execute(delete(Producto))
                await session.execute(delete(Subcategoria))
                await session.execute(delete(Categoria))
                await session.execute(delete(UnidadMedida))
                await session.execute(delete(AreaBodega))
                await session.execute(delete(Caja))
                await session.execute(delete(Sucursal))
                await session.execute(delete(RolPermiso))
                await session.execute(delete(Permiso))
                await session.execute(delete(Usuario))
                await session.execute(delete(Rol))
                await session.execute(delete(Cliente))
                await session.execute(delete(TipoCliente))
                await session.execute(delete(MetodoPago))
                await session.execute(delete(DenominacionEfectivo))
                await session.execute(delete(TipoMovimientoCaja))
                await session.execute(delete(MotivoMerma))
                await session.execute(delete(ParametroSistema))

                # Inserción en orden de dependencias
                # Rol & Permiso
                for item in snapshot.get("rol", []):
                    session.add(Rol(**item))
                for item in snapshot.get("permiso", []):
                    session.add(Permiso(**item))
                await session.flush()

                for item in snapshot.get("rol_permiso", []):
                    session.add(RolPermiso(**item))
                for item in snapshot.get("usuario", []):
                    session.add(Usuario(**item))
                await session.flush()

                # Catálogo
                for item in snapshot.get("categoria", []):
                    session.add(Categoria(**item))
                for item in snapshot.get("unidad_medida", []):
                    session.add(UnidadMedida(**item))
                for item in snapshot.get("sucursal", []):
                    session.add(Sucursal(**item))
                await session.flush()

                for item in snapshot.get("subcategoria", []):
                    session.add(Subcategoria(**item))
                for item in snapshot.get("area_bodega", []):
                    session.add(AreaBodega(**item))
                for item in snapshot.get("caja", []):
                    session.add(Caja(**item))
                for item in snapshot.get("tipo_cliente", []):
                    session.add(TipoCliente(**item))
                await session.flush()

                for item in snapshot.get("cliente", []):
                    session.add(Cliente(**item))
                for item in snapshot.get("producto", []):
                    session.add(Producto(**item))
                await session.flush()

                for item in snapshot.get("variante_producto", []):
                    session.add(VarianteProducto(**item))
                await session.flush()

                for item in snapshot.get("inventario_sucursal", []):
                    session.add(InventarioSucursal(**item))
                for item in snapshot.get("metodo_pago", []):
                    session.add(MetodoPago(**item))
                for item in snapshot.get("denominacion_efectivo", []):
                    session.add(DenominacionEfectivo(**item))
                for item in snapshot.get("tipo_movimiento_caja", []):
                    session.add(TipoMovimientoCaja(**item))
                for item in snapshot.get("motivo_merma", []):
                    session.add(MotivoMerma(**item))
                for item in snapshot.get("parametro_sistema", []):
                    session.add(ParametroSistema(**item))

                # Actualizar metadatos de sincronización
                for tabla_nombre, registros in snapshot.items():
                    cant = len(registros)
                    counts[tabla_nombre] = cant
                    stmt = select(SyncCacheMetadata).where(SyncCacheMetadata.tabla == tabla_nombre)
                    res_meta = await session.execute(stmt)
                    meta_row = res_meta.scalar_one_or_none()
                    if not meta_row:
                        meta_row = SyncCacheMetadata(
                            tabla=tabla_nombre,
                            registros_sincronizados=cant,
                            fecha_sincronizacion=ahora,
                        )
                        session.add(meta_row)
                    else:
                        meta_row.registros_sincronizados = cant
                        meta_row.fecha_sincronizacion = ahora

        return {
            "status": "success",
            "synced_at": ahora.isoformat(),
            "counts": counts,
            "sqlite_file": self.sqlite_path,
        }

    async def get_sqlite_status(self) -> Dict[str, Any]:
        """Consulta el estado del archivo SQLite local y sus registros sincronizados."""
        exists = os.path.exists(self.sqlite_path)
        if not exists:
            return {
                "initialized": False,
                "file_exists": False,
                "file_path": self.sqlite_path,
                "file_size_bytes": 0,
                "last_sync": None,
                "counts": {},
            }

        file_size = os.path.getsize(self.sqlite_path)
        engine = self._get_local_engine()
        session_maker = async_sessionmaker(engine, expire_on_commit=False)
        counts = {}
        last_sync = None

        try:
            async with session_maker() as session:
                res_prod = await session.execute(select(Producto))
                counts["productos"] = len(res_prod.scalars().all())

                res_var = await session.execute(select(VarianteProducto))
                counts["variantes"] = len(res_var.scalars().all())

                res_user = await session.execute(select(Usuario))
                counts["usuarios"] = len(res_user.scalars().all())

                res_cat = await session.execute(select(Categoria))
                counts["categorias"] = len(res_cat.scalars().all())

                res_rol = await session.execute(select(Rol))
                counts["roles"] = len(res_rol.scalars().all())

                res_meta = await session.execute(select(SyncCacheMetadata).order_by(SyncCacheMetadata.fecha_sincronizacion.desc()))
                first_meta = res_meta.scalars().first()
                if first_meta:
                    last_sync = first_meta.fecha_sincronizacion.isoformat()
        except Exception:
            return {
                "initialized": False,
                "file_exists": True,
                "file_path": self.sqlite_path,
                "file_size_bytes": file_size,
                "last_sync": None,
                "counts": {},
            }

        return {
            "initialized": True,
            "file_exists": True,
            "file_path": self.sqlite_path,
            "file_size_bytes": file_size,
            "last_sync": last_sync,
            "counts": counts,
        }

    async def get_sqlite_preview(self) -> Dict[str, Any]:
        """Lee directamente de SQLite local para previsualizar productos con precios y usuarios."""
        if not os.path.exists(self.sqlite_path):
            return {"productos": [], "usuarios": []}

        engine = self._get_local_engine()
        session_maker = async_sessionmaker(engine, expire_on_commit=False)

        async with session_maker() as session:
            # Consultar productos con variantes y categorías
            stmt_prod = select(Producto).order_by(Producto.id_producto.asc())
            res_prod = await session.execute(stmt_prod)
            productos_orm = res_prod.scalars().all()

            stmt_var = select(VarianteProducto)
            res_var = await session.execute(stmt_var)
            variantes = res_var.scalars().all()
            var_map = {}
            for v in variantes:
                var_map.setdefault(v.id_producto, []).append(v)

            stmt_cat = select(Categoria)
            res_cat = await session.execute(stmt_cat)
            categorias = {c.id_categoria: c.nombre for c in res_cat.scalars().all()}

            stmt_sub = select(Subcategoria)
            res_sub = await session.execute(stmt_sub)
            subcategorias = {s.id_subcategoria: (s.nombre, s.id_categoria) for s in res_sub.scalars().all()}

            productos_out = []
            for p in productos_orm:
                sub_info = subcategorias.get(p.id_subcategoria, ("General", 1))
                cat_nombre = categorias.get(sub_info[1], "General")
                vars_p = var_map.get(p.id_producto, [])
                primera_var = vars_p[0] if vars_p else None

                productos_out.append({
                    "id_producto": p.id_producto,
                    "nombre": p.nombre,
                    "categoria": cat_nombre,
                    "subcategoria": sub_info[0],
                    "estado": p.estado,
                    "codigo_barras": primera_var.codigo_barras if primera_var else "-",
                    "precio_detalle": float(primera_var.precio_detalle) if primera_var else 0.0,
                    "precio_mayoreo": float(primera_var.precio_mayoreo) if primera_var else 0.0,
                    "costo_promedio": float(primera_var.costo_promedio) if primera_var else 0.0,
                })

            # Consultar usuarios con roles
            stmt_rol = select(Rol)
            res_rol = await session.execute(stmt_rol)
            roles = {r.id_rol: r.nombre for r in res_rol.scalars().all()}

            stmt_user = select(Usuario).order_by(Usuario.id_usuario.asc())
            res_user = await session.execute(stmt_user)
            usuarios_orm = res_user.scalars().all()

            usuarios_out = [
                {
                    "id_usuario": u.id_usuario,
                    "nombre_completo": u.nombre_completo,
                    "username": u.username,
                    "rol": roles.get(u.id_rol, "Desconocido"),
                    "estado": u.estado,
                }
                for u in usuarios_orm
            ]

            return {
                "productos": productos_out,
                "usuarios": usuarios_out,
            }

