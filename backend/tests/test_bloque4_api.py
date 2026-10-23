import pytest
from sqlalchemy import select
from datetime import datetime
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.database import get_db
from app.core import security
from app.db.models import Rol, Usuario, Permiso, BitacoraAuditoria


@pytest.fixture
async def client(db_session):
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c
    app.dependency_overrides.clear()


async def seed_admin_auth(db_session, username="admin_b4"):
    rol = Rol(nombre="Administradora", estado="Activo")
    db_session.add(rol)
    await db_session.flush()
    user = Usuario(
        id_rol=rol.id_rol, nombre_completo="Admin Bloque 4", username=username,
        password_hash=security.get_password_hash("pass123"), estado="Activo",
    )
    db_session.add(user)
    await db_session.commit()
    token = security.create_access_token(
        data={"sub": user.username, "role": "Administradora", "permissions": ["BITACORA_CONSULTAR"]}
    )
    return {"Authorization": f"Bearer {token}"}


async def seed_non_admin_auth(db_session, role_name="Cajera", username="cajera_b4"):
    rol = Rol(nombre=role_name, estado="Activo")
    db_session.add(rol)
    await db_session.flush()
    user = Usuario(
        id_rol=rol.id_rol, nombre_completo=f"{role_name} Demo", username=username,
        password_hash=security.get_password_hash("pass123"), estado="Activo",
    )
    db_session.add(user)
    await db_session.commit()
    token = security.create_access_token(data={"sub": user.username, "role": role_name, "permissions": []})
    return {"Authorization": f"Bearer {token}"}


async def get_user_by_username(db_session, username):
    res = await db_session.execute(select(Usuario).where(Usuario.username == username))
    return res.scalar_one()


# ---------------------------------------------------------------------------
# PERMISOS / ROL-PERMISO
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_listar_permisos_api(client, db_session):
    headers = await seed_admin_auth(db_session)
    p1 = Permiso(modulo="Seguridad", codigo="BITACORA_CONSULTAR", descripcion="Ver bitácora")
    p2 = Permiso(modulo="Catálogo", codigo="CATALOGO_ADMIN", descripcion="Catálogo")
    db_session.add_all([p1, p2])
    await db_session.commit()

    res = await client.get("/api/roles/permisos/catalogo", headers=headers)
    assert res.status_code == 200
    codigos = [p["codigo"] for p in res.json()]
    assert "BITACORA_CONSULTAR" in codigos
    assert "CATALOGO_ADMIN" in codigos
    assert all("modulo" in p for p in res.json())


@pytest.mark.asyncio
async def test_get_y_update_permisos_rol_api(client, db_session):
    headers = await seed_admin_auth(db_session)

    rol = Rol(nombre="Cajero B4", estado="Activo")
    db_session.add(rol)
    await db_session.flush()
    p1 = Permiso(modulo="Ventas", codigo="VENTA_COBRAR", descripcion="cobrar")
    p2 = Permiso(modulo="Ventas", codigo="VENTA_APLICAR_DESCUENTO", descripcion="descuento")
    p3 = Permiso(modulo="Compras", codigo="COMPRA_EMITIR_ORDEN", descripcion="compras")
    db_session.add_all([p1, p2, p3])
    await db_session.commit()

    # Inicialmente sin permisos
    res = await client.get(f"/api/roles/{rol.id_rol}/permisos", headers=headers)
    assert res.status_code == 200
    assert res.json() == []

    # Asignar permisos (reemplazo)
    res = await client.put(
        f"/api/roles/{rol.id_rol}/permisos",
        headers=headers,
        json={"codigos": ["VENTA_COBRAR", "COMPRA_EMITIR_ORDEN"]},
    )
    assert res.status_code == 200
    assert sorted(res.json()) == ["COMPRA_EMITIR_ORDEN", "VENTA_COBRAR"]

    res = await client.get(f"/api/roles/{rol.id_rol}/permisos", headers=headers)
    assert sorted(res.json()) == ["COMPRA_EMITIR_ORDEN", "VENTA_COBRAR"]

    # Limpiar y reemplazar con uno solo
    res = await client.put(
        f"/api/roles/{rol.id_rol}/permisos", headers=headers, json={"codigos": ["VENTA_APLICAR_DESCUENTO"]}
    )
    assert res.status_code == 200
    assert res.json() == ["VENTA_APLICAR_DESCUENTO"]


@pytest.mark.asyncio
async def test_update_permisos_rol_inexistente_api_404(client, db_session):
    headers = await seed_admin_auth(db_session)
    res = await client.put("/api/roles/9999/permisos", headers=headers, json={"codigos": ["VENTA_COBRAR"]})
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_update_permisos_codigo_inexistente_api_400(client, db_session):
    headers = await seed_admin_auth(db_session)
    rol = Rol(nombre="Rol 400 B4", estado="Activo")
    db_session.add(rol)
    await db_session.commit()
    res = await client.put(f"/api/roles/{rol.id_rol}/permisos", headers=headers, json={"codigos": ["NO_EXISTE"]})
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_permisos_rol_api_403_sin_admin(client, db_session):
    headers = await seed_non_admin_auth(db_session)
    rol = Rol(nombre="Rol X", estado="Activo")
    db_session.add(rol)
    await db_session.commit()

    res = await client.get(f"/api/roles/{rol.id_rol}/permisos", headers=headers)
    assert res.status_code == 403
    res = await client.put(f"/api/roles/{rol.id_rol}/permisos", headers=headers, json={"codigos": ["VENTA_COBRAR"]})
    assert res.status_code == 403


# ---------------------------------------------------------------------------
# BITÁCORA DE AUDITORÍA
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_bitacora_api_403_sin_permiso(client, db_session):
    headers = await seed_non_admin_auth(db_session)
    res = await client.get("/api/bitacora", headers=headers)
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_bitacora_api_lee_registros_con_filtros(client, db_session):
    headers = await seed_admin_auth(db_session)

    user = await get_user_by_username(db_session, "admin_b4")
    db_session.add_all([
        BitacoraAuditoria(id_usuario=user.id_usuario, tabla_afectada="usuario", accion="CREATE",
                          descripcion="Creó usuario 'a'", fecha_hora=datetime(2026, 10, 1, 10, 0, 0)),
        BitacoraAuditoria(id_usuario=user.id_usuario, tabla_afectada="categoria", accion="UPDATE",
                          descripcion="Editó categoría X", fecha_hora=datetime(2026, 10, 2, 11, 0, 0)),
        BitacoraAuditoria(id_usuario=user.id_usuario, tabla_afectada="producto", accion="PRECIO",
                          descripcion="Cambió precio", fecha_hora=datetime(2026, 10, 3, 9, 0, 0)),
    ])
    await db_session.commit()

    # Sin filtros
    res = await client.get("/api/bitacora", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3
    assert data["items"][0]["usuario_nombre"] == "Admin Bloque 4"

    # Filtro por tabla
    res = await client.get("/api/bitacora", headers=headers, params={"tabla": "categor"})
    data = res.json()
    assert data["total"] == 1
    assert data["items"][0]["tabla_afectada"] == "categoria"

    # Filtro por acción
    res = await client.get("/api/bitacora", headers=headers, params={"accion": "PRECIO"})
    data = res.json()
    assert data["total"] == 1
    assert data["items"][0]["accion"] == "PRECIO"

    # Filtro por rango de fechas
    res = await client.get(
        "/api/bitacora", headers=headers,
        params={"fecha_desde": "2026-10-02", "fecha_hasta": "2026-10-03"},
    )
    data = res.json()
    assert data["total"] == 2

    # Filtro por usuario
    res = await client.get("/api/bitacora", headers=headers, params={"id_usuario": user.id_usuario})
    data = res.json()
    assert data["total"] == 3


@pytest.mark.asyncio
async def test_bitacora_api_es_solo_lectura(client, db_session):
    headers = await seed_admin_auth(db_session)
    # No existe endpoint de escritura; un POST debe responder 405/404 pero nunca insertar.
    res = await client.post("/api/bitacora", headers=headers, json={})
    assert res.status_code in (405, 404)
