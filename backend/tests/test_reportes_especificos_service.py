import pytest
from datetime import date, datetime, timedelta
from fastapi import HTTPException

from app.db.models import Rol, Usuario, Permiso, RolPermiso, TipoCliente, Cliente, ClienteContacto, DepartamentoGeografico, Municipio
from app.services.reporte_service import ReportesService
from tests.conftest import TestUnitOfWork


async def _seed_data(db):
    p_rep = Permiso(id_permiso=9, modulo="Reportes", codigo="REPORTE_VER", descripcion="Ver reportes")
    db.add(p_rep)
    await db.flush()

    rol_admin = Rol(id_rol=1, nombre="Administradora", estado="Activo")
    rol_cajera = Rol(id_rol=2, nombre="Cajera", estado="Activo")
    db_session_add = [rol_admin, rol_cajera]
    db.add_all(db_session_add)
    await db.flush()

    db.add(RolPermiso(id_rol=1, id_permiso=9))
    await db.flush()

    u_admin = Usuario(
        id_usuario=1,
        id_rol=1,
        nombre_completo="Admin Reportes",
        username="admin_rep",
        password_hash="hash",
        estado="Activo",
        fecha_creacion=datetime(2026, 10, 1),
    )
    u_inactivo = Usuario(
        id_usuario=2,
        id_rol=2,
        nombre_completo="Usuario Inactivo",
        username="user_inact",
        password_hash="hash",
        estado="Inactivo",
        fecha_creacion=datetime(2026, 10, 15),
    )
    u_cajera = Usuario(
        id_usuario=3,
        id_rol=2,
        nombre_completo="Cajera Sin Reportes",
        username="cajera_rep",
        password_hash="hash",
        estado="Activo",
        fecha_creacion=datetime(2026, 10, 20),
    )
    db.add_all([u_admin, u_inactivo, u_cajera])
    await db.flush()

    # Tipos de cliente
    tc_general = TipoCliente(id_tipo_cliente=1, nombre="Mayorista", estado="Activo")
    db.add(tc_general)

    # Depto y Municipio
    depto = DepartamentoGeografico(id_departamento=1, nombre="Sololá", estado="Activo")
    db.add(depto)
    await db.flush()

    muni = Municipio(id_municipio=1, id_departamento=1, nombre="Panajachel", estado="Activo")
    db.add(muni)
    await db.flush()

    # Clientes
    c1 = Cliente(
        id_cliente=1,
        id_tipo_cliente=1,
        id_municipio=1,
        nit="123456-7",
        nombre_comercial="Distribuidora El Lago",
        direccion="Calle Principal 1-23",
        estado="Activo",
        fecha_creacion=datetime(2026, 10, 5),
    )
    c2 = Cliente(
        id_cliente=2,
        id_tipo_cliente=1,
        id_municipio=1,
        nit="CF",
        nombre_comercial="Consumidor Final",
        direccion="Ciudad",
        estado="Inactivo",
        fecha_creacion=datetime(2026, 10, 18),
    )
    db.add_all([c1, c2])
    await db.flush()

    # Contactos de c1
    ct1 = ClienteContacto(id_contacto=1, id_cliente=1, telefono="7762-1234", correo="ventas@ellago.gt")
    ct2 = ClienteContacto(id_contacto=2, id_cliente=1, telefono="5555-4321", correo=None)
    db.add_all([ct1, ct2])
    await db.flush()


@pytest.mark.asyncio
async def test_obtener_reporte_usuarios_filtrado(db_session):
    await _seed_data(db_session)
    uow = TestUnitOfWork(db_session)
    svc = ReportesService(uow)

    # Todos los usuarios
    todos = await svc.obtener_reporte_usuarios(None, None, None, user_id=1)
    assert len(todos) == 3

    # Filtrar por estado Inactivo
    inactivos = await svc.obtener_reporte_usuarios("Inactivo", None, None, user_id=1)
    assert len(inactivos) == 1
    assert inactivos[0].username == "user_inact"

    # Filtrar por fecha
    recientes = await svc.obtener_reporte_usuarios(None, date(2026, 10, 10), date(2026, 10, 22), user_id=1)
    assert len(recientes) == 2


@pytest.mark.asyncio
async def test_obtener_ficha_usuario(db_session):
    await _seed_data(db_session)
    uow = TestUnitOfWork(db_session)
    svc = ReportesService(uow)

    ficha = await svc.obtener_ficha_usuario(1, user_id=1)
    assert ficha.id_usuario == 1
    assert ficha.nombre_completo == "Admin Reportes"
    assert ficha.rol_nombre == "Administradora"
    assert ficha.estado == "Activo"


@pytest.mark.asyncio
async def test_exportar_usuarios_formatos_pdf_excel_csv(db_session):
    await _seed_data(db_session)
    uow = TestUnitOfWork(db_session)
    svc = ReportesService(uow)

    # PDF listado
    pdf_list = await svc.exportar_usuarios(None, None, None, "pdf", user_id=1)
    assert pdf_list.filename.endswith(".pdf")
    assert pdf_list.content.startswith(b"%PDF-")
    assert len(pdf_list.content) > 500

    # Excel
    excel = await svc.exportar_usuarios(None, None, None, "excel", user_id=1)
    assert excel.filename.endswith(".xlsx")
    assert len(excel.content) > 0

    # CSV
    csv_res = await svc.exportar_usuarios(None, None, None, "csv", user_id=1)
    assert csv_res.filename.endswith(".csv")
    assert b"Admin Reportes" in csv_res.content

    # Ficha individual PDF
    ficha_pdf = await svc.exportar_ficha_usuario_pdf(1, user_id=1)
    assert ficha_pdf.filename.startswith("ficha_usuario_1")
    assert ficha_pdf.content.startswith(b"%PDF-")


@pytest.mark.asyncio
async def test_obtener_reporte_clientes_filtrado(db_session):
    await _seed_data(db_session)
    uow = TestUnitOfWork(db_session)
    svc = ReportesService(uow)

    # Todos los clientes
    todos = await svc.obtener_reporte_clientes(None, None, None, user_id=1)
    assert len(todos) == 2

    # Filtrar por estado Activo
    activos = await svc.obtener_reporte_clientes("Activo", None, None, user_id=1)
    assert len(activos) == 1
    assert activos[0].nit == "123456-7"
    assert activos[0].tipo_cliente_nombre == "Mayorista"
    assert activos[0].municipio_nombre == "Panajachel"
    assert activos[0].departamento_nombre == "Sololá"
    assert "7762-1234" in activos[0].telefonos
    assert "ventas@ellago.gt" in activos[0].correos


@pytest.mark.asyncio
async def test_obtener_ficha_cliente(db_session):
    await _seed_data(db_session)
    uow = TestUnitOfWork(db_session)
    svc = ReportesService(uow)

    ficha = await svc.obtener_ficha_cliente(1, user_id=1)
    assert ficha.id_cliente == 1
    assert ficha.nombre_comercial == "Distribuidora El Lago"
    assert ficha.nit == "123456-7"
    assert ficha.tipo_cliente_nombre == "Mayorista"
    assert len(ficha.telefonos) == 2
    assert len(ficha.correos) == 1


@pytest.mark.asyncio
async def test_exportar_clientes_formatos_pdf_excel_csv(db_session):
    await _seed_data(db_session)
    uow = TestUnitOfWork(db_session)
    svc = ReportesService(uow)

    # PDF listado
    pdf_list = await svc.exportar_clientes(None, None, None, "pdf", user_id=1)
    assert pdf_list.filename.endswith(".pdf")
    assert pdf_list.content.startswith(b"%PDF-")
    assert len(pdf_list.content) > 500

    # Excel
    excel = await svc.exportar_clientes(None, None, None, "excel", user_id=1)
    assert excel.filename.endswith(".xlsx")
    assert len(excel.content) > 0

    # CSV
    csv_res = await svc.exportar_clientes(None, None, None, "csv", user_id=1)
    assert csv_res.filename.endswith(".csv")
    assert b"Distribuidora El Lago" in csv_res.content

    # Ficha individual PDF
    ficha_pdf = await svc.exportar_ficha_cliente_pdf(1, user_id=1)
    assert ficha_pdf.filename.startswith("ficha_cliente_1")
    assert ficha_pdf.content.startswith(b"%PDF-")


@pytest.mark.asyncio
async def test_reportes_403_cajera_sin_permiso(db_session):
    await _seed_data(db_session)
    uow = TestUnitOfWork(db_session)
    svc = ReportesService(uow)

    # Usuario 3 (cajera sin REPORTE_VER)
    with pytest.raises(HTTPException) as exc1:
        await svc.obtener_reporte_usuarios(None, None, None, user_id=3)
    assert exc1.value.status_code == 403

    with pytest.raises(HTTPException) as exc2:
        await svc.obtener_reporte_clientes(None, None, None, user_id=3)
    assert exc2.value.status_code == 403

