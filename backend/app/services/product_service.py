from typing import Optional, List
from fastapi import HTTPException, status
from datetime import datetime
from app.db.models import Producto, VarianteProducto, InventarioSucursal
from app.interfaces.repositories import ProductRepository
from app.interfaces.services import ProductService
from app.schemas import schemas


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

    async def create_product(self, data: schemas.ProductoCreate) -> schemas.ProductoOut:
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
        return schemas.ProductoOut.model_validate(created)

    async def update_product(
        self, product_id: int, data: schemas.ProductoUpdate
    ) -> schemas.ProductoOut:
        producto = await self.products.get_producto_by_id(product_id)
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

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
        return schemas.ProductoOut.model_validate(updated)

    async def deactivate_product(self, product_id: int) -> schemas.ProductoOut:
        """Eliminación lógica (soft delete): marca el producto como inactivo."""
        producto = await self.products.get_producto_by_id(product_id)
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        producto.estado = "Inactivo"
        await self.products.commit()
        updated = await self.products.get_producto_by_id(product_id)
        return schemas.ProductoOut.model_validate(updated)