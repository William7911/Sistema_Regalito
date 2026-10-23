import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.database import get_db
from app.core import security
from app.db.models import Rol, Usuario, Permiso, RolPermiso, Municipio


@pytest.fixture
async def client(db_session):
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c
    app.dependency_overrides.clear()


async def seed_catalogo_admin_auth(db_session):
    rol = Rol(nombre="Administradora-B3", estado="Activo")
    db_session.add(rol)
    await db_session.flush()
    user = Usuario(
        id_rol=rol.id_rol,
        nombre_completo="Admin B3",
        username="admin_b3",
        password_hash=security.get_password_hash("pass123"),
        estado="Activo",
    )
    db_session.add(user)
    permiso = Permiso(modulo="Catálogos", codigo="CATALOGO_ADMIN", descripcion="Gestión de catálogos")
    db_session.add(permiso)
    await db_session.flush()
    db_session.add(RolPermiso(id_rol=rol.id_rol, id_permiso=permiso.id_permiso))
    await db_session.commit()
    token = security.create_access_token(
        data={"sub": user.username, "role": "Administradora", "permissions": ["CATALOGO_ADMIN"]}
    )
    return {"Authorization": f"Bearer {token}"}


async def seed_non_admin_auth(db_session):
    rol = Rol(nombre="Cajera-B3", estado="Activo")
    db_session.add(rol)
    await db_session.flush()
    user = Usuario(
        id_rol=rol.id_rol,
        nombre_completo="Cajera B3",
        username="cajera_b3",
        password_hash=security.get_password_hash("pass123"),
        estado="Activo",
    )
    db_session.add(user)
    await db_session.commit()
    token = security.create_access_token(
        data={"sub": user.username, "role": "Cajera", "permissions": []}
    )
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# LECTURA de combos para usuarios NO admin (pendiente 1 aplicado al Bloque 3)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_combos_bloque3_cargan_para_usuario_no_admin(client, db_session):
    headers = await seed_non_admin_auth(db_session)
    combos = [
        "/api/catalogos/motivos-merma",
        "/api/catalogos/metodos-pago",
        "/api/catalogos/proveedores",
        "/api/catalogos/departamentos",
        "/api/catalogos/municipios",
    ]
    for url in combos:
        res = await client.get(url, headers=headers)
        assert res.status_code == 200, f"{url} debería responder 200 para no-admin, obtuvo {res.status_code}"


@pytest.mark.asyncio
async def test_crud_bloque3_rechazado_403_para_usuario_no_admin(client, db_session):
    headers = await seed_non_admin_auth(db_session)
    cases = [
        ("/api/catalogos/motivos-merma", {"descripcion": "X"}),
        ("/api/catalogos/metodos-pago", {"nombre": "Y"}),
        ("/api/catalogos/proveedores", {"nombre_contacto": "A", "distribuidora": "B"}),
        ("/api/catalogos/departamentos", {"nombre": "Z"}),
        ("/api/catalogos/municipios", {"id_departamento": 1, "nombre": "W"}),
    ]
    for url, payload in cases:
        res = await client.post(url, headers=headers, json=payload)
        assert res.status_code == 403, f"POST {url} debería dar 403, obtuvo {res.status_code}"


# ---------------------------------------------------------------------------
# MOTIVOS DE MERMA API
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_crud_motivo_merma_api(client, db_session):
    headers = await seed_catalogo_admin_auth(db_session)

    res = await client.post("/api/catalogos/motivos-merma", headers=headers,
                            json={"descripcion": "Daño en transporte"})
    assert res.status_code == 201
    id_motivo = res.json()["id_motivo"]
    assert res.json()["estado"] == "Activo"

    # Duplicado (case-insensitive)
    res_dup = await client.post("/api/catalogos/motivos-merma", headers=headers,
                                json={"descripcion": "daño en transporte"})
    assert res_dup.status_code == 400

    # Ficha
    res_get = await client.get(f"/api/catalogos/motivos-merma/{id_motivo}", headers=headers)
    assert res_get.status_code == 200

    # Actualizar
    res_put = await client.put(f"/api/catalogos/motivos-merma/{id_motivo}", headers=headers,
                               json={"descripcion": "Daño en transporte actualizado"})
    assert res_put.status_code == 200

    # Desactivar
    res_del = await client.delete(f"/api/catalogos/motivos-merma/{id_motivo}", headers=headers)
    assert res_del.status_code == 200
    assert res_del.json()["estado"] == "Inactivo"

    # Exportaciones
    res_csv = await client.get("/api/catalogos/motivos-merma/export?format=csv", headers=headers)
    assert res_csv.status_code == 200
    assert "text/csv" in res_csv.headers["content-type"]


# ---------------------------------------------------------------------------
# MÉTODOS DE PAGO API
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_crud_metodo_pago_api(client, db_session):
    headers = await seed_catalogo_admin_auth(db_session)

    res = await client.post("/api/catalogos/metodos-pago", headers=headers,
                            json={"nombre": "Bitcoin"})
    assert res.status_code == 201
    id_metodo = res.json()["id_metodo_pago"]

    res_dup = await client.post("/api/catalogos/metodos-pago", headers=headers,
                                json={"nombre": "bitcoin"})
    assert res_dup.status_code == 400

    res_del = await client.delete(f"/api/catalogos/metodos-pago/{id_metodo}", headers=headers)
    assert res_del.status_code == 200
    assert res_del.json()["estado"] == "Inactivo"

    res_activar = await client.post(f"/api/catalogos/metodos-pago/{id_metodo}/activar", headers=headers)
    assert res_activar.status_code == 200
    assert res_activar.json()["estado"] == "Activo"


# ---------------------------------------------------------------------------
# PROVEEDORES API
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_crud_proveedor_api(client, db_session):
    headers = await seed_catalogo_admin_auth(db_session)

    res = await client.post("/api/catalogos/proveedores", headers=headers, json={
        "nombre_contacto": "Karen",
        "distribuidora": "Distribuidora del Valle",
        "telefono": "5566-7788",
        "correo": "info@delvalle.gt",
    })
    assert res.status_code == 201
    id_prov = res.json()["id_proveedor"]
    assert res.json()["distribuidora"] == "Distribuidora del Valle"

    res_dup = await client.post("/api/catalogos/proveedores", headers=headers, json={
        "nombre_contacto": "Otro",
        "distribuidora": "distribuidora del valle",
    })
    assert res_dup.status_code == 400

    # Filtros y ordenamiento por fecha
    res_paged = await client.get("/api/catalogos/proveedores/paged?search=valle&limit=10", headers=headers)
    assert res_paged.status_code == 200
    assert res_paged.json()["total"] >= 1

    res_del = await client.delete(f"/api/catalogos/proveedores/{id_prov}", headers=headers)
    assert res_del.status_code == 200
    assert res_del.json()["estado"] == "Inactivo"

    res_xlsx = await client.get("/api/catalogos/proveedores/export?format=excel", headers=headers)
    assert res_xlsx.status_code == 200
    assert "spreadsheetml" in res_xlsx.headers["content-type"]


# ---------------------------------------------------------------------------
# DEPARTAMENTOS API
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_crud_departamento_api_y_desactivacion_segura(client, db_session):
    headers = await seed_catalogo_admin_auth(db_session)

    res = await client.post("/api/catalogos/departamentos", headers=headers,
                            json={"nombre": "Depto Test B3"})
    assert res.status_code == 201
    id_dep = res.json()["id_departamento"]

    # Municipio activo dependiente bloquea la desactivación
    muni = Municipio(id_departamento=id_dep, nombre="Muni Test", estado="Activo")
    db_session.add(muni)
    await db_session.commit()

    res_del = await client.delete(f"/api/catalogos/departamentos/{id_dep}", headers=headers)
    assert res_del.status_code == 400
    assert "municipio" in res_del.json()["detail"].lower()

    # Sin dependencias activas sí se desactiva
    muni.estado = "Inactivo"
    await db_session.commit()
    res_del2 = await client.delete(f"/api/catalogos/departamentos/{id_dep}", headers=headers)
    assert res_del2.status_code == 200
    assert res_del2.json()["estado"] == "Inactivo"


# ---------------------------------------------------------------------------
# MUNICIPIOS API
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_crud_municipio_api_y_dropdown(client, db_session):
    headers = await seed_catalogo_admin_auth(db_session)

    res_dep = await client.post("/api/catalogos/departamentos", headers=headers,
                                json={"nombre": "Depto Para Municipios"})
    id_dep = res_dep.json()["id_departamento"]

    res = await client.post("/api/catalogos/municipios", headers=headers,
                            json={"id_departamento": id_dep, "nombre": "Municipio Test"})
    assert res.status_code == 201
    id_muni = res.json()["id_municipio"]

    res_dup = await client.post("/api/catalogos/municipios", headers=headers,
                                json={"id_departamento": id_dep, "nombre": "municipio test"})
    assert res_dup.status_code == 400

    # Dropdown dependiente (lectura no admin)
    headers_no_admin = await seed_non_admin_auth(db_session)
    res_combo = await client.get(f"/api/catalogos/municipios?id_departamento={id_dep}",
                                 headers=headers_no_admin)
    assert res_combo.status_code == 200
    assert any(m["nombre"] == "Municipio Test" for m in res_combo.json())

    # Desactivar con admin
    res_del = await client.delete(f"/api/catalogos/municipios/{id_muni}", headers=headers)
    assert res_del.status_code == 200
    assert res_del.json()["estado"] == "Inactivo"