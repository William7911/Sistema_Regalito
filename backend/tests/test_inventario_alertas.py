"""
Pruebas del endpoint GET /api/inventario/alertas (campanita de notificaciones):
  1. Sin token -> 401.
  2. Autenticado -> 200 con SOLO alertas estado 'Pendiente' enriquecidas con el
     nombre del producto (JOIN alerta_stock → inventario_sucursal →
     variante_producto → producto).
"""
import pytest
from datetime import datetime
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.db.database import get_db
from app.api.deps import get_current_user
from app.db.models import (
    Usuario,
    Rol,
    Permiso,
    RolPermiso,
    Categoria,
    Subcategoria,
    UnidadMedida,
    Producto,
    VarianteProducto,
    InventarioSucursal,
    AlertaStock,
    BitacoraAuditoria,
)
from sqlalchemy import select


pytestmark = pytest.mark.asyncio


@pytest.fixture
async def client(db_session):
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c
    app.dependency_overrides.clear()


async def _seed_alertas(db):
    cat = Categoria(id_categoria=1, nombre="Cat1", estado="Activo")
    db.add(cat)
    await db.flush()

    subcat = Subcategoria(id_subcategoria=1, id_categoria=1, nombre="SubCat1")
    db.add(subcat)
    await db.flush()

    unidad = UnidadMedida(id_unidad=1, codigo="U", descripcion="Unidad")
    db.add(unidad)
    await db.flush()

    producto = Producto(id_producto=1, id_subcategoria=1, id_unidad=1, nombre="Producto A", estado="Activo")
    db.add(producto)
    await db.flush()

    variante = VarianteProducto(id_variante=1, id_producto=1, codigo_barras="123", precio_detalle=10, precio_mayoreo=8, costo_promedio=5)
    db.add(variante)
    await db.flush()

    inv = InventarioSucursal(id_inventario=1, id_variante=1, id_sucursal=1, stock_actual=4, stock_minimo=5)
    db.add(inv)
    await db.flush()

    db.add(AlertaStock(id_inventario=1, mensaje="Producto A por debajo del stock mínimo", fecha_generacion=datetime.utcnow(), estado="Pendiente"))
    db.add(AlertaStock(id_inventario=1, mensaje="Producto A por debajo del stock mínimo", fecha_generacion=datetime.utcnow(), estado="Atendida"))
    await db.commit()


async def test_inventario_alertas_requires_auth(client):
    response = await client.get("/api/inventario/alertas")
    assert response.status_code == 401


async def test_inventario_alertas_devuelve_solo_pendientes(client, db_session):
    await _seed_alertas(db_session)
    admin_user = Usuario(
        id_usuario=1, id_rol=1, nombre_completo="Administrador",
        username="admin", password_hash="x", estado="Activo",
    )
    app.dependency_overrides[get_current_user] = lambda: admin_user

    response = await client.get("/api/inventario/alertas")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["estado"] == "Pendiente"
    assert data[0]["producto_nombre"] == "Producto A"
    assert data[0]["variante_sku"] == "123"
    assert data[0]["stock_actual"] == 4
    assert data[0]["stock_minimo"] == 5


async def test_atender_alerta_exitosa_y_registra_bitacora(client, db_session):
    await _seed_alertas(db_session)
    # Rol y permiso para bodeguero
    perm = Permiso(id_permiso=3, modulo="Inventario", codigo="INV_INGRESAR_MERCADERIA", descripcion="Ingreso")
    rol_bodega = Rol(id_rol=3, nombre="Bodeguero", estado="Activo")
    db_session.add_all([perm, rol_bodega])
    await db_session.flush()

    db_session.add(RolPermiso(id_rol=3, id_permiso=3))
    user_bodega = Usuario(
        id_usuario=10, id_rol=3, nombre_completo="Bodeguero 10",
        username="bodega10", password_hash="x", estado="Activo"
    )
    db_session.add(user_bodega)
    await db_session.commit()

    from app.core import security
    token = security.create_access_token(
        data={"sub": user_bodega.username, "role": "Bodeguero", "permissions": ["INV_INGRESAR_MERCADERIA"]}
    )
    headers = {"Authorization": f"Bearer {token}"}

    # Atender alerta con ID 1
    res = await client.put("/api/inventario/alertas/1/atender", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["id_alerta"] == 1
    assert data["estado"] == "Atendida"

    # Verificar que ya no aparece como pendiente
    app.dependency_overrides[get_current_user] = lambda: user_bodega
    res_pendientes = await client.get("/api/inventario/alertas", headers=headers)
    assert res_pendientes.status_code == 200
    assert len(res_pendientes.json()) == 0

    # Verificar bitácora
    audit = await db_session.execute(
        select(BitacoraAuditoria).where(BitacoraAuditoria.tabla_afectada == "alerta_stock")
    )
    logs = audit.scalars().all()
    assert len(logs) == 1
    assert logs[0].accion == "EDITAR"
    assert "Marcó como atendida" in logs[0].descripcion


async def test_atender_alerta_403_cajera(client, db_session):
    await _seed_alertas(db_session)
    rol_cajera = Rol(id_rol=2, nombre="Cajera", estado="Activo")
    db_session.add(rol_cajera)
    await db_session.flush()

    user_cajera = Usuario(
        id_usuario=20, id_rol=2, nombre_completo="Cajera 20",
        username="cajera20", password_hash="x", estado="Activo"
    )
    db_session.add(user_cajera)
    await db_session.commit()

    from app.core import security
    token = security.create_access_token(
        data={"sub": user_cajera.username, "role": "Cajera", "permissions": ["VENTA_COBRAR"]}
    )
    headers = {"Authorization": f"Bearer {token}"}

    res = await client.put("/api/inventario/alertas/1/atender", headers=headers)
    assert res.status_code == 403
    assert "INV_INGRESAR_MERCADERIA" in res.json()["detail"]


async def test_atender_alerta_404_no_existe(client, db_session):
    rol_admin = Rol(id_rol=1, nombre="Administradora", estado="Activo")
    perm = Permiso(id_permiso=3, modulo="Inventario", codigo="INV_INGRESAR_MERCADERIA", descripcion="Ingreso")
    db_session.add_all([rol_admin, perm])
    await db_session.flush()
    db_session.add(RolPermiso(id_rol=1, id_permiso=3))

    user_admin = Usuario(
        id_usuario=1, id_rol=1, nombre_completo="Admin",
        username="admin_test", password_hash="x", estado="Activo"
    )
    db_session.add(user_admin)
    await db_session.commit()

    from app.core import security
    token = security.create_access_token(
        data={"sub": user_admin.username, "role": "Administradora", "permissions": ["INV_INGRESAR_MERCADERIA"]}
    )
    headers = {"Authorization": f"Bearer {token}"}

    res = await client.put("/api/inventario/alertas/9999/atender", headers=headers)
    assert res.status_code == 404
