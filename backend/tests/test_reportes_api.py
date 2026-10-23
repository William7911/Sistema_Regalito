import pytest
from httpx import AsyncClient, ASGITransport
from datetime import date, datetime

from app.main import app
from app.db.database import get_db
from app.core import security
from app.db.models import Rol, Usuario, Permiso, RolPermiso, TipoCliente, Cliente, ClienteContacto, DepartamentoGeografico, Municipio


@pytest.fixture
async def client(db_session):
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c
    app.dependency_overrides.clear()


async def setup_reportes_api_data(db_session):
    p_rep = Permiso(id_permiso=9, modulo="Reportes", codigo="REPORTE_VER", descripcion="Ver reportes")
    db_session.add(p_rep)
    await db_session.flush()

    rol_admin = Rol(id_rol=1, nombre="Administradora", estado="Activo")
    rol_cajera = Rol(id_rol=2, nombre="Cajera", estado="Activo")
    db_session.add_all([rol_admin, rol_cajera])
    await db_session.flush()

    db_session.add(RolPermiso(id_rol=1, id_permiso=9))
    await db_session.flush()

    u_admin = Usuario(
        id_usuario=1,
        id_rol=1,
        nombre_completo="Admin Reportes API",
        username="admin_rep_api",
        password_hash=security.get_password_hash("pass123"),
        estado="Activo",
        fecha_creacion=datetime(2026, 10, 1),
    )
    u_cajera = Usuario(
        id_usuario=2,
        id_rol=2,
        nombre_completo="Cajera Sin Reportes",
        username="cajera_rep_api",
        password_hash=security.get_password_hash("pass123"),
        estado="Activo",
        fecha_creacion=datetime(2026, 10, 2),
    )
    db_session.add_all([u_admin, u_cajera])
    await db_session.flush()

    tc = TipoCliente(id_tipo_cliente=1, nombre="Minorista", estado="Activo")
    db_session.add(tc)

    depto = DepartamentoGeografico(id_departamento=1, nombre="Guatemala", estado="Activo")
    db_session.add(depto)
    await db_session.flush()

    muni = Municipio(id_municipio=1, id_departamento=1, nombre="Mixco", estado="Activo")
    db_session.add(muni)
    await db_session.flush()

    c1 = Cliente(
        id_cliente=1,
        id_tipo_cliente=1,
        id_municipio=1,
        nit="889944-1",
        nombre_comercial="Librería Central",
        direccion="Zona 4 de Mixco",
        estado="Activo",
        fecha_creacion=datetime(2026, 10, 3),
    )
    db_session.add(c1)
    await db_session.flush()

    ct = ClienteContacto(id_contacto=1, id_cliente=1, telefono="2233-4455", correo="info@libreria.gt")
    db_session.add(ct)
    await db_session.flush()

    return {
        "admin_token": security.create_access_token({"sub": "admin_rep_api"}),
        "cajera_token": security.create_access_token({"sub": "cajera_rep_api"}),
    }


@pytest.mark.asyncio
async def test_api_reporte_usuarios_flujo(client, db_session):
    tokens = await setup_reportes_api_data(db_session)
    admin_headers = {"Authorization": f"Bearer {tokens['admin_token']}"}

    # 1. Listar usuarios
    r = await client.get("/api/reportes/usuarios", headers=admin_headers)
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 2
    assert data[0]["username"] == "admin_rep_api"

    # 2. Ficha de usuario
    r_ficha = await client.get("/api/reportes/usuarios/1", headers=admin_headers)
    assert r_ficha.status_code == 200
    assert r_ficha.json()["nombre_completo"] == "Admin Reportes API"

    # 3. Exportar PDF listado
    r_pdf_list = await client.get("/api/reportes/usuarios/exportar?formato=pdf", headers=admin_headers)
    assert r_pdf_list.status_code == 200
    assert r_pdf_list.headers["content-type"] == "application/pdf"
    assert r_pdf_list.content.startswith(b"%PDF-")

    # 4. Exportar PDF ficha
    r_pdf_ficha = await client.get("/api/reportes/usuarios/1/pdf", headers=admin_headers)
    assert r_pdf_ficha.status_code == 200
    assert r_pdf_ficha.headers["content-type"] == "application/pdf"
    assert r_pdf_ficha.content.startswith(b"%PDF-")


@pytest.mark.asyncio
async def test_api_reporte_clientes_flujo(client, db_session):
    tokens = await setup_reportes_api_data(db_session)
    admin_headers = {"Authorization": f"Bearer {tokens['admin_token']}"}

    # 1. Listar clientes
    r = await client.get("/api/reportes/clientes", headers=admin_headers)
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["nit"] == "889944-1"
    assert data[0]["municipio_nombre"] == "Mixco"
    assert data[0]["departamento_nombre"] == "Guatemala"
    assert "2233-4455" in data[0]["telefonos"]

    # 2. Ficha de cliente
    r_ficha = await client.get("/api/reportes/clientes/1", headers=admin_headers)
    assert r_ficha.status_code == 200
    assert r_ficha.json()["nombre_comercial"] == "Librería Central"

    # 3. Exportar PDF listado
    r_pdf_list = await client.get("/api/reportes/clientes/exportar?formato=pdf", headers=admin_headers)
    assert r_pdf_list.status_code == 200
    assert r_pdf_list.headers["content-type"] == "application/pdf"
    assert r_pdf_list.content.startswith(b"%PDF-")

    # 4. Exportar PDF ficha
    r_pdf_ficha = await client.get("/api/reportes/clientes/1/pdf", headers=admin_headers)
    assert r_pdf_ficha.status_code == 200
    assert r_pdf_ficha.headers["content-type"] == "application/pdf"
    assert r_pdf_ficha.content.startswith(b"%PDF-")


@pytest.mark.asyncio
async def test_api_reportes_403_cajera_sin_permiso(client, db_session):
    tokens = await setup_reportes_api_data(db_session)
    cajera_headers = {"Authorization": f"Bearer {tokens['cajera_token']}"}

    endpoints = [
        "/api/reportes/usuarios",
        "/api/reportes/usuarios/1",
        "/api/reportes/usuarios/exportar?formato=pdf",
        "/api/reportes/usuarios/1/pdf",
        "/api/reportes/clientes",
        "/api/reportes/clientes/1",
        "/api/reportes/clientes/exportar?formato=pdf",
        "/api/reportes/clientes/1/pdf",
        "/api/reportes/?fecha_inicio=2026-10-01&fecha_fin=2026-10-23",
        "/api/reportes/exportar?fecha_inicio=2026-10-01&fecha_fin=2026-10-23&formato=excel",
    ]

    for ep in endpoints:
        resp = await client.get(ep, headers=cajera_headers)
        assert resp.status_code == 403, f"Endpoint {ep} debe responder 403, respondió {resp.status_code}"


@pytest.mark.asyncio
async def test_api_reportes_404_no_encontrado(client, db_session):
    tokens = await setup_reportes_api_data(db_session)
    admin_headers = {"Authorization": f"Bearer {tokens['admin_token']}"}

    r_user = await client.get("/api/reportes/usuarios/9999", headers=admin_headers)
    assert r_user.status_code == 404

    r_cli = await client.get("/api/reportes/clientes/9999", headers=admin_headers)
    assert r_cli.status_code == 404
