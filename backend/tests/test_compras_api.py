import pytest
from decimal import Decimal
from datetime import datetime, date
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.database import get_db
from app.core import security
from app.db.models import (
    Rol, Usuario, Permiso, RolPermiso, Sucursal, Categoria, Subcategoria, UnidadMedida,
    Producto, VarianteProducto, InventarioSucursal, Proveedor, OrdenCompra, DetalleOrdenCompra, BitacoraAuditoria
)
from sqlalchemy import select


@pytest.fixture
async def client(db_session):
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c
    app.dependency_overrides.clear()


async def seed_compras_api_env(db_session):
    p1 = Permiso(id_permiso=1, modulo="Compras", codigo="COMPRA_EMITIR_ORDEN", descripcion="Emitir orden")
    p2 = Permiso(id_permiso=2, modulo="Inventario", codigo="INV_INGRESAR_MERCADERIA", descripcion="Ingresar mercadería")
    p3 = Permiso(id_permiso=3, modulo="Ventas", codigo="VENTA_COBRAR", descripcion="Cobro")
    db_session.add_all([p1, p2, p3])
    await db_session.flush()

    rol_admin = Rol(id_rol=1, nombre="Administradora", estado="Activo")
    rol_bodega = Rol(id_rol=2, nombre="Bodeguero", estado="Activo")
    rol_cajera = Rol(id_rol=3, nombre="Cajera", estado="Activo")
    db_session.add_all([rol_admin, rol_bodega, rol_cajera])
    await db_session.flush()

    db_session.add_all([
        RolPermiso(id_rol=1, id_permiso=1),
        RolPermiso(id_rol=1, id_permiso=2),
        RolPermiso(id_rol=2, id_permiso=2),
        RolPermiso(id_rol=3, id_permiso=3),
    ])
    await db_session.flush()

    user_admin = Usuario(
        id_usuario=1, id_rol=1, nombre_completo="Admin Test",
        username="admin_compras", password_hash=security.get_password_hash("pass123"), estado="Activo"
    )
    user_bodega = Usuario(
        id_usuario=2, id_rol=2, nombre_completo="Bodeguero Test",
        username="bodega_compras", password_hash=security.get_password_hash("pass123"), estado="Activo"
    )
    user_cajera = Usuario(
        id_usuario=3, id_rol=3, nombre_completo="Cajera Test",
        username="cajera_compras", password_hash=security.get_password_hash("pass123"), estado="Activo"
    )
    db_session.add_all([user_admin, user_bodega, user_cajera])
    await db_session.flush()

    sucursal = Sucursal(id_sucursal=1, nombre="Central", direccion="Zona 1", estado="Activo")
    proveedor = Proveedor(id_proveedor=1, nombre_contacto="Juan Distribuidor", distribuidora="Distribuidora Central", estado="Activo")
    cat = Categoria(id_categoria=1, nombre="General", estado="Activo")
    subcat = Subcategoria(id_subcategoria=1, id_categoria=1, nombre="General Sub", estado="Activo")
    unidad = UnidadMedida(id_unidad=1, codigo="UND", descripcion="Unidad", estado="Activo")
    db_session.add_all([sucursal, proveedor, cat, subcat, unidad])
    await db_session.flush()

    prod = Producto(id_producto=1, id_subcategoria=1, id_unidad=1, nombre="Cuaderno Espiral", estado="Activo")
    db_session.add(prod)
    await db_session.flush()

    var = VarianteProducto(
        id_variante=1, id_producto=1, codigo_barras="7401001",
        costo_promedio=Decimal("15.00"),
        precio_detalle=Decimal("25.00"), precio_mayoreo=Decimal("20.00")
    )
    db_session.add(var)
    await db_session.flush()

    inv = InventarioSucursal(
        id_inventario=1, id_variante=1, id_sucursal=1,
        stock_actual=10, stock_minimo=5
    )
    db_session.add(inv)
    await db_session.commit()

    return {
        "admin_token": security.create_access_token({"sub": "admin_compras"}),
        "bodega_token": security.create_access_token({"sub": "bodega_compras"}),
        "cajera_token": security.create_access_token({"sub": "cajera_compras"}),
        "id_proveedor": 1,
        "id_variante": 1,
        "id_sucursal": 1,
    }


@pytest.mark.asyncio
async def test_emitir_orden_api_exito_admin(client, db_session):
    env = await seed_compras_api_env(db_session)
    headers = {"Authorization": f"Bearer {env['admin_token']}"}

    payload = {
        "id_proveedor": env["id_proveedor"],
        "detalles": [
            {"id_variante": env["id_variante"], "cantidad_pedida": 20, "costo_pactado": 14.50}
        ]
    }
    resp = await client.post("/api/compras/ordenes", json=payload, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["estado"] == "Emitida"
    assert float(data["total_estimado"]) == 290.0
    assert data["id_proveedor"] == env["id_proveedor"]


@pytest.mark.asyncio
async def test_emitir_orden_api_403_cajera(client, db_session):
    env = await seed_compras_api_env(db_session)
    headers = {"Authorization": f"Bearer {env['cajera_token']}"}

    payload = {
        "id_proveedor": env["id_proveedor"],
        "detalles": [
            {"id_variante": env["id_variante"], "cantidad_pedida": 10, "costo_pactado": 15.00}
        ]
    }
    resp = await client.post("/api/compras/ordenes", json=payload, headers=headers)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_listar_ordenes_api_con_filtros(client, db_session):
    env = await seed_compras_api_env(db_session)
    headers = {"Authorization": f"Bearer {env['admin_token']}"}

    # Emitir orden 1
    p1 = {
        "id_proveedor": env["id_proveedor"],
        "detalles": [{"id_variante": env["id_variante"], "cantidad_pedida": 5, "costo_pactado": 10.0}]
    }
    r1 = await client.post("/api/compras/ordenes", json=p1, headers=headers)
    id1 = r1.json()["id_orden"]

    # Emitir orden 2
    p2 = {
        "id_proveedor": env["id_proveedor"],
        "detalles": [{"id_variante": env["id_variante"], "cantidad_pedida": 8, "costo_pactado": 12.0}]
    }
    r2 = await client.post("/api/compras/ordenes", json=p2, headers=headers)
    id2 = r2.json()["id_orden"]

    # Cancelar orden 2
    r_cancel = await client.post(f"/api/compras/ordenes/{id2}/cancelar", json={"motivo": "Cancelado por prueba"}, headers=headers)
    assert r_cancel.status_code == 200
    assert r_cancel.json()["estado"] == "Cancelada"

    # Listar Emitidas
    resp_emitidas = await client.get("/api/compras/ordenes?estado=Emitida", headers=headers)
    assert resp_emitidas.status_code == 200
    ids_emitidas = [o["id_orden"] for o in resp_emitidas.json()]
    assert id1 in ids_emitidas
    assert id2 not in ids_emitidas

    # Listar Canceladas
    resp_canceladas = await client.get("/api/compras/ordenes?estado=Cancelada", headers=headers)
    assert resp_canceladas.status_code == 200
    ids_canceladas = [o["id_orden"] for o in resp_canceladas.json()]
    assert id2 in ids_canceladas
    assert id1 not in ids_canceladas


@pytest.mark.asyncio
async def test_recibir_orden_api_exito_bodega(client, db_session):
    env = await seed_compras_api_env(db_session)
    admin_headers = {"Authorization": f"Bearer {env['admin_token']}"}
    bodega_headers = {"Authorization": f"Bearer {env['bodega_token']}"}

    # Admin emite orden
    p = {
        "id_proveedor": env["id_proveedor"],
        "detalles": [{"id_variante": env["id_variante"], "cantidad_pedida": 15, "costo_pactado": 15.0}]
    }
    r_emit = await client.post("/api/compras/ordenes", json=p, headers=admin_headers)
    id_orden = r_emit.json()["id_orden"]

    # Bodega recibe orden
    ingreso_payload = {
        "id_orden": id_orden,
        "id_proveedor": env["id_proveedor"],
        "numero_factura_proveedor": "FAC-TEST-001",
        "gasto_flete": 20.0,
        "gasto_cargadores": 10.0,
        "detalles": [
            {"id_variante": env["id_variante"], "cantidad_recibida": 15, "costo_unitario": 15.0, "id_sucursal": 1}
        ]
    }
    r_ing = await client.post("/api/compras/ingreso", json=ingreso_payload, headers=bodega_headers)
    assert r_ing.status_code == 201

    # Verificar que el stock subió de 10 a 25
    inv = await db_session.get(InventarioSucursal, 1)
    assert inv.stock_actual == 25

    # Verificar estado de orden actualizado a Recibida
    r_ord = await client.get(f"/api/compras/ordenes/{id_orden}", headers=bodega_headers)
    assert r_ord.status_code == 200
    assert r_ord.json()["estado"] == "Recibida"


@pytest.mark.asyncio
async def test_recibir_orden_api_403_cajera(client, db_session):
    env = await seed_compras_api_env(db_session)
    cajera_headers = {"Authorization": f"Bearer {env['cajera_token']}"}

    ingreso_payload = {
        "id_orden": 1,
        "id_proveedor": env["id_proveedor"],
        "numero_factura_proveedor": "FAC-TEST-403",
        "detalles": [
            {"id_variante": env["id_variante"], "cantidad_recibida": 5, "costo_unitario": 15.0}
        ]
    }
    resp = await client.post("/api/compras/ingreso", json=ingreso_payload, headers=cajera_headers)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_cancelar_orden_api_403_bodega(client, db_session):
    env = await seed_compras_api_env(db_session)
    admin_headers = {"Authorization": f"Bearer {env['admin_token']}"}
    bodega_headers = {"Authorization": f"Bearer {env['bodega_token']}"}

    p = {
        "id_proveedor": env["id_proveedor"],
        "detalles": [{"id_variante": env["id_variante"], "cantidad_pedida": 5, "costo_pactado": 10.0}]
    }
    r_emit = await client.post("/api/compras/ordenes", json=p, headers=admin_headers)
    id_orden = r_emit.json()["id_orden"]

    # Bodega intenta cancelar orden
    r_cancel = await client.post(f"/api/compras/ordenes/{id_orden}/cancelar", json={}, headers=bodega_headers)
    assert r_cancel.status_code == 403


@pytest.mark.asyncio
async def test_cancelar_orden_ya_recibida_api_400(client, db_session):
    env = await seed_compras_api_env(db_session)
    admin_headers = {"Authorization": f"Bearer {env['admin_token']}"}

    # Emitir y recibir
    p = {
        "id_proveedor": env["id_proveedor"],
        "detalles": [{"id_variante": env["id_variante"], "cantidad_pedida": 5, "costo_pactado": 10.0}]
    }
    r_emit = await client.post("/api/compras/ordenes", json=p, headers=admin_headers)
    id_orden = r_emit.json()["id_orden"]

    ingreso_payload = {
        "id_orden": id_orden,
        "id_proveedor": env["id_proveedor"],
        "numero_factura_proveedor": "FAC-TEST-REC",
        "detalles": [
            {"id_variante": env["id_variante"], "cantidad_recibida": 5, "costo_unitario": 10.0}
        ]
    }
    await client.post("/api/compras/ingreso", json=ingreso_payload, headers=admin_headers)

    # Intentar cancelar la orden recibida
    r_cancel = await client.post(f"/api/compras/ordenes/{id_orden}/cancelar", json={}, headers=admin_headers)
    assert r_cancel.status_code == 400
    assert "No se puede cancelar" in r_cancel.json()["detail"]
