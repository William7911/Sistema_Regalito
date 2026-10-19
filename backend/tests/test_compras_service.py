"""
Pruebas unitarias para el Módulo de Compras e Ingreso a Bodega.
Aplica metodología TDD basándose en specs/compras.feature.
"""
import pytest
from decimal import Decimal
from datetime import date
from fastapi import HTTPException
from sqlalchemy import select, func
from app.db.models import (
    Rol, Usuario, Permiso, RolPermiso, Proveedor, Sucursal, Categoria, 
    Subcategoria, UnidadMedida, Producto, VarianteProducto, InventarioSucursal, 
    OrdenCompra, DetalleOrdenCompra, BitacoraAuditoria
)

# En TDD, estas clases/esquemas aún no existen, las importamos suponiendo el diseño DERCAS
try:
    from app.services.compra_service import ConcreteComprasService
    from app.schemas.compras_schema import (
        OrdenCompraCreate, DetalleOrdenCompraCreate, IngresoMercaderiaCreate, DetalleIngresoCreate
    )
except ImportError:
    # Dummy fallbacks para que pytest recolecte el archivo aunque la lógica no exista aún
    ConcreteComprasService = None
    OrdenCompraCreate = None
    DetalleOrdenCompraCreate = None
    IngresoMercaderiaCreate = None
    DetalleIngresoCreate = None


@pytest.fixture
def compras_service(uow):
    if not ConcreteComprasService:
        pytest.skip("ConcreteComprasService no implementado todavía (TDD)")
    return ConcreteComprasService(uow)


async def _seed_compras_data(db):
    """Prepara el estado inicial de la base de datos para compras."""
    # 1. Permisos
    p1 = Permiso(id_permiso=1, codigo="COMPRA_EMITIR_ORDEN", modulo="COMPRAS")
    p2 = Permiso(id_permiso=2, codigo="INV_INGRESAR_MERCADERIA", modulo="INVENTARIO")
    
    # 2. Roles
    rol_admin = Rol(id_rol=1, nombre="Administradora", estado="Activo")
    rol_bodega = Rol(id_rol=2, nombre="Bodeguero", estado="Activo")
    rol_cajero = Rol(id_rol=3, nombre="Cajero", estado="Activo") # Sin permisos
    
    db.add_all([p1, p2, rol_admin, rol_bodega, rol_cajero])
    await db.flush()

    # 3. Mapeo Rol-Permiso
    rp1 = RolPermiso(id_rol=1, id_permiso=1) # Admin puede emitir
    rp2 = RolPermiso(id_rol=1, id_permiso=2) # Admin puede ingresar
    rp3 = RolPermiso(id_rol=2, id_permiso=2) # Bodega puede ingresar
    db.add_all([rp1, rp2, rp3])
    await db.flush()

    # 4. Usuarios
    u_admin = Usuario(id_usuario=1, id_rol=1, nombre_completo="Admin", username="admin", password_hash="h", estado="Activo")
    u_bodega = Usuario(id_usuario=2, id_rol=2, nombre_completo="Bodeguero", username="bodega", password_hash="h", estado="Activo")
    u_cajero = Usuario(id_usuario=3, id_rol=3, nombre_completo="Cajero", username="cajero", password_hash="h", estado="Activo")
    db.add_all([u_admin, u_bodega, u_cajero])
    await db.flush()

    # 5. Proveedor y Catálogo
    proveedor = Proveedor(id_proveedor=1, nombre_contacto="John Doe", distribuidora="Distribuidora X")
    sucursal = Sucursal(id_sucursal=1, nombre="Central", direccion="D1", estado="Activa")
    cat = Categoria(id_categoria=1, nombre="General", estado="Activo")
    subcat = Subcategoria(id_subcategoria=1, id_categoria=1, nombre="Subgen")
    unidad = UnidadMedida(id_unidad=1, codigo="UND", descripcion="Unidad")
    
    db.add_all([proveedor, sucursal, cat, subcat, unidad])
    await db.flush()

    producto = Producto(id_producto=1, id_subcategoria=1, id_unidad=1, nombre="Pelota", estado="Activo")
    db.add(producto)
    await db.flush()

    variante = VarianteProducto(
        id_variante=1, id_producto=1, precio_detalle=Decimal("10.0"), 
        precio_mayoreo=Decimal("8.0"), costo_promedio=Decimal("5.0")
    )
    db.add(variante)
    await db.flush()

    # 6. Inventario Inicial (Stock 10)
    inventario = InventarioSucursal(
        id_inventario=1, id_variante=1, id_sucursal=1, stock_actual=10, stock_minimo=5
    )
    db.add(inventario)
    await db.commit()
    
    return {"admin": 1, "bodega": 2, "cajero": 3, "sucursal": 1, "proveedor": 1, "variante": 1}


@pytest.mark.asyncio
async def test_emitir_orden_compra_exito(compras_service, db_session, uow):
    """Escenario: Emisión exitosa de una Orden de Compra por un usuario autorizado."""
    ctx = await _seed_compras_data(db_session)
    
    payload = OrdenCompraCreate(
        id_proveedor=ctx["proveedor"],
        detalles=[DetalleOrdenCompraCreate(id_variante=ctx["variante"], cantidad_pedida=50, costo_pactado=Decimal("5.00"))]
    )
    
    orden = await compras_service.crear_orden(payload, user_id=ctx["admin"])
    
    # Aserciones lógicas
    assert orden.estado == "Emitida"
    assert orden.total_estimado == Decimal("250.00")
    
    # Aserción ESTRICTA DB: Verificar persistencia
    orden_db = await db_session.get(OrdenCompra, orden.id_orden)
    assert orden_db is not None
    assert orden_db.estado == "Emitida"
    
    # Aserción ESTRICTA DB: El inventario NO debe haberse alterado aún
    inv = await db_session.get(InventarioSucursal, 1)
    assert inv.stock_actual == 10


@pytest.mark.asyncio
async def test_recibir_orden_compra_exito(compras_service, db_session, uow):
    """Escenario: Ingreso de mercadería a bodega por el rol Bodeguero."""
    ctx = await _seed_compras_data(db_session)
    
    # Pre-condición: Crear una orden "Emitida"
    orden_pre = OrdenCompra(
        id_orden=1, id_proveedor=ctx["proveedor"], id_usuario=ctx["admin"], 
        fecha_emision=date.today(), total_estimado=Decimal("250.00"), estado="Emitida"
    )
    detalle_pre = DetalleOrdenCompra(
        id_detalle_orden=1, id_orden=1, id_variante=ctx["variante"], 
        cantidad_pedida=50, costo_pactado=Decimal("5.00")
    )
    db_session.add_all([orden_pre, detalle_pre])
    await db_session.commit()
    
    payload = IngresoMercaderiaCreate(
        id_orden=1, 
        id_proveedor=ctx["proveedor"],
        numero_factura_proveedor="INV-12345",
        detalles=[DetalleIngresoCreate(id_variante=ctx["variante"], cantidad_recibida=50, costo_unitario=Decimal("5.00"))]
    )
    
    # Acción: Bodeguero recibe la orden
    resultado = await compras_service.ingresar_mercaderia(payload, user_id=ctx["bodega"])
    
    assert resultado.estado == "Recibida"
    
    # Aserción ESTRICTA DB: El inventario DEBE haberse incrementado (10 + 50 = 60)
    inv = await db_session.get(InventarioSucursal, 1)
    assert inv.stock_actual == 60
    
    # Aserción ESTRICTA DB: Se debió generar una bitácora de auditoría
    auditorias = (await db_session.execute(select(func.count(BitacoraAuditoria.id_bitacora)))).scalar()
    assert auditorias >= 1


@pytest.mark.asyncio
async def test_emitir_orden_sin_permisos_falla(compras_service, db_session, uow):
    """Escenario: Rechazo en la emisión de orden por falta de permiso (HTTP 403)."""
    ctx = await _seed_compras_data(db_session)
    
    payload = OrdenCompraCreate(
        id_proveedor=ctx["proveedor"],
        detalles=[DetalleOrdenCompraCreate(id_variante=ctx["variante"], cantidad_pedida=10, costo_pactado=Decimal("5.00"))]
    )
    
    # Acción: Cajero intenta crear orden
    with pytest.raises(HTTPException) as exc_info:
        await compras_service.crear_orden(payload, user_id=ctx["cajero"])
        
    await db_session.rollback()
    
    assert exc_info.value.status_code == 403
    
    # Aserción ESTRICTA DB: Ninguna orden debió guardarse
    ordenes = (await db_session.execute(select(func.count(OrdenCompra.id_orden)))).scalar()
    assert ordenes == 0


@pytest.mark.asyncio
async def test_recibir_orden_sin_permisos_falla(compras_service, db_session, uow):
    """Escenario: Rechazo en el ingreso de mercadería por falta de permiso (HTTP 403)."""
    ctx = await _seed_compras_data(db_session)
    
    orden_pre = OrdenCompra(
        id_orden=1, id_proveedor=ctx["proveedor"], id_usuario=ctx["admin"], 
        fecha_emision=date.today(), total_estimado=Decimal("250.00"), estado="Emitida"
    )
    db_session.add(orden_pre)
    await db_session.commit()
    
    payload = IngresoMercaderiaCreate(
        id_orden=1,
        id_proveedor=ctx["proveedor"],
        numero_factura_proveedor="INV-12345",
        detalles=[DetalleIngresoCreate(id_variante=ctx["variante"], cantidad_recibida=50, costo_unitario=Decimal("5.00"))]
    )
    
    # Acción: Cajero intenta recibir orden
    with pytest.raises(HTTPException) as exc_info:
        await compras_service.ingresar_mercaderia(payload, user_id=ctx["cajero"])
        
    await db_session.rollback()
    
    assert exc_info.value.status_code == 403
    
    # Aserción ESTRICTA DB: Inventario intacto
    inv = await db_session.get(InventarioSucursal, 1)
    assert inv.stock_actual == 10
    
    # Aserción ESTRICTA DB: Orden sigue en estado "Emitida"
    orden_db = await db_session.get(OrdenCompra, 1)
    assert orden_db.estado == "Emitida"


@pytest.mark.asyncio
async def test_emitir_orden_cantidad_negativa_falla(compras_service, db_session, uow):
    ctx = await _seed_compras_data(db_session)
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        payload = OrdenCompraCreate(
            id_proveedor=ctx["proveedor"],
            detalles=[DetalleOrdenCompraCreate(id_variante=ctx["variante"], cantidad_pedida=-10, costo_pactado=Decimal("5.00"))]
        )
    await db_session.rollback()
    ordenes = (await db_session.execute(select(func.count(OrdenCompra.id_orden)))).scalar()
    assert ordenes == 0
