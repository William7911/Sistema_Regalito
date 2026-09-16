import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from fastapi import HTTPException
from app.db.models import Rol, Usuario, Sucursal, Caja
from app.services.cash_service import ConcreteCashService
from app.schemas import schemas


@pytest.fixture
def cash_service(uow):
    return ConcreteCashService(uow)


async def _seed_base_data(db):
    rol = Rol(id_rol=1, nombre="Cajero", estado="Activo")
    db.add(rol)
    await db.flush()

    usuario = Usuario(
        id_usuario=1,
        id_rol=1,
        nombre_completo="Juan Cajero",
        username="cajero1",
        password_hash="hash123",
        estado="Activo",
    )
    usuario2 = Usuario(
        id_usuario=2,
        id_rol=1,
        nombre_completo="Maria Cajera",
        username="cajera2",
        password_hash="hash123",
        estado="Activo",
    )
    db.add_all([usuario, usuario2])
    await db.flush()

    sucursal = Sucursal(
        id_sucursal=1,
        nombre="Central",
        direccion="Calle Principal 1-23",
        telefono="7766-5544",
        estado="Activa",
    )
    db.add(sucursal)
    await db.flush()

    caja1 = Caja(id_caja=1, id_sucursal=1, descripcion="Caja Mostrador 1", estado="Activa")
    caja2 = Caja(id_caja=2, id_sucursal=1, descripcion="Caja Inactiva", estado="Inactiva")
    db.add_all([caja1, caja2])
    await db.commit()


@pytest.mark.asyncio
async def test_abrir_caja_exitoso(cash_service, db_session):
    await _seed_base_data(db_session)

    payload = schemas.TurnoApertura(id_caja=1, monto_apertura=Decimal("150.00"))
    turno = await cash_service.abrir_caja(payload, user_id=1)

    assert turno.id_turno is not None
    assert turno.id_caja == 1
    assert turno.id_usuario == 1
    assert turno.monto_apertura == Decimal("150.00")
    assert turno.estado == "Abierto"
    assert turno.fecha_apertura is not None
    assert turno.fecha_cierre is None
    assert turno.caja is not None
    assert turno.caja.descripcion == "Caja Mostrador 1"
    assert turno.usuario is not None
    assert turno.usuario.username == "cajero1"


@pytest.mark.asyncio
async def test_abrir_caja_falla_caja_inexistente(cash_service, db_session):
    await _seed_base_data(db_session)

    payload = schemas.TurnoApertura(id_caja=999, monto_apertura=Decimal("100.00"))
    with pytest.raises(HTTPException) as exc:
        await cash_service.abrir_caja(payload, user_id=1)
    assert exc.value.status_code == 404
    assert "no existe" in exc.value.detail


@pytest.mark.asyncio
async def test_abrir_caja_falla_caja_inactiva(cash_service, db_session):
    await _seed_base_data(db_session)

    payload = schemas.TurnoApertura(id_caja=2, monto_apertura=Decimal("100.00"))
    with pytest.raises(HTTPException) as exc:
        await cash_service.abrir_caja(payload, user_id=1)
    assert exc.value.status_code == 400
    assert "no está activa" in exc.value.detail


@pytest.mark.asyncio
async def test_abrir_caja_falla_usuario_con_turno_abierto(cash_service, db_session):
    await _seed_base_data(db_session)

    payload = schemas.TurnoApertura(id_caja=1, monto_apertura=Decimal("100.00"))
    await cash_service.abrir_caja(payload, user_id=1)

    # Intentar abrir de nuevo con el mismo usuario
    with pytest.raises(HTTPException) as exc:
        await cash_service.abrir_caja(payload, user_id=1)
    assert exc.value.status_code == 400
    assert "ya tiene un turno de caja abierto" in exc.value.detail


@pytest.mark.asyncio
async def test_abrir_caja_falla_caja_ocupada(cash_service, db_session):
    await _seed_base_data(db_session)

    # Usuario 1 abre caja 1
    payload1 = schemas.TurnoApertura(id_caja=1, monto_apertura=Decimal("100.00"))
    await cash_service.abrir_caja(payload1, user_id=1)

    # Usuario 2 intenta abrir la misma caja 1
    payload2 = schemas.TurnoApertura(id_caja=1, monto_apertura=Decimal("200.00"))
    with pytest.raises(HTTPException) as exc:
        await cash_service.abrir_caja(payload2, user_id=2)
    assert exc.value.status_code == 400
    assert "ya cuenta con un turno abierto" in exc.value.detail


@pytest.mark.asyncio
async def test_cerrar_caja_exitoso(cash_service, db_session):
    await _seed_base_data(db_session)

    # Abrir
    payload_open = schemas.TurnoApertura(id_caja=1, monto_apertura=Decimal("100.00"))
    await cash_service.abrir_caja(payload_open, user_id=1)

    # Cerrar
    payload_close = schemas.TurnoCierre(
        monto_cierre=Decimal("450.75"),
        notas="Cierre normal del turno",
    )
    turno_cerrado = await cash_service.cerrar_caja(payload_close, user_id=1)

    assert turno_cerrado.estado == "Cerrado"
    assert turno_cerrado.monto_cierre == Decimal("450.75")
    assert turno_cerrado.notas == "Cierre normal del turno"
    assert turno_cerrado.fecha_cierre is not None


@pytest.mark.asyncio
async def test_cerrar_caja_sin_turno_falla(cash_service, db_session):
    await _seed_base_data(db_session)

    payload_close = schemas.TurnoCierre(monto_cierre=Decimal("100.00"))
    with pytest.raises(HTTPException) as exc:
        await cash_service.cerrar_caja(payload_close, user_id=1)
    assert exc.value.status_code == 400
    assert "no tiene un turno de caja abierto" in exc.value.detail


@pytest.mark.asyncio
async def test_get_estado_actual(cash_service, db_session):
    await _seed_base_data(db_session)

    # Sin turno
    estado = await cash_service.get_estado_actual(user_id=1)
    assert estado is None

    # Abrir turno
    payload_open = schemas.TurnoApertura(id_caja=1, monto_apertura=Decimal("80.00"))
    await cash_service.abrir_caja(payload_open, user_id=1)

    estado = await cash_service.get_estado_actual(user_id=1)
    assert estado is not None
    assert estado.estado == "Abierto"
    assert estado.monto_apertura == Decimal("80.00")

    # Cerrar turno
    await cash_service.cerrar_caja(schemas.TurnoCierre(monto_cierre=Decimal("80.00")), user_id=1)
    estado = await cash_service.get_estado_actual(user_id=1)
    assert estado is None


@pytest.mark.asyncio
async def test_list_y_count_turnos(cash_service, db_session):
    await _seed_base_data(db_session)

    # Turno 1: Usuario 1 abre y cierra
    await cash_service.abrir_caja(schemas.TurnoApertura(id_caja=1, monto_apertura=Decimal("50.00")), user_id=1)
    await cash_service.cerrar_caja(schemas.TurnoCierre(monto_cierre=Decimal("120.00")), user_id=1)

    # Turno 2: Usuario 2 abre
    await cash_service.abrir_caja(schemas.TurnoApertura(id_caja=1, monto_apertura=Decimal("100.00")), user_id=2)

    # Listar todos
    filters = schemas.TurnoFilter(limit=10, offset=0)
    turnos = await cash_service.list_turnos(filters)
    total = await cash_service.count_turnos(filters)
    assert total == 2
    assert len(turnos) == 2

    # Filtrar por estado Abierto
    filters_abiertos = schemas.TurnoFilter(estado="Abierto")
    turnos_abiertos = await cash_service.list_turnos(filters_abiertos)
    assert len(turnos_abiertos) == 1
    assert turnos_abiertos[0].id_usuario == 2

    # Filtrar por estado Cerrado
    filters_cerrados = schemas.TurnoFilter(estado="Cerrado")
    turnos_cerrados = await cash_service.list_turnos(filters_cerrados)
    assert len(turnos_cerrados) == 1
    assert turnos_cerrados[0].id_usuario == 1


@pytest.mark.asyncio
async def test_list_cajas(cash_service, db_session):
    await _seed_base_data(db_session)

    cajas_activas = await cash_service.list_cajas(include_inactive=False)
    assert len(cajas_activas) == 1
    assert cajas_activas[0].descripcion == "Caja Mostrador 1"

    todas_cajas = await cash_service.list_cajas(include_inactive=True)
    assert len(todas_cajas) == 2
