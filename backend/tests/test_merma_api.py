import pytest
from decimal import Decimal
from datetime import datetime
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.database import get_db
from app.core import security
from app.db.models import (
    Rol, Usuario, Permiso, RolPermiso, Sucursal, Categoria, Subcategoria, UnidadMedida,
    Producto, VarianteProducto, InventarioSucursal, MotivoMerma, BitacoraAuditoria
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


async def seed_merma_env(db_session):
    # Permiso
    perm_inv = Permiso(id_permiso=3, modulo="Inventario", codigo="INV_INGRESAR_MERCADERIA", descripcion="Ingreso")
    perm_venta = Permiso(id_permiso=1, modulo="Ventas", codigo="VENTA_COBRAR", descripcion="Cobro")
    db_session.add_all([perm_inv, perm_venta])
    await db_session.flush()

    # Roles
    rol_admin = Rol(id_rol=1, nombre="Administradora", estado="Activo")
    rol_bodega = Rol(id_rol=2, nombre="Bodeguero", estado="Activo")
    rol_cajera = Rol(id_rol=3, nombre="Cajera", estado="Activo")
    db_session.add_all([rol_admin, rol_bodega, rol_cajera])
    await db_session.flush()

    # Rol Permisos
    db_session.add_all([
        RolPermiso(id_rol=1, id_permiso=3),
        RolPermiso(id_rol=1, id_permiso=1),
        RolPermiso(id_rol=2, id_permiso=3),
        RolPermiso(id_rol=3, id_permiso=1),
    ])
    await db_session.flush()

    # Usuarios
    user_admin = Usuario(
        id_usuario=1, id_rol=rol_admin.id_rol, nombre_completo="Admin Test",
        username="admin_merma", password_hash=security.get_password_hash("pass123"), estado="Activo"
    )
    user_bodega = Usuario(
        id_usuario=2, id_rol=rol_bodega.id_rol, nombre_completo="Bodeguero Test",
        username="bodega_merma", password_hash=security.get_password_hash("pass123"), estado="Activo"
    )
    user_cajera = Usuario(
        id_usuario=3, id_rol=rol_cajera.id_rol, nombre_completo="Cajera Test",
        username="cajera_merma", password_hash=security.get_password_hash("pass123"), estado="Activo"
    )
    db_session.add_all([user_admin, user_bodega, user_cajera])

    # Sucursal, Catalogo, Producto, Variante, Inventario
    suc = Sucursal(id_sucursal=1, nombre="Central Merma", direccion="Dir Central", telefono="12345678", estado="Activa")
    cat = Categoria(id_categoria=1, nombre="Oficina", estado="Activo")
    sub = Subcategoria(id_subcategoria=1, id_categoria=1, nombre="Papelería")
    und = UnidadMedida(id_unidad=1, codigo="UND", descripcion="Unidad")
    mot1 = MotivoMerma(id_motivo=1, descripcion="Dañado por lluvia")
    mot2 = MotivoMerma(id_motivo=2, descripcion="Vencido")

    db_session.add_all([suc, cat, sub, und, mot1, mot2])
    await db_session.flush()

    prod = Producto(id_producto=1, id_subcategoria=1, id_unidad=1, nombre="Resma de Papel", estado="Activo")
    db_session.add(prod)
    await db_session.flush()

    var = VarianteProducto(
        id_variante=1, id_producto=1, codigo_barras="74010001",
        precio_detalle=Decimal("40.00"), precio_mayoreo=Decimal("35.00"), costo_promedio=Decimal("25.00")
    )
    db_session.add(var)
    await db_session.flush()

    inv = InventarioSucursal(
        id_inventario=1, id_variante=1, id_sucursal=1, stock_actual=30, stock_minimo=5
    )
    db_session.add(inv)
    await db_session.commit()

    token_admin = security.create_access_token(
        data={"sub": user_admin.username, "role": "Administradora", "permissions": ["INV_INGRESAR_MERCADERIA", "VENTA_COBRAR"]}
    )
    token_bodega = security.create_access_token(
        data={"sub": user_bodega.username, "role": "Bodeguero", "permissions": ["INV_INGRESAR_MERCADERIA"]}
    )
    token_cajera = security.create_access_token(
        data={"sub": user_cajera.username, "role": "Cajera", "permissions": ["VENTA_COBRAR"]}
    )

    return {
        "admin": {"Authorization": f"Bearer {token_admin}"},
        "bodega": {"Authorization": f"Bearer {token_bodega}"},
        "cajera": {"Authorization": f"Bearer {token_cajera}"},
    }


@pytest.mark.asyncio
async def test_get_motivos_merma_api(client, db_session):
    headers = await seed_merma_env(db_session)
    res = await client.get("/api/mermas/motivos", headers=headers["bodega"])
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 2
    assert any(m["descripcion"] == "Dañado por lluvia" for m in data)


@pytest.mark.asyncio
async def test_get_motivos_merma_403_cajera(client, db_session):
    headers = await seed_merma_env(db_session)
    res = await client.get("/api/mermas/motivos", headers=headers["cajera"])
    assert res.status_code == 403
    assert "INV_INGRESAR_MERCADERIA" in res.json()["detail"]


@pytest.mark.asyncio
async def test_create_merma_api_success(client, db_session):
    headers = await seed_merma_env(db_session)
    payload = {
        "id_sucursal": 1,
        "observaciones": "Merma por humedad en bodega",
        "detalles": [
            {"id_variante": 1, "id_motivo": 1, "cantidad": 4}
        ]
    }
    res = await client.post("/api/mermas", json=payload, headers=headers["bodega"])
    assert res.status_code == 201
    data = res.json()
    assert data["id_merma"] is not None
    assert Decimal(str(data["costo_total_perdida"])) == Decimal("100.00")  # 4 * Q25.00
    assert data["nombre_sucursal"] == "Central Merma"

    # Verificar bitácora
    audit = await db_session.execute(
        select(BitacoraAuditoria).where(BitacoraAuditoria.tabla_afectada == "merma")
    )
    logs = audit.scalars().all()
    assert len(logs) == 1
    assert logs[0].accion == "CREAR"


@pytest.mark.asyncio
async def test_create_merma_api_stock_insuficiente(client, db_session):
    headers = await seed_merma_env(db_session)
    payload = {
        "id_sucursal": 1,
        "observaciones": "Intento de merma excedida",
        "detalles": [
            {"id_variante": 1, "id_motivo": 1, "cantidad": 50}  # Stock es 30
        ]
    }
    res = await client.post("/api/mermas", json=payload, headers=headers["bodega"])
    assert res.status_code == 400
    assert "Stock insuficiente" in res.json()["detail"]


@pytest.mark.asyncio
async def test_create_merma_api_403_cajera(client, db_session):
    headers = await seed_merma_env(db_session)
    payload = {
        "id_sucursal": 1,
        "detalles": [{"id_variante": 1, "id_motivo": 1, "cantidad": 1}]
    }
    res = await client.post("/api/mermas", json=payload, headers=headers["cajera"])
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_list_mermas_api_with_filters(client, db_session):
    headers = await seed_merma_env(db_session)
    # Crear merma 1
    await client.post("/api/mermas", json={
        "id_sucursal": 1,
        "observaciones": "Merma 1",
        "detalles": [{"id_variante": 1, "id_motivo": 1, "cantidad": 2}]
    }, headers=headers["admin"])

    # Crear merma 2
    await client.post("/api/mermas", json={
        "id_sucursal": 1,
        "observaciones": "Merma 2",
        "detalles": [{"id_variante": 1, "id_motivo": 2, "cantidad": 3}]
    }, headers=headers["admin"])

    # Filtrar por motivo 1
    res1 = await client.get("/api/mermas?id_motivo=1", headers=headers["admin"])
    assert res1.status_code == 200
    d1 = res1.json()
    assert d1["total"] == 1
    assert d1["items"][0]["detalles"][0]["id_motivo"] == 1

    # Filtrar por motivo 2
    res2 = await client.get("/api/mermas?id_motivo=2", headers=headers["admin"])
    assert res2.status_code == 200
    d2 = res2.json()
    assert d2["total"] == 1
    assert d2["items"][0]["detalles"][0]["id_motivo"] == 2

    # Cajera sin permiso -> 403
    res_caj = await client.get("/api/mermas", headers=headers["cajera"])
    assert res_caj.status_code == 403
