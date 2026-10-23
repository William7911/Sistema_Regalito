import pytest
from datetime import date
from fastapi import HTTPException
from sqlalchemy import select

from app.core import security
from app.db.models import Rol, Usuario, Permiso, RolPermiso, VisitaSeguimiento, VisitaModuloEvaluacion, BitacoraAuditoria
from app.schemas.visita_schema import VisitaCreate, VisitaUpdate, ModuloEvaluacionInput, MODULOS_DEFAULT
from app.services.visita_service import ConcreteVisitaService
from tests.conftest import TestUnitOfWork


async def seed_visita_data(db_session):
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
        nombre_completo="Admin Visitas",
        username="admin_visita",
        password_hash=security.get_password_hash("pass123"),
        estado="Activo",
    )
    user_cajera = Usuario(
        id_usuario=2,
        id_rol=2,
        nombre_completo="Cajera Sin Permiso",
        username="cajera_visita",
        password_hash=security.get_password_hash("pass123"),
        estado="Activo",
    )
    db_session.add_all([user_admin, user_cajera])
    await db_session.flush()


@pytest.mark.asyncio
async def test_guardar_borrador_exito(db_session):
    await seed_visita_data(db_session)
    uow = TestUnitOfWork(db_session)
    service = ConcreteVisitaService(uow)

    data = VisitaCreate(
        fecha_visita=date(2026, 10, 23),
        lugar="Tienda Panajachel",
        nombre_representante="Doña Silvia",
        cargo_representante="Propietaria",
        calificacion_general=5,
        observaciones="Visita inicial de prueba",
        modulos=[
            ModuloEvaluacionInput(nombre_modulo="POS/Ventas", resultado="Conforme", calificacion=5, comentario="Rápido"),
            ModuloEvaluacionInput(nombre_modulo="Inventario", resultado="Modificar", comentario="Falta código de barras"),
            ModuloEvaluacionInput(nombre_modulo="Compras", resultado="Agregar", comentario="Sugerir proveedor"),
        ]
    )

    visita_out = await service.guardar_borrador(data, id_usuario=1)

    assert visita_out.id_visita is not None
    assert visita_out.estado == "Borrador"
    assert visita_out.nombre_representante == "Doña Silvia"
    assert visita_out.evaluador_nombre == "Admin Visitas"
    assert len(visita_out.modulos) == 3
    assert visita_out.resumen.conformes == 1
    assert visita_out.resumen.modificar == 1
    assert visita_out.resumen.agregar == 1
    assert visita_out.resumen.sin_evaluar == 7

    # Verificar bitácora de auditoría
    res_bit = await db_session.execute(
        select(BitacoraAuditoria).where(BitacoraAuditoria.tabla_afectada == "visita_seguimiento")
    )
    bit = res_bit.scalar_one_or_none()
    assert bit is not None
    assert bit.accion == "CREAR"


@pytest.mark.asyncio
async def test_actualizar_borrador_exito(db_session):
    await seed_visita_data(db_session)
    uow = TestUnitOfWork(db_session)
    service = ConcreteVisitaService(uow)

    data = VisitaCreate(
        nombre_representante="Doña Silvia",
        cargo_representante="Dueña",
        modulos=[
            ModuloEvaluacionInput(nombre_modulo="POS/Ventas", resultado="Modificar", comentario="Ajuste menor"),
        ]
    )
    visita_creada = await service.guardar_borrador(data, id_usuario=1)

    # Actualizar borrador
    data_up = VisitaUpdate(
        lugar="Sucursal 1",
        calificacion_general=4,
        modulos=[
            ModuloEvaluacionInput(nombre_modulo="POS/Ventas", resultado="Conforme", comentario="Solucionado"),
            ModuloEvaluacionInput(nombre_modulo="Caja", resultado="Conforme", comentario="Todo cuadra"),
        ]
    )
    visita_actualizada = await service.actualizar_borrador(visita_creada.id_visita, data_up, id_usuario=1)

    assert visita_actualizada.lugar == "Sucursal 1"
    assert visita_actualizada.calificacion_general == 4
    assert len(visita_actualizada.modulos) == 2
    assert visita_actualizada.resumen.conformes == 2


@pytest.mark.asyncio
async def test_completar_visita_exito(db_session):
    await seed_visita_data(db_session)
    uow = TestUnitOfWork(db_session)
    service = ConcreteVisitaService(uow)

    data = VisitaCreate(
        nombre_representante="Don Carlos",
        cargo_representante="Gerente",
        calificacion_general=5,
    )
    visita_borrador = await service.guardar_borrador(data, id_usuario=1)
    assert visita_borrador.estado == "Borrador"

    visita_completada = await service.completar_visita(visita_borrador.id_visita, None, id_usuario=1)
    assert visita_completada.estado == "Completada"

    # Intentar editar borrador una vez completado debe fallar con 400
    with pytest.raises(HTTPException) as exc_info:
        await service.actualizar_borrador(visita_borrador.id_visita, VisitaUpdate(lugar="Otro"), id_usuario=1)
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_generar_pdf_exito(db_session):
    await seed_visita_data(db_session)
    uow = TestUnitOfWork(db_session)
    service = ConcreteVisitaService(uow)

    data = VisitaCreate(
        fecha_visita=date(2026, 10, 23),
        lugar="Panajachel",
        nombre_representante="Silvia Gómez",
        cargo_representante="Propietaria",
        calificacion_general=5,
        observaciones="Evaluación trimestral satisfactoria.",
        modulos=[
            ModuloEvaluacionInput(nombre_modulo=m, resultado="Conforme" if i % 2 == 0 else "Modificar")
            for i, m in enumerate(MODULOS_DEFAULT)
        ]
    )
    visita = await service.guardar_borrador(data, id_usuario=1)
    await service.completar_visita(visita.id_visita, None, id_usuario=1)

    pdf_bytes = await service.generar_pdf(visita.id_visita, id_usuario=1)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 1000


@pytest.mark.asyncio
async def test_permiso_denegado_cajera_403(db_session):
    await seed_visita_data(db_session)
    uow = TestUnitOfWork(db_session)
    service = ConcreteVisitaService(uow)

    data = VisitaCreate(nombre_representante="Test")
    # Usuario 2 (Cajera) no tiene VISITA_REGISTRAR
    with pytest.raises(HTTPException) as exc_info:
        await service.guardar_borrador(data, id_usuario=2)
    assert exc_info.value.status_code == 403
