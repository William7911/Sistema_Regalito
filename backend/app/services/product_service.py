from typing import Optional, List
from fastapi import HTTPException, status
from datetime import datetime
from app.db.models import Producto, VarianteProducto, InventarioSucursal, HistorialPrecio
from app.interfaces.repositories import ProductRepository
from app.interfaces.services import ProductService
from app.schemas import schemas
from app.services.audit_service import log_action


class ConcreteProductService(ProductService):
    """Lógica de negocio de Productos (inserción anidada Producto -> Variante -> Inventario).

    Las claves foráneas (subcategoría, unidad, sucursal, área) siempre se validan contra la BD.
    """

    def __init__(self, product_repository: ProductRepository):
        self.products = product_repository

    async def list_products(self, filters: schemas.ProductoFilter) -> List[schemas.ProductoOut]:
        products = await self.products.search(
            name=filters.name,
            barcode=filters.barcode,
            is_active=filters.is_active,
            subcategoria_id=filters.subcategoria_id,
            created_from=filters.created_from,
            created_to=filters.created_to,
            sort_by=filters.sort_by,
            sort_dir=filters.sort_dir or "asc",
            limit=filters.limit,
            offset=filters.offset,
        )
        return [schemas.ProductoOut.model_validate(p) for p in products]

    async def count_products(self, filters: schemas.ProductoFilter) -> int:
        return await self.products.count_search(
            name=filters.name,
            barcode=filters.barcode,
            is_active=filters.is_active,
            subcategoria_id=filters.subcategoria_id,
            created_from=filters.created_from,
            created_to=filters.created_to,
        )

    async def get_product(self, product_id: int) -> schemas.ProductoOut:
        product = await self.products.get_producto_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return schemas.ProductoOut.model_validate(product)

    async def get_by_barcode(self, barcode: str) -> schemas.ProductoOut:
        variante = await self.products.get_variante_by_barcode(barcode)
        if not variante:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        product = await self.products.get_producto_by_id(variante.id_producto)
        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        if product.estado != "Activo":
            raise HTTPException(status_code=400, detail="El producto está inactivo")
        return schemas.ProductoOut.model_validate(product)

    async def _validate_subcategoria(self, subcategoria_id: int):
        sub = await self.products.get_subcategoria_by_id(subcategoria_id)
        if not sub:
            raise HTTPException(status_code=400, detail="La subcategoría especificada no existe")
        return sub

    async def _validate_unidad(self, unidad_id: int):
        unidad = await self.products.get_unidad_by_id(unidad_id)
        if not unidad:
            raise HTTPException(status_code=400, detail="La unidad de medida especificada no existe")
        return unidad

    async def _validate_sucursal(self, sucursal_id: int):
        sucursal = await self.products.get_sucursal_by_id(sucursal_id)
        if not sucursal:
            raise HTTPException(status_code=400, detail="La sucursal especificada no existe")
        return sucursal

    async def _validate_area(self, area_id: int):
        if area_id is None:
            return
        area = await self.products.get_area_by_id(area_id)
        if not area:
            raise HTTPException(status_code=400, detail="El área de bodega especificada no existe")

    async def _validate_unique_barcode(
        self, codigo_barras: Optional[str], variante_id: Optional[int] = None
    ):
        if not codigo_barras:
            return
        existing = await self.products.get_variante_by_barcode(codigo_barras)
        if existing and existing.id_variante != variante_id:
            raise HTTPException(
                status_code=400, detail="Ya existe un producto con ese código de barras"
            )

    async def create_product(self, data: schemas.ProductoCreate, actor_id: int = 0) -> schemas.ProductoOut:
        await self._validate_subcategoria(data.id_subcategoria)
        await self._validate_unidad(data.id_unidad)
        await self._validate_sucursal(data.inventario.id_sucursal)
        await self._validate_area(data.inventario.id_area)
        await self._validate_unique_barcode(data.variante.codigo_barras)

        producto = Producto(
            id_subcategoria=data.id_subcategoria,
            id_unidad=data.id_unidad,
            nombre=data.nombre.strip(),
            descripcion=data.descripcion.strip() if data.descripcion else None,
            imagen_url=data.imagen_url.strip() if data.imagen_url else None,
            estado="Activo",
        )
        producto = await self.products.add_producto(producto)

        variante = VarianteProducto(
            id_producto=producto.id_producto,
            codigo_barras=data.variante.codigo_barras.strip() if data.variante.codigo_barras else None,
            talla=data.variante.talla.strip() if data.variante.talla else None,
            color=data.variante.color.strip() if data.variante.color else None,
            precio_detalle=data.variante.precio_detalle,
            precio_mayoreo=data.variante.precio_mayoreo,
            costo_promedio=data.variante.costo_promedio,
        )
        variante = await self.products.add_variante(variante)

        inventario = InventarioSucursal(
            id_variante=variante.id_variante,
            id_sucursal=data.inventario.id_sucursal,
            id_area=data.inventario.id_area,
            stock_actual=data.inventario.stock_actual,
            stock_minimo=data.inventario.stock_minimo,
            fecha_actualizacion=datetime.utcnow(),
        )
        await self.products.add_inventario(inventario)
        await self.products.commit()

        created = await self.products.get_producto_by_id(producto.id_producto)
        if actor_id:
            await log_action(
                self.products.db,
                id_usuario=actor_id,
                tabla="producto",
                accion="CREAR",
                descripcion=f"Creó producto '{created.nombre}' (ID {created.id_producto}).",
            )
            await self.products.commit()
        return schemas.ProductoOut.model_validate(created)

    async def update_product(
        self, product_id: int, data: schemas.ProductoUpdate, actor_id: int = 0
    ) -> schemas.ProductoOut:
        producto = await self.products.get_producto_by_id(product_id)
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        # Detectar cambios de precio para auditoría específica
        variante_previa = producto.variantes[0] if producto.variantes else None
        precio_detalle_prev = float(variante_previa.precio_detalle) if variante_previa else None
        precio_mayoreo_prev = float(variante_previa.precio_mayoreo) if variante_previa else None

        if data.id_subcategoria is not None:
            await self._validate_subcategoria(data.id_subcategoria)
            producto.id_subcategoria = data.id_subcategoria
        if data.id_unidad is not None:
            await self._validate_unidad(data.id_unidad)
            producto.id_unidad = data.id_unidad
        if data.nombre is not None:
            producto.nombre = data.nombre.strip()
        if data.descripcion is not None:
            producto.descripcion = data.descripcion.strip() if data.descripcion else None
        if data.imagen_url is not None:
            producto.imagen_url = data.imagen_url.strip() if data.imagen_url else None
        if data.estado is not None:
            producto.estado = data.estado.strip()

        variante = producto.variantes[0] if producto.variantes else None
        if data.variante is not None:
            if not variante:
                variante = VarianteProducto(
                    id_producto=producto.id_producto,
                    precio_detalle=0,
                    precio_mayoreo=0,
                    costo_promedio=0,
                )
                variante = await self.products.add_variante(variante)
            v = data.variante
            if v.codigo_barras is not None:
                await self._validate_unique_barcode(v.codigo_barras, variante.id_variante)
                variante.codigo_barras = v.codigo_barras.strip() if v.codigo_barras else None
            if v.talla is not None:
                variante.talla = v.talla.strip() if v.talla else None
            if v.color is not None:
                variante.color = v.color.strip() if v.color else None
            if v.precio_detalle is not None:
                variante.precio_detalle = v.precio_detalle
            if v.precio_mayoreo is not None:
                variante.precio_mayoreo = v.precio_mayoreo
            if v.costo_promedio is not None:
                variante.costo_promedio = v.costo_promedio

        inventario = variante.inventarios[0] if variante and variante.inventarios else None
        if data.inventario is not None:
            if not variante:
                variante = VarianteProducto(
                    id_producto=producto.id_producto,
                    precio_detalle=0,
                    precio_mayoreo=0,
                    costo_promedio=0,
                )
                variante = await self.products.add_variante(variante)
            if not inventario:
                inventario = InventarioSucursal(
                    id_variante=variante.id_variante,
                    id_sucursal=1,
                    stock_actual=0,
                    stock_minimo=0,
                    fecha_actualizacion=datetime.utcnow(),
                )
                await self.products.add_inventario(inventario)
            inv = data.inventario
            if inv.id_sucursal is not None:
                await self._validate_sucursal(inv.id_sucursal)
                inventario.id_sucursal = inv.id_sucursal
            if inv.id_area is not None:
                await self._validate_area(inv.id_area)
                inventario.id_area = inv.id_area
            if inv.stock_actual is not None:
                inventario.stock_actual = inv.stock_actual
            if inv.stock_minimo is not None:
                inventario.stock_minimo = inv.stock_minimo
            inventario.fecha_actualizacion = datetime.utcnow()

        await self.products.commit()

        updated = await self.products.get_producto_by_id(product_id)
        if actor_id:
            # Generar descripción de auditoría
            partes_precio = []
            variante_nueva = updated.variantes[0] if updated.variantes else None
            if variante_nueva and precio_detalle_prev is not None:
                nuevo_det = float(variante_nueva.precio_detalle)
                nuevo_may = float(variante_nueva.precio_mayoreo)
                if nuevo_det != precio_detalle_prev:
                    partes_precio.append(f"precio_detalle: Q{precio_detalle_prev:.2f}→Q{nuevo_det:.2f}")
                if nuevo_may != precio_mayoreo_prev:
                    partes_precio.append(f"precio_mayoreo: Q{precio_mayoreo_prev:.2f}→Q{nuevo_may:.2f}")
                # Registrar en historial_precio el cambio de precio de detalle
                if nuevo_det != precio_detalle_prev:
                    self.products.db.add(HistorialPrecio(
                        id_variante=variante_nueva.id_variante,
                        id_usuario=actor_id,
                        precio_anterior=precio_detalle_prev,
                        precio_nuevo=nuevo_det,
                        fecha_modificacion=datetime.utcnow(),
                    ))
            accion = "PRECIO" if partes_precio else "EDITAR"
            desc = f"Editó producto '{updated.nombre}' (ID {product_id})."
            if partes_precio:
                desc += " Cambio de precios: " + ", ".join(partes_precio) + "."
            await log_action(
                self.products.db,
                id_usuario=actor_id,
                tabla="producto",
                accion=accion,
                descripcion=desc,
            )
            await self.products.commit()
        return schemas.ProductoOut.model_validate(updated)

    async def deactivate_product(self, product_id: int, actor_id: int = 0) -> schemas.ProductoOut:
        """Eliminación lógica (soft delete): marca el producto como inactivo."""
        producto = await self.products.get_producto_by_id(product_id)
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        nombre_p = producto.nombre
        producto.estado = "Inactivo"
        await self.products.commit()
        updated = await self.products.get_producto_by_id(product_id)
        if actor_id:
            await log_action(
                self.products.db,
                id_usuario=actor_id,
                tabla="producto",
                accion="DESACTIVAR",
                descripcion=f"Desactivó producto '{nombre_p}' (ID {product_id}).",
            )
            await self.products.commit()
        return schemas.ProductoOut.model_validate(updated)