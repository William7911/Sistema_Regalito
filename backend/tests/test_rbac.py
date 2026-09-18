"""
Pruebas integrales de Control de Acceso Basado en Roles y Permisos (RBAC).
Verifica:
  1. Login en tiempo real con roles y permisos (RF de esquema Token).
  2. Restricción de módulos administrativos (Usuarios, Roles, Departamentos) sólo para Administradora.
  3. Protección de endpoints operativos por permisos:
     - Venta con o sin descuento (VENTA_COBRAR, VENTA_APLICAR_DESCUENTO)
     - Cierre a ciegas (CAJA_CIERRE_CIEGAS)
     - Apertura de caja (permitida para todos los autenticados)
     - Emisión de órdenes de compra (COMPRA_EMITIR_ORDEN)
     - Ingreso de mercadería (INV_INGRESAR_MERCADERIA)
"""
import pytest
from decimal import Decimal
from datetime import datetime, date
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.database import get_db
from app.core import security
from app.db.models import (
    Rol, Usuario, Permiso, RolPermiso, Sucursal, Caja, TurnoCaja,
    Categoria, Subcategoria, UnidadMedida, Producto, VarianteProducto,
    InventarioSucursal, MetodoPago, Proveedor
)


@pytest.fixture
async def client(db_session):
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c
    app.dependency_overrides.clear()


async def _seed_rbac_database(db):
    """Crea la estructura completa de roles, permisos, usuarios semilla y catálogo mínimo."""
    # 1. Roles
    rol_admin = Rol(id_rol=1, nombre="Administradora", estado="Activo")
    rol_cajero = Rol(id_rol=2, nombre="Cajero", estado="Activo")
    rol_bodega = Rol(id_rol=3, nombre="Bodeguero", estado="Activo")
    rol_cajero_no_desc = Rol(id_rol=4, nombre="CajeroSinDescuento", estado="Activo")
    db.add_all([rol_admin, rol_cajero, rol_bodega, rol_cajero_no_desc])
    await db.flush()

    # 2. Permisos oficiales
    permisos = [
        Permiso(id_permiso=1, modulo="Ventas", codigo="VENTA_COBRAR", descripcion="Registrar cobros en mostrador"),
        Permiso(id_permiso=2, modulo="Ventas", codigo="VENTA_APLICAR_DESCUENTO", descripcion="Aplicar descuentos por volumen"),
        Permiso(id_permiso=3, modulo="Inventario", codigo="INV_INGRESAR_MERCADERIA", descripcion="Registrar ingreso de compras"),
        Permiso(id_permiso=4, modulo="Caja", codigo="CAJA_CIERRE_CIEGAS", descripcion="Ejecutar arqueo de caja a ciegas"),
        Permiso(id_permiso=5, modulo="Compras", codigo="COMPRA_EMITIR_ORDEN", descripcion="Emitir órdenes de compra"),
    ]
    db.add_all(permisos)
    await db.flush()

    # 3. Rol - Permiso
    rol_perms = [
        # Administradora: todos (1..5)
        RolPermiso(id_rol=1, id_permiso=1),
        RolPermiso(id_rol=1, id_permiso=2),
        RolPermiso(id_rol=1, id_permiso=3),
        RolPermiso(id_rol=1, id_permiso=4),
        RolPermiso(id_rol=1, id_permiso=5),
        # Cajero: 1 y 2
        RolPermiso(id_rol=2, id_permiso=1),
        RolPermiso(id_rol=2, id_permiso=2),
        # Bodeguero: 3
        RolPermiso(id_rol=3, id_permiso=3),
        # CajeroSinDescuento: solo 1 (sin descuento)
        RolPermiso(id_rol=4, id_permiso=1),
    ]
    db.add_all(rol_perms)
    await db.flush()

    # 4. Usuarios semilla
    hash_pass = security.get_password_hash("admin123")
    u_admin = Usuario(id_usuario=1, id_rol=1, nombre_completo="Administradora General", username="admin", password_hash=hash_pass, estado="Activo")
    u_cajera = Usuario(id_usuario=2, id_rol=2, nombre_completo="Cajera Principal", username="cajera", password_hash=hash_pass, estado="Activo")
    u_bodega = Usuario(id_usuario=3, id_rol=3, nombre_completo="Bodeguero Central", username="bodega", password_hash=hash_pass, estado="Activo")
    u_caj_nodesc = Usuario(id_usuario=4, id_rol=4, nombre_completo="Cajero Junior", username="caj_nodesc", password_hash=hash_pass, estado="Activo")
    db.add_all([u_admin, u_cajera, u_bodega, u_caj_nodesc])
    await db.flush()

    # 5. Sucursal, Caja, Turnos
    sucursal = Sucursal(id_sucursal=1, nombre="Central", direccion="Zona 1", telefono="12345678", estado="Activa")
    db.add(sucursal)
    await db.flush()

    caja1 = Caja(id_caja=1, id_sucursal=1, descripcion="Caja Admin", estado="Activa")
    caja2 = Caja(id_caja=2, id_sucursal=1, descripcion="Caja Cajera", estado="Activa")
    caja3 = Caja(id_caja=3, id_sucursal=1, descripcion="Caja Cajero NoDesc", estado="Activa")
    caja4 = Caja(id_caja=4, id_sucursal=1, descripcion="Caja Bodega", estado="Activa")
    db.add_all([caja1, caja2, caja3, caja4])
    await db.flush()

    turno_admin = TurnoCaja(id_turno=1, id_caja=1, id_usuario=1, monto_apertura=Decimal("100.00"), fecha_apertura=datetime.now(), estado="Abierto")
    turno_cajera = TurnoCaja(id_turno=2, id_caja=2, id_usuario=2, monto_apertura=Decimal("100.00"), fecha_apertura=datetime.now(), estado="Abierto")
    turno_caj_nodesc = TurnoCaja(id_turno=3, id_caja=3, id_usuario=4, monto_apertura=Decimal("100.00"), fecha_apertura=datetime.now(), estado="Abierto")
    db.add_all([turno_admin, turno_cajera, turno_caj_nodesc])

    # 6. Catálogo mínimo para ventas e inventario
    cat = Categoria(id_categoria=1, nombre="General", estado="Activo")
    subcat = Subcategoria(id_subcategoria=1, id_categoria=1, nombre="Subgen")
    unidad = UnidadMedida(id_unidad=1, codigo="UND", descripcion="Unidad")
    metodo = MetodoPago(id_metodo_pago=1, nombre="Efectivo")
    proveedor = Proveedor(id_proveedor=1, nombre_contacto="Juan Proveedor", distribuidora="Distribuidora El Sol", telefono="55555555")
    db.add_all([cat, subcat, unidad, metodo, proveedor])
    await db.flush()

    producto = Producto(id_producto=1, id_subcategoria=1, id_unidad=1, nombre="Producto Test", estado="Activo")
    db.add(producto)
    await db.flush()

    variante = VarianteProducto(
        id_variante=1,
        id_producto=1,
        precio_detalle=Decimal("10.00"),
        precio_mayoreo=Decimal("8.00"),
        costo_promedio=Decimal("5.00"),
    )
    db.add(variante)
    await db.flush()

    inventario = InventarioSucursal(id_inventario=1, id_variante=1, id_sucursal=1, stock_actual=100, stock_minimo=5)
    db.add(inventario)

    await db.commit()


async def _get_token(client, username, password="admin123"):
    res = await client.post("/api/auth/login", data={"username": username, "password": password})
    assert res.status_code == 200, f"Login failed for {username}: {res.text}"
    return res.json()


@pytest.mark.asyncio
async def test_login_returns_roles_and_realtime_permissions(client, db_session):
    """1.1 y 1.2: El login devuelve el rol y permisos consultados en tiempo real."""
    await _seed_rbac_database(db_session)

    # Administradora
    data_admin = await _get_token(client, "admin")
    assert data_admin["rol"] == "Administradora"
    assert "VENTA_COBRAR" in data_admin["permisos"]
    assert "VENTA_APLICAR_DESCUENTO" in data_admin["permisos"]
    assert "INV_INGRESAR_MERCADERIA" in data_admin["permisos"]
    assert "CAJA_CIERRE_CIEGAS" in data_admin["permisos"]
    assert "COMPRA_EMITIR_ORDEN" in data_admin["permisos"]
    assert len(data_admin["permisos"]) == 5

    # Cajera
    data_cajera = await _get_token(client, "cajera")
    assert data_cajera["rol"] == "Cajero"
    assert sorted(data_cajera["permisos"]) == ["VENTA_APLICAR_DESCUENTO", "VENTA_COBRAR"]

    # Bodega
    data_bodega = await _get_token(client, "bodega")
    assert data_bodega["rol"] == "Bodeguero"
    assert data_bodega["permisos"] == ["INV_INGRESAR_MERCADERIA"]


@pytest.mark.asyncio
async def test_admin_only_modules_reject_non_admin(client, db_session):
    """1.4: Los módulos sin permiso granular (Usuarios, Roles, Departamentos) sólo permiten Administradora."""
    await _seed_rbac_database(db_session)

    token_admin = (await _get_token(client, "admin"))["access_token"]
    token_cajera = (await _get_token(client, "cajera"))["access_token"]
    token_bodega = (await _get_token(client, "bodega"))["access_token"]

    endpoints = [
        "/api/usuarios",
        "/api/roles",
        "/api/departamentos",
    ]

    for ep in endpoints:
        # Administradora -> 200 OK
        res_admin = await client.get(ep, headers={"Authorization": f"Bearer {token_admin}"})
        assert res_admin.status_code == 200, f"Admin should access {ep}, got {res_admin.status_code}"

        # Cajera -> 403 Forbidden
        res_cajera = await client.get(ep, headers={"Authorization": f"Bearer {token_cajera}"})
        assert res_cajera.status_code == 403, f"Cajera should be forbidden on {ep}"
        assert "requiere rol de Administradora" in res_cajera.json()["detail"]

        # Bodega -> 403 Forbidden
        res_bodega = await client.get(ep, headers={"Authorization": f"Bearer {token_bodega}"})
        assert res_bodega.status_code == 403, f"Bodega should be forbidden on {ep}"
        assert "requiere rol de Administradora" in res_bodega.json()["detail"]


@pytest.mark.asyncio
async def test_sales_endpoint_permission(client, db_session):
    """POST /api/ventas requiere VENTA_COBRAR. Cajero puede, Bodeguero recibe 403."""
    await _seed_rbac_database(db_session)

    token_cajera = (await _get_token(client, "cajera"))["access_token"]
    token_bodega = (await _get_token(client, "bodega"))["access_token"]

    payload_sale = {
        "id_sucursal": 1,
        "items": [{"id_variante": 1, "cantidad": 1}],
        "pagos": [{"id_metodo_pago": 1, "monto_recibido": 10.00}],
    }

    # Cajera tiene VENTA_COBRAR -> 201 Created
    res_caj = await client.post(
        "/api/ventas",
        json=payload_sale,
        headers={"Authorization": f"Bearer {token_cajera}"},
    )
    assert res_caj.status_code == 201, f"Cajera should sell, got: {res_caj.text}"

    # Bodeguero no tiene VENTA_COBRAR -> 403 Forbidden
    res_bod = await client.post(
        "/api/ventas",
        json=payload_sale,
        headers={"Authorization": f"Bearer {token_bodega}"},
    )
    assert res_bod.status_code == 403
    assert "VENTA_COBRAR" in res_bod.json()["detail"]


@pytest.mark.asyncio
async def test_sale_with_discount_permission(client, db_session):
    """Aplicar descuento requiere VENTA_APLICAR_DESCUENTO."""
    await _seed_rbac_database(db_session)

    token_cajera = (await _get_token(client, "cajera"))["access_token"]
    token_nodesc = (await _get_token(client, "caj_nodesc"))["access_token"]

    # Venta de 6 unidades activa mayoreo automático (descuento > 0)
    payload_mayoreo = {
        "id_sucursal": 1,
        "items": [{"id_variante": 1, "cantidad": 6}],
        "pagos": [{"id_metodo_pago": 1, "monto_recibido": 50.00}],
    }

    # Cajera tiene VENTA_APLICAR_DESCUENTO -> 201 Created
    res_caj = await client.post(
        "/api/ventas",
        json=payload_mayoreo,
        headers={"Authorization": f"Bearer {token_cajera}"},
    )
    assert res_caj.status_code == 201
    assert res_caj.json()["descuento_total"] == "12.00"

    # Cajero sin descuento intenta aplicar mayoreo -> 403 Forbidden
    res_no = await client.post(
        "/api/ventas",
        json=payload_mayoreo,
        headers={"Authorization": f"Bearer {token_nodesc}"},
    )
    assert res_no.status_code == 403
    assert "VENTA_APLICAR_DESCUENTO" in res_no.json()["detail"]


@pytest.mark.asyncio
async def test_caja_apertura_open_to_all_authenticated(client, db_session):
    """Aclaración 2: POST /api/caja/apertura está disponible para cualquier usuario autenticado."""
    await _seed_rbac_database(db_session)

    token_bodega = (await _get_token(client, "bodega"))["access_token"]

    # Bodeguero no tiene rol de cajero pero puede autenticar y abrir turno (no rechazado con 403)
    payload_apertura = {
        "id_caja": 4,
        "monto_apertura": 50.00,
    }
    res = await client.post(
        "/api/caja/apertura",
        json=payload_apertura,
        headers={"Authorization": f"Bearer {token_bodega}"},
    )
    assert res.status_code == 201, f"Expected 201, got: {res.status_code} - {res.text}"


@pytest.mark.asyncio
async def test_caja_cierre_ciegas_requires_permission(client, db_session):
    """POST /api/caja/cierre-ciegas requiere CAJA_CIERRE_CIEGAS."""
    await _seed_rbac_database(db_session)

    token_cajera = (await _get_token(client, "cajera"))["access_token"]
    token_bodega = (await _get_token(client, "bodega"))["access_token"]

    payload_cierre = {
        "detalles": [{"id_denominacion": 1, "cantidad_piezas": 10}],
        "observaciones": "Arqueo de prueba",
    }

    # Cajera no tiene CAJA_CIERRE_CIEGAS -> 403 Forbidden
    res_caj = await client.post(
        "/api/caja/cierre-ciegas",
        json=payload_cierre,
        headers={"Authorization": f"Bearer {token_cajera}"},
    )
    assert res_caj.status_code == 403
    assert "CAJA_CIERRE_CIEGAS" in res_caj.json()["detail"]

    # Bodeguero no tiene CAJA_CIERRE_CIEGAS -> 403 Forbidden
    res_bod = await client.post(
        "/api/caja/cierre-ciegas",
        json=payload_cierre,
        headers={"Authorization": f"Bearer {token_bodega}"},
    )
    assert res_bod.status_code == 403
    assert "CAJA_CIERRE_CIEGAS" in res_bod.json()["detail"]


@pytest.mark.asyncio
async def test_compras_endpoints_permissions(client, db_session):
    """POST /api/compras/ordenes requiere COMPRA_EMITIR_ORDEN.
    POST /api/compras/ingreso requiere INV_INGRESAR_MERCADERIA."""
    await _seed_rbac_database(db_session)

    token_admin = (await _get_token(client, "admin"))["access_token"]
    token_cajera = (await _get_token(client, "cajera"))["access_token"]
    token_bodega = (await _get_token(client, "bodega"))["access_token"]

    # 1. Orden de compra
    payload_orden = {
        "id_proveedor": 1,
        "detalles": [{"id_variante": 1, "cantidad_pedida": 10, "costo_pactado": 4.50}],
    }
    # Bodeguero no tiene COMPRA_EMITIR_ORDEN -> 403
    res_bod_ord = await client.post(
        "/api/compras/ordenes",
        json=payload_orden,
        headers={"Authorization": f"Bearer {token_bodega}"},
    )
    assert res_bod_ord.status_code == 403
    assert "COMPRA_EMITIR_ORDEN" in res_bod_ord.json()["detail"]

    # Administradora tiene COMPRA_EMITIR_ORDEN -> 201 Created
    res_adm_ord = await client.post(
        "/api/compras/ordenes",
        json=payload_orden,
        headers={"Authorization": f"Bearer {token_admin}"},
    )
    assert res_adm_ord.status_code == 201
    orden_id = res_adm_ord.json()["id_orden"]

    # 2. Ingreso de mercadería
    payload_ingreso = {
        "id_proveedor": 1,
        "numero_factura_proveedor": "FAC-9999",
        "id_orden": orden_id,
        "gasto_flete": 10.00,
        "gasto_cargadores": 5.00,
        "detalles": [
            {"id_variante": 1, "cantidad_recibida": 10, "costo_unitario": 4.50, "id_sucursal": 1}
        ],
    }
    # Cajera no tiene INV_INGRESAR_MERCADERIA -> 403
    res_caj_ing = await client.post(
        "/api/compras/ingreso",
        json=payload_ingreso,
        headers={"Authorization": f"Bearer {token_cajera}"},
    )
    assert res_caj_ing.status_code == 403
    assert "INV_INGRESAR_MERCADERIA" in res_caj_ing.json()["detail"]

    # Bodeguero tiene INV_INGRESAR_MERCADERIA -> 201 Created
    res_bod_ing = await client.post(
        "/api/compras/ingreso",
        json=payload_ingreso,
        headers={"Authorization": f"Bearer {token_bodega}"},
    )
    assert res_bod_ing.status_code == 201
    assert res_bod_ing.json()["total_compra"] == "60.00"
