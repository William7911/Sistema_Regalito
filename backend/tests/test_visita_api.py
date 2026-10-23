import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.db.database import get_db
from app.core import security
from app.db.models import Rol, Usuario, Permiso, RolPermiso
from app.schemas.visita_schema import MODULOS_DEFAULT


@pytest.fixture
async def client(db_session):
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c
    app.dependency_overrides.clear()


async def setup_api_data(db_session):
    p_visita = Permiso(id_permiso=10, modulo="Visitas", codigo="VISITA_REGISTRAR", descripcion="Registrar visitas")
    db_session.add(p_visita)
    await db_session.flush()

    rol_admin = Rol(id_rol=1, nombre="Administradora", estado="Activo")
    rol_cajera = Rol(id_rol=2, nombre="Cajera", estado="Activo")
    db_session.add_all([rol_admin, rol_cajera])
    await db_session.flush()

    db_session.add(RolPermiso(id_rol=1, id_permiso=10))
    await db_session.flush()

    user_admin = Usuario(
        id_usuario=1,
        id_rol=1,
        nombre_completo="Admin Visita API",
        username="admin_v_api",
        password_hash=security.get_password_hash("pass123"),
        estado="Activo",
    )
    user_cajera = Usuario(
        id_usuario=2,
        id_rol=2,
        nombre_completo="Cajera Visita API",
        username="cajera_v_api",
        password_hash=security.get_password_hash("pass123"),
        estado="Activo",
    )
    db_session.add_all([user_admin, user_cajera])
    await db_session.flush()

    return {
        "admin_token": security.create_access_token({"sub": "admin_v_api"}),
        "cajera_token": security.create_access_token({"sub": "cajera_v_api"}),
    }


@pytest.mark.asyncio
async def test_visitas_api_flujo_completo(client, db_session):
    tokens = await setup_api_data(db_session)
    admin_headers = {"Authorization": f"Bearer {tokens['admin_token']}"}

    # 1. Guardar Borrador
    payload_draft = {
        "fecha_visita": "2026-10-23",
        "lugar": "Tienda Central Panajachel",
        "nombre_representante": "Silvia Gómez",
        "cargo_representante": "Propietaria",
        "calificacion_general": 5,
        "observaciones": "Visita trimestral con alta satisfacción.",
        "modulos": [
            {"nombre_modulo": "POS/Ventas", "resultado": "Conforme", "calificacion": 5, "comentario": "Excelente velocidad"},
            {"nombre_modulo": "Inventario", "resultado": "Modificar", "comentario": "Falta escáner bluetooth"},
            {"nombre_modulo": "Caja", "resultado": "Conforme", "comentario": "Cierres ciegos funcionan perfecto"},
        ]
    }
    r = await client.post("/api/visitas/borrador", json=payload_draft, headers=admin_headers)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["id_visita"] is not None
    assert data["estado"] == "Borrador"
    assert data["resumen"]["conformes"] == 2
    assert data["resumen"]["modificar"] == 1
    assert data["resumen"]["sin_evaluar"] == 7
    visita_id = data["id_visita"]

    # 2. Listar Visitas
    r_list = await client.get("/api/visitas", headers=admin_headers)
    assert r_list.status_code == 200
    items = r_list.json()
    assert len(items) == 1
    assert items[0]["id_visita"] == visita_id

    # 3. Ver Detalle
    r_detail = await client.get(f"/api/visitas/{visita_id}", headers=admin_headers)
    assert r_detail.status_code == 200
    det = r_detail.json()
    assert det["nombre_representante"] == "Silvia Gómez"

    # 4. Actualizar Borrador
    r_put = await client.put(
        f"/api/visitas/{visita_id}/borrador",
        json={"cargo_representante": "Dueña y Gerente"},
        headers=admin_headers
    )
    assert r_put.status_code == 200
    assert r_put.json()["cargo_representante"] == "Dueña y Gerente"

    # 5. Completar Visita
    r_comp = await client.post(
        f"/api/visitas/{visita_id}/completar",
        headers=admin_headers
    )
    assert r_comp.status_code == 200
    assert r_comp.json()["estado"] == "Completada"

    # 6. Descargar PDF
    r_pdf = await client.get(f"/api/visitas/{visita_id}/pdf", headers=admin_headers)
    assert r_pdf.status_code == 200
    assert r_pdf.headers["content-type"] == "application/pdf"
    assert len(r_pdf.content) > 1000
    assert r_pdf.content.startswith(b"%PDF-")


@pytest.mark.asyncio
async def test_visitas_api_403_cajera_sin_permiso(client, db_session):
    tokens = await setup_api_data(db_session)
    cajera_headers = {"Authorization": f"Bearer {tokens['cajera_token']}"}

    # Intentos de acceso con usuario sin permiso VISITA_REGISTRAR
    r1 = await client.get("/api/visitas", headers=cajera_headers)
    assert r1.status_code == 403

    r2 = await client.post("/api/visitas/borrador", json={"nombre_representante": "X"}, headers=cajera_headers)
    assert r2.status_code == 403

    r3 = await client.get("/api/visitas/1", headers=cajera_headers)
    assert r3.status_code == 403

    r4 = await client.get("/api/visitas/1/pdf", headers=cajera_headers)
    assert r4.status_code == 403


@pytest.mark.asyncio
async def test_visitas_api_404_no_encontrado(client, db_session):
    tokens = await setup_api_data(db_session)
    admin_headers = {"Authorization": f"Bearer {tokens['admin_token']}"}

    r = await client.get("/api/visitas/9999", headers=admin_headers)
    assert r.status_code == 404
