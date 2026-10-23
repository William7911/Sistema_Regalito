import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy import text

# Modelos para sembrar la base de datos de prueba
from app.db.models import Usuario, Rol, Venta, Merma, Compra, Proveedor, Sucursal, Caja, TurnoCaja

# Asumimos que la lógica se encapsulará en ReportesService (capa DERCAS)
from app.services.reporte_service import ReportesService


async def _seed_reportes_data(db_session):
    """
    Hidrata la base de datos en memoria con Roles, Usuarios y 
    datos de Ventas, Mermas y Compras distribuidos en diferentes fechas
    para probar exhaustivamente el filtrado y las restricciones RBAC.
    """
    # 0. Crear Sucursal, Caja, Turno (Requerido para Ventas)
    sucursal = Sucursal(id_sucursal=1, nombre="Central", direccion="Zona 1", telefono="123", estado="Activo")
    caja = Caja(id_caja=1, id_sucursal=1, descripcion="Caja 1", estado="Activo")
    db_session.add_all([sucursal, caja])
    await db_session.flush()

    # 1. Crear Roles
    rol_admin = Rol(id_rol=1, nombre="Administradora", descripcion="Admin", estado="Activo")
    rol_bodega = Rol(id_rol=2, nombre="Bodeguero", descripcion="Bodega", estado="Activo")
    rol_cajero = Rol(id_rol=3, nombre="Cajero", descripcion="Caja", estado="Activo")
    db_session.add_all([rol_admin, rol_bodega, rol_cajero])
    await db_session.flush()

    # 2. Crear Usuarios
    admin = Usuario(id_usuario=1, id_rol=1, nombre_completo="Admin", username="admin", password_hash="hash", estado="Activo")
    bodega = Usuario(id_usuario=2, id_rol=2, nombre_completo="Bodega", username="bodega", password_hash="hash", estado="Activo")
    cajero = Usuario(id_usuario=3, id_rol=3, nombre_completo="Cajero", username="cajero", password_hash="hash", estado="Activo")
    db_session.add_all([admin, bodega, cajero])
    await db_session.flush()
    
    # 2.5 Crear Turno
    fecha_hoy = date.today()
    dt_hoy = datetime.now()
    turno = TurnoCaja(id_turno=1, id_caja=1, id_usuario=3, monto_apertura=Decimal("0.00"), fecha_apertura=dt_hoy, estado="Abierto")
    db_session.add(turno)
    await db_session.flush()

    # 3. Proveedor (para las compras)
    prov = Proveedor(id_proveedor=1, nombre_contacto="Juan", distribuidora="Dist X")
    db_session.add(prov)
    await db_session.flush()

    # Fechas de prueba
    fecha_pasada = fecha_hoy - timedelta(days=10)
    fecha_futura = fecha_hoy + timedelta(days=10)
    
    dt_pasado = dt_hoy - timedelta(days=10)
    dt_futuro = dt_hoy + timedelta(days=10)

    # 4. Crear Ventas (3 fechas distintas)
    v1 = Venta(id_venta=1, id_turno=1, id_usuario=3, fecha_venta=dt_pasado, subtotal=Decimal("100"), descuento_total=Decimal("0"), total_venta=Decimal("100.00"), estado="Completada")
    v2 = Venta(id_venta=2, id_turno=1, id_usuario=3, fecha_venta=dt_hoy, subtotal=Decimal("200"), descuento_total=Decimal("0"), total_venta=Decimal("200.00"), estado="Completada")
    v3 = Venta(id_venta=3, id_turno=1, id_usuario=3, fecha_venta=dt_futuro, subtotal=Decimal("300"), descuento_total=Decimal("0"), total_venta=Decimal("300.00"), estado="Completada")
    db_session.add_all([v1, v2, v3])

    # 5. Crear Mermas (3 fechas distintas)
    m1 = Merma(id_merma=1, id_sucursal=1, id_usuario=2, fecha_merma=dt_pasado, observaciones="1")
    m2 = Merma(id_merma=2, id_sucursal=1, id_usuario=2, fecha_merma=dt_hoy, observaciones="2")
    m3 = Merma(id_merma=3, id_sucursal=1, id_usuario=2, fecha_merma=dt_futuro, observaciones="3")
    db_session.add_all([m1, m2, m3])

    # 6. Crear Compras / Ingresos (3 fechas distintas)
    c1 = Compra(id_compra=1, id_proveedor=1, id_usuario=2, fecha_ingreso=fecha_pasada, numero_factura_proveedor="1", subtotal_mercaderia=Decimal("1000.00"), gasto_flete=Decimal("0.00"), gasto_cargadores=Decimal("0.00"), total_compra=Decimal("1000.00"))
    c2 = Compra(id_compra=2, id_proveedor=1, id_usuario=2, fecha_ingreso=fecha_hoy, numero_factura_proveedor="2", subtotal_mercaderia=Decimal("2000.00"), gasto_flete=Decimal("0.00"), gasto_cargadores=Decimal("0.00"), total_compra=Decimal("2000.00"))
    c3 = Compra(id_compra=3, id_proveedor=1, id_usuario=2, fecha_ingreso=fecha_futura, numero_factura_proveedor="3", subtotal_mercaderia=Decimal("3000.00"), gasto_flete=Decimal("0.00"), gasto_cargadores=Decimal("0.00"), total_compra=Decimal("3000.00"))
    db_session.add_all([c1, c2, c3])

    await db_session.commit()

    return {
        "admin_id": 1,
        "bodega_id": 2,
        "cajero_id": 3,
        "v_hoy_id": 2,
        "m_hoy_id": 2,
        "c_hoy_id": 2
    }


@pytest.fixture
def reportes_service(uow):
    return ReportesService(uow)


@pytest.mark.asyncio
async def test_acceso_administradora_exito(reportes_service, db_session, uow):
    """
    Escenario: La Administradora debe poder acceder al consolidado de reportes exitosamente.
    """
    ctx = await _seed_reportes_data(db_session)
    
    fecha_inicio = date.today() - timedelta(days=30)
    fecha_fin = date.today() + timedelta(days=30)
    
    reporte = await reportes_service.obtener_consolidado(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        user_id=ctx["admin_id"]
    )
    
    assert reporte is not None
    assert hasattr(reporte, 'ventas')
    assert hasattr(reporte, 'mermas')
    assert hasattr(reporte, 'compras')


@pytest.mark.asyncio
async def test_filtrado_fechas_estricto(reportes_service, db_session, uow):
    """
    Escenario: El sistema debe filtrar correctamente las ventas, mermas e ingresos
    asegurando que sólo se devuelvan los registros que caigan dentro del rango seleccionado.
    """
    ctx = await _seed_reportes_data(db_session)
    
    # Rango donde solo debe caer "Hoy" (excluye registros pasados y futuros a 10 días)
    fecha_inicio = date.today() - timedelta(days=2)
    fecha_fin = date.today() + timedelta(days=2)
    
    reporte = await reportes_service.obtener_consolidado(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        user_id=ctx["admin_id"]
    )
    
    # Validaciones estrictas: debe haber exactamente 1 registro por entidad
    assert len(reporte.ventas) == 1, "Debe traer solo la venta del rango de fechas"
    assert len(reporte.mermas) == 1, "Debe traer solo la merma del rango de fechas"
    assert len(reporte.compras) == 1, "Debe traer solo la compra del rango de fechas"
    
    # Asegurar que son exactamente los registros correctos
    assert reporte.ventas[0].id_venta == ctx["v_hoy_id"]
    assert reporte.mermas[0].id_merma == ctx["m_hoy_id"]
    assert reporte.compras[0].id_compra == ctx["c_hoy_id"]


@pytest.mark.asyncio
async def test_exportar_reporte_formatos_exito(reportes_service, db_session, uow):
    """
    Escenario: Descarga del reporte en Excel y CSV. 
    Aseguramos que retorna la estructura correcta esperada para armar el StreamingResponse.
    """
    ctx = await _seed_reportes_data(db_session)
    
    fecha_inicio = date.today() - timedelta(days=2)
    fecha_fin = date.today() + timedelta(days=2)
    
    # Exportación a Excel
    export_excel = await reportes_service.exportar_reporte(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        formato="excel",
        user_id=ctx["admin_id"]
    )
    assert export_excel is not None
    assert export_excel.filename.endswith(".xlsx"), "El archivo Excel debe tener la extensión correcta"
    assert isinstance(export_excel.content, bytes) and len(export_excel.content) > 0, "El contenido Excel no puede estar vacío"
    
    # Exportación a CSV
    export_csv = await reportes_service.exportar_reporte(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        formato="csv",
        user_id=ctx["admin_id"]
    )
    assert export_csv is not None
    assert export_csv.filename.endswith(".csv"), "El archivo CSV debe tener la extensión correcta"
    assert isinstance(export_csv.content, bytes) and len(export_csv.content) > 0, "El contenido CSV no puede estar vacío"


@pytest.mark.asyncio
async def test_acceso_denegado_cajero_bodeguero_falla(reportes_service, db_session, uow):
    """
    Escenario Negativo Estricto: Roles no autorizados intentando acceder al consolidado o a exportarlo.
    """
    ctx = await _seed_reportes_data(db_session)
    fecha_inicio = date.today()
    fecha_fin = date.today()
    
    # 1. Cajero intentando acceder al consolidado -> 403
    with pytest.raises(HTTPException) as exc_cajero_cons:
        await reportes_service.obtener_consolidado(
            fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, user_id=ctx["cajero_id"]
        )
    await db_session.rollback()  # Limpieza de transacción simulada
    assert exc_cajero_cons.value.status_code == 403, "Se esperaba HTTP 403 para Cajero en consolidado"
    
    # 2. Bodeguero intentando exportar el reporte -> 403
    with pytest.raises(HTTPException) as exc_bodega_exp:
        await reportes_service.exportar_reporte(
            fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, formato="excel", user_id=ctx["bodega_id"]
        )
    await db_session.rollback()  # Limpieza de transacción simulada
    assert exc_bodega_exp.value.status_code == 403, "Se esperaba HTTP 403 para Bodeguero en exportación"
