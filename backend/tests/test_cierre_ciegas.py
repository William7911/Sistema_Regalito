"""
Pruebas unitarias para Cierre de Caja a Ciegas y Arqueo de Efectivo (RF17, Proceso 4).
"""
import pytest
from decimal import Decimal
from fastapi import HTTPException
from app.db.models import Rol, Usuario, Sucursal, Caja, TurnoCaja, DenominacionEfectivo
from app.services.cash_service import ConcreteCashService
from app.schemas import schemas


@pytest.fixture
def cash_service(uow):
    return ConcreteCashService(uow)


async def _seed_cierre_data(db):
    rol = Rol(id_rol=1, nombre="Cajero", estado="Activo")
    db.add(rol)
    await db.flush()

    usuario = Usuario(
        id_usuario=1,
        id_rol=1,
        nombre_completo="Cajero Test",
        username="cajerotest",
        password_hash="hash123",
        estado="Activo",
    )
    db.add(usuario)
    await db.flush()

    sucursal = Sucursal(
        id_sucursal=1,
        nombre="Central",
        direccion="Calle 1",
        telefono="1234",
        estado="Activa",
    )
    db.add(sucursal)
    await db.flush()

    caja = Caja(id_caja=1, id_sucursal=1, descripcion="Caja 1", estado="Activa")
    db.add(caja)
    await db.flush()

    turno = TurnoCaja(
        id_turno=1,
        id_caja=1,
        id_usuario=1,
        monto_apertura=Decimal("100.00"),
        fecha_apertura=schemas.datetime.now(),
        estado="Abierto",
    )
    db.add(turno)

    # Denominaciones: 1 (Q200), 2 (Q100), 3 (Q50)
    d1 = DenominacionEfectivo(id_denominacion=1, valor=Decimal("200.00"), tipo="Billete")
    d2 = DenominacionEfectivo(id_denominacion=2, valor=Decimal("100.00"), tipo="Billete")
    d3 = DenominacionEfectivo(id_denominacion=3, valor=Decimal("50.00"), tipo="Billete")
    db.add_all([d1, d2, d3])
    await db.commit()


@pytest.mark.asyncio
async def test_cierre_ciegas_cuadrado(cash_service, db_session):
    """Cierre a ciegas donde el arqueo coincide con el fondo inicial (sin ventas)."""
    await _seed_cierre_data(db_session)

    # Fondo inicial = 100.00. Arqueo = 1 billete de 100.00
    payload = schemas.CierreCiegasCreate(
        detalles=[schemas.ArqueoItemCreate(id_denominacion=2, cantidad_piezas=1)],
        observaciones=None,
    )
    cierre = await cash_service.cerrar_caja_ciegas(payload, user_id=1)

    assert cierre.total_contado_ciegas == Decimal("100.00")
    assert cierre.total_calculado_sistema == Decimal("100.00")
    assert cierre.diferencia == Decimal("0.00")
    assert cierre.estado_cierre == "Cuadrado"


@pytest.mark.asyncio
async def test_cierre_ciegas_descuadre_sin_observaciones_falla(cash_service, db_session):
    """RF17: Si hay diferencia (descuadre), es obligatorio ingresar observaciones."""
    await _seed_cierre_data(db_session)

    # Arqueo = 50.00 (Faltan 50.00 respecto a los 100.00)
    payload = schemas.CierreCiegasCreate(
        detalles=[schemas.ArqueoItemCreate(id_denominacion=3, cantidad_piezas=1)],
        observaciones=None,  # Sin justificación
    )

    with pytest.raises(HTTPException) as exc_info:
        await cash_service.cerrar_caja_ciegas(payload, user_id=1)

    assert exc_info.value.status_code == 400
    assert "Debe ingresar observaciones" in exc_info.value.detail


@pytest.mark.asyncio
async def test_cierre_ciegas_descuadre_con_observaciones_exitoso(cash_service, db_session):
    """RF17: Cierre con sobrante y justificación en observaciones."""
    await _seed_cierre_data(db_session)

    # Arqueo = 150.00 (1 billete de 100 y 1 de 50). Sobrante de 50.00
    payload = schemas.CierreCiegasCreate(
        detalles=[
            schemas.ArqueoItemCreate(id_denominacion=2, cantidad_piezas=1),
            schemas.ArqueoItemCreate(id_denominacion=3, cantidad_piezas=1),
        ],
        observaciones="Sobrante por propina dejada en mostrador",
    )
    cierre = await cash_service.cerrar_caja_ciegas(payload, user_id=1)

    assert cierre.total_contado_ciegas == Decimal("150.00")
    assert cierre.diferencia == Decimal("50.00")
    assert cierre.estado_cierre == "Sobrante"
    assert "propina" in cierre.observaciones

