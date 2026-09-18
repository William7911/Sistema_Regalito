"""
Tests unitarios — ConcreteUserService.export_users()
Patrón: seed → acción → assert (mismo estilo que test_cash_service.py)
"""
import pytest
from fastapi.responses import StreamingResponse
from app.db.models import Rol, Usuario
from app.services.user_service import ConcreteUserService
from app.schemas import schemas


@pytest.fixture
def user_service(uow):
    return ConcreteUserService(uow)


async def _seed_users(db):
    """Crea un rol y dos usuarios (1 activo, 1 inactivo) para los tests."""
    rol = Rol(id_rol=1, nombre="Administrador", estado="Activo")
    db.add(rol)
    await db.flush()

    activo = Usuario(
        id_usuario=1,
        id_rol=1,
        nombre_completo="Ana García",
        username="ana.garcia",
        password_hash="hash_test",
        estado="Activo",
    )
    inactivo = Usuario(
        id_usuario=2,
        id_rol=1,
        nombre_completo="Luis Pérez",
        username="luis.perez",
        password_hash="hash_test",
        estado="Inactivo",
    )
    db.add_all([activo, inactivo])
    await db.commit()


# ---------------------------------------------------------------------------
# Formato Excel
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_export_excel_retorna_streaming_response(user_service, db_session):
    """export_users con fmt='excel' debe retornar un StreamingResponse con el MIME correcto."""
    await _seed_users(db_session)
    filters = schemas.UserFilter()
    response = await user_service.export_users(filters, "excel")

    assert isinstance(response, StreamingResponse)
    assert "spreadsheetml" in response.media_type
    assert "reporte_usuarios_" in response.headers["Content-Disposition"]
    assert ".xlsx" in response.headers["Content-Disposition"]


@pytest.mark.asyncio
async def test_export_excel_body_no_vacio(user_service, db_session):
    """El cuerpo del Excel no debe estar vacío cuando hay usuarios."""
    await _seed_users(db_session)
    filters = schemas.UserFilter()
    response = await user_service.export_users(filters, "excel")

    body = b"".join([chunk async for chunk in response.body_iterator])
    assert len(body) > 0


# ---------------------------------------------------------------------------
# Formato CSV
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_export_csv_retorna_streaming_response(user_service, db_session):
    """export_users con fmt='csv' debe retornar un StreamingResponse con MIME text/csv."""
    await _seed_users(db_session)
    filters = schemas.UserFilter()
    response = await user_service.export_users(filters, "csv")

    assert isinstance(response, StreamingResponse)
    assert "text/csv" in response.media_type
    assert ".csv" in response.headers["Content-Disposition"]


@pytest.mark.asyncio
async def test_export_csv_filtra_activos(user_service, db_session):
    """El filtro is_active=True debe incluir solo usuarios activos en el CSV."""
    await _seed_users(db_session)
    filters = schemas.UserFilter(is_active=True)
    response = await user_service.export_users(filters, "csv")

    body = b"".join([chunk async for chunk in response.body_iterator])
    text = body.decode("utf-8-sig")
    lines = [l for l in text.strip().splitlines() if l.strip()]

    # 1 cabecera + 1 fila de datos (solo el usuario activo)
    assert len(lines) == 2
    assert "Ana García" in text
    assert "Luis Pérez" not in text


@pytest.mark.asyncio
async def test_export_csv_sin_usuarios_solo_cabeceras(user_service, db_session):
    """Sin usuarios en la BD, el CSV debe contener solo la fila de cabeceras."""
    filters = schemas.UserFilter()
    response = await user_service.export_users(filters, "csv")

    body = b"".join([chunk async for chunk in response.body_iterator])
    text = body.decode("utf-8-sig")
    lines = [l for l in text.strip().splitlines() if l.strip()]

    assert len(lines) == 1
    assert "ID" in lines[0]
    assert "Nombre Completo" in lines[0]

