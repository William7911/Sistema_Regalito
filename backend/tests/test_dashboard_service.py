"""
Pruebas del Panel Principal (Dashboard):
  1. Repositorio: métricas agregadas reales sobre aiosqlite (ventas del día,
     stock crítico, compras del mes, turnos activos, ventas por metodo de pago,
     mermas, top productos, pendientes y últimas ventas) y estados vacíos.
  2. Servicio: ensambla el resumen DTO completo con los valores de la BD.
  3. API: GET /api/dashboard/resumen autenticado devuelve 200; sin token 401.
"""
import pytest
from decimal import Decimal
from datetime import date, datetime, timedelta
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.db.database import get_db
from app.api.deps import get_current_user
from app.db.models import (
    Usuario, Venta, InventarioSucursal, TurnoCaja, Compra,
    Caja, Sucursal, Producto, VarianteProducto, MetodoPago,
    PagoVenta, DetalleVenta, OrdenCompra, Proveedor, TrasladoInventario,
)
from app.repositories.dashboard_repository import (
    DashboardRepositoryImpl,
    guatemala_today,
    _utc_bounds,
)
from app.services.dashboard_service import ConcreteDashboardService


@pytest.fixture
async def client(db_session):
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c
    app.dependency_overrides.clear()


async def _seed_metrics(db):
    """Población controlada y determinista en zona horaria Guatemala.

    Los timestamps de venta/turno se generan dentro de los límites UTC que
    corresponden a los días calendario locales, de modo que las pruebas pasan
    sin importar la zona horaria de la máquina.
    """
    hoy_gt = guatemala_today()
    ayer_gt = hoy_gt - timedelta(days=1)
    inicio_hoy, _ = _utc_bounds(hoy_gt)
    inicio_ayer, _ = _utc_bounds(ayer_gt)

    turno_activo = TurnoCaja(
        id_caja=1, id_usuario=1, monto_apertura=Decimal("100.00"),
        fecha_apertura=inicio_hoy, estado="Abierto",
    )
    turno_cerrado = TurnoCaja(
        id_caja=2, id_usuario=2, monto_apertura=Decimal("50.00"),
        fecha_apertura=inicio_hoy, estado="Cerrado",
    )
    db.add_all([turno_activo, turno_cerrado])

    venta_hoy = Venta(
        id_turno=1, id_usuario=1, fecha_venta=inicio_hoy + timedelta(hours=2),
        subtotal=Decimal("100.00"), descuento_total=Decimal("0.00"),
        total_venta=Decimal("100.00"), estado="Completada",
    )
    venta_ayer = Venta(
        id_turno=1, id_usuario=1, fecha_venta=inicio_ayer + timedelta(hours=2),
        subtotal=Decimal("50.00"), descuento_total=Decimal("0.00"),
        total_venta=Decimal("50.00"), estado="Completada",
    )
    venta_cancelada_hoy = Venta(
        id_turno=1, id_usuario=1, fecha_venta=inicio_hoy + timedelta(hours=3),
        subtotal=Decimal("999.00"), descuento_total=Decimal("0.00"),
        total_venta=Decimal("999.00"), estado="Cancelada",
    )
    db.add_all([venta_hoy, venta_ayer, venta_cancelada_hoy])

    inv_bajo = InventarioSucursal(
        id_variante=1, id_sucursal=1, stock_actual=3, stock_minimo=10,
        fecha_actualizacion=inicio_hoy,
    )
    inv_ok = InventarioSucursal(
        id_variante=2, id_sucursal=1, stock_actual=50, stock_minimo=10,
        fecha_actualizacion=inicio_hoy,
    )
    db.add_all([inv_bajo, inv_ok])

    compra_mes_1 = Compra(
        id_proveedor=1, id_usuario=1, numero_factura_proveedor="F2001",
        fecha_ingreso=hoy_gt.replace(day=1),
        subtotal_mercaderia=Decimal("200.00"), gasto_flete=Decimal("10.00"),
        gasto_cargadores=Decimal("0.00"), total_compra=Decimal("210.00"),
    )
    compra_mes_2 = Compra(
        id_proveedor=1, id_usuario=1, numero_factura_proveedor="F2002",
        fecha_ingreso=hoy_gt,
        subtotal_mercaderia=Decimal("100.00"), gasto_flete=Decimal("0.00"),
        gasto_cargadores=Decimal("0.00"), total_compra=Decimal("100.00"),
    )
    db.add_all([compra_mes_1, compra_mes_2])
    await db.flush()


async def _seed_caja_completa(db):
    """Datos auxiliares para ejercitar todos los bloques del panel (turno,
    metodos de pago, top productos, mermas, pendientes y últimas ventas)."""
    hoy_gt = guatemala_today()
    semana = [hoy_gt - timedelta(days=i) for i in range(7)]
    inicio_hoy, _ = _utc_bounds(hoy_gt)

    caja = Caja(id_caja=10, id_sucursal=10, descripcion="Caja Principal", estado="Activa")
    db.add(caja)

    vendedora = Usuario(
        id_usuario=10, id_rol=1, nombre_completo="Ana Vendedora",
        username="ana", password_hash="x", estado="Activo",
    )
    db.add(vendedora)

    met_efectivo = MetodoPago(id_metodo_pago=1, nombre="Efectivo", estado="Activo")
    met_transf = MetodoPago(id_metodo_pago=2, nombre="Transferencia", estado="Activo")
    db.add_all([met_efectivo, met_transf])

    base_gt = Sucursal(
        id_sucursal=10, nombre="Sucursal Central",
        direccion="Av. Principal", estado="Activa",
    )
    otro_gt = Sucursal(
        id_sucursal=11, nombre="Sucursal Norte",
        direccion="Zona 3", estado="Activa",
    )
    db.add_all([base_gt, otro_gt])

    producto_a = Producto(id_producto=10, id_subcategoria=1, id_unidad=1, nombre="Galleta Soda", estado="Activo")
    prodb = Producto(id_producto=11, id_subcategoria=1, id_unidad=1, nombre="Aceite 1L", estado="Activo")
    db.add_all([producto_a, prodb])

    var_a = VarianteProducto(
        id_variante=10, id_producto=10, codigo_barras="7501000000010",
        precio_detalle=Decimal("6.00"), precio_mayoreo=Decimal("5.00"),
        costo_promedio=Decimal("4.00"),
    )
    var_b = VarianteProducto(
        id_variante=11, id_producto=11, codigo_barras="7501000000011",
        precio_detalle=Decimal("45.00"), precio_mayoreo=Decimal("42.00"),
        costo_promedio=Decimal("38.00"),
    )
    db.add_all([var_a, var_b])

    inv_a = InventarioSucursal(
        id_inventario=10, id_variante=10, id_sucursal=10,
        stock_actual=2, stock_minimo=10, fecha_actualizacion=inicio_hoy,
    )
    db.add(inv_a)

    turno = TurnoCaja(
        id_turno=10, id_caja=10, id_usuario=10,
        monto_apertura=Decimal("300.00"), fecha_apertura=inicio_hoy,
        estado="Abierto",
    )
    db.add(turno)

    # Dos ventas el día de hoy (suman Q630.00): una con efectivo, otra con transferencia.
    v1 = Venta(
        id_venta=10, id_turno=10, id_usuario=10,
        fecha_venta=inicio_hoy + timedelta(hours=10),
        subtotal=Decimal("290.00"), descuento_total=Decimal("0.00"),
        total_venta=Decimal("290.00"), estado="Completada",
    )
    v2 = Venta(
        id_venta=11, id_turno=10, id_usuario=10,
        fecha_venta=inicio_hoy + timedelta(hours=11),
        subtotal=Decimal("340.00"), descuento_total=Decimal("0.00"),
        total_venta=Decimal("340.00"), estado="Completada",
    )
    db.add_all([v1, v2])

    db.add_all([
        PagoVenta(id_venta=10, id_metodo_pago=1, monto_recibido=Decimal("300.00"), vuelto_entregado=Decimal("10.00")),
        PagoVenta(id_venta=11, id_metodo_pago=2, monto_recibido=Decimal("340.00"), vuelto_entregado=Decimal("0.00")),
    ])
    db.add_all([
        DetalleVenta(id_venta=10, id_variante=10, cantidad=3, precio_unitario=Decimal("6.00"), descuento_item=Decimal("0.00"), subtotal=Decimal("290.00")),
        DetalleVenta(id_venta=11, id_variante=11, cantidad=1, precio_unitario=Decimal("45.00"), descuento_item=Decimal("0.00"), subtotal=Decimal("340.00")),
    ])

    proveedor = Proveedor(
        id_proveedor=10, nombre_contacto="Carlos", distribuidora="Distribuidora Norte",
        estado="Activo",
    )
    db.add(proveedor)

    orden = OrdenCompra(
        id_orden=10, id_proveedor=10, id_usuario=10,
        fecha_emision=inicio_hoy.date(), total_estimado=Decimal("250.00"), estado="Emitida",
    )
    db.add(orden)

    traslado = TrasladoInventario(
        id_traslado=10, id_variante=10, id_sucursal_origen=10, id_sucursal_destino=11,
        cantidad=4, fecha_traslado=inicio_hoy, estado="En tránsito",
        id_usuario_envia=10,
    )
    db.add(traslado)
    await db.flush()


async def test_dashboard_repository_metrics_con_datos(db_session):
    await _seed_metrics(db_session)
    repo = DashboardRepositoryImpl(db_session)

    ventas = await repo.get_ventas_hoy()
    assert ventas[1] == 1 and ventas[0] == Decimal("100.00")
    assert await repo.count_stock_critico() == 1

    compras = await repo.get_compras_mes()
    assert compras[1] == 2 and compras[0] == Decimal("310.00")
    assert await repo.count_turnos_activos() == 1


async def test_dashboard_repository_metrics_vacias(db_session):
    repo = DashboardRepositoryImpl(db_session)

    ventas = await repo.get_ventas_hoy()
    assert ventas == (Decimal("0"), 0)
    assert await repo.count_stock_critico() == 0
    compras = await repo.get_compras_mes()
    assert compras == (Decimal("0"), 0)
    assert await repo.count_turnos_activos() == 0


async def test_dashboard_service_get_resumen(db_session):
    await _seed_metrics(db_session)
    service = ConcreteDashboardService(DashboardRepositoryImpl(db_session))

    resumen = await service.get_resumen(user_id=1)
    assert resumen.ventas_hoy.total == Decimal("100.00")
    assert resumen.ventas_hoy.cantidad == 1
    assert resumen.stock_critico == 1
    assert resumen.compras_mes.total == Decimal("310.00")
    assert resumen.compras_mes.cantidad == 2
    assert resumen.turnos_activos == 1
    assert resumen.turno_actual is not None
    assert resumen.turno_actual.estado == "Abierto"


async def test_dashboard_resumen_sin_datos(db_session):
    """Estado vacío (0 ventas): el panel devuelve ceros y listas vacías sin fallar."""
    service = ConcreteDashboardService(DashboardRepositoryImpl(db_session))
    resumen = await service.get_resumen(user_id=1)

    assert resumen.ventas_hoy.total == Decimal("0.00")
    assert resumen.ventas_hoy.cantidad == 0
    assert resumen.ventas_hoy.ticket_promedio == Decimal("0.00")
    assert resumen.turno_actual is None
    assert resumen.ventas_por_metodo == []
    assert resumen.mermas_mes == Decimal("0.00")
    assert len(resumen.ventas_7dias) == 7
    assert all(d.total == Decimal("0.00") for d in resumen.ventas_7dias)
    assert resumen.top_productos == []
    assert resumen.stock_critico_lista == []
    assert resumen.ordenes_pendientes == []
    assert resumen.traslados_pendientes == []
    assert resumen.ultimas_ventas == []


async def test_dashboard_resumen_dos_ventas_q630(db_session):
    """Escenario realista: 2 ventas por Q630, turno abierto, método de pago,
    top productos, stock crítico y pendientes."""
    await _seed_caja_completa(db_session)
    service = ConcreteDashboardService(DashboardRepositoryImpl(db_session))
    resumen = await service.get_resumen(user_id=10)

    assert resumen.ventas_hoy.total == Decimal("630.00")
    assert resumen.ventas_hoy.cantidad == 2
    assert resumen.ventas_hoy.ticket_promedio == Decimal("315.00")

    metodos = {m.nombre: m.total for m in resumen.ventas_por_metodo}
    assert metodos.get("Efectivo") == Decimal("290.00")
    assert metodos.get("Transferencia") == Decimal("340.00")

    assert resumen.turno_actual is not None
    assert resumen.turno_actual.cajero == "Ana Vendedora"
    assert resumen.turno_actual.monto_apertura == Decimal("300.00")

    nombres_top = {p.nombre for p in resumen.top_productos}
    assert "Galleta Soda" in nombres_top and "Aceite 1L" in nombres_top
    by_nombre = {p.nombre: p for p in resumen.top_productos}
    assert by_nombre["Galleta Soda"].cantidad == 3

    assert len(resumen.stock_critico_lista) == 1
    assert resumen.stock_critico_lista[0].producto == "Galleta Soda"
    assert resumen.stock_critico_lista[0].stock_actual == 2

    assert len(resumen.ordenes_pendientes) == 1
    orden = resumen.ordenes_pendientes[0]
    assert orden.proveedor == "Distribuidora Norte"
    assert orden.estado == "Emitida"

    assert len(resumen.traslados_pendientes) == 1
    traslado = resumen.traslados_pendientes[0]
    assert traslado.estado == "En tránsito"
    assert traslado.origen == "Sucursal Central"
    assert traslado.destino == "Sucursal Norte"

    assert len(resumen.ultimas_ventas) == 2
    folios = [v.folio for v in resumen.ultimas_ventas]
    assert folios == [11, 10]
    assert resumen.ultimas_ventas[0].vendedor == "Ana Vendedora"
    assert sum(v.total for v in resumen.ultimas_ventas) == Decimal("630.00")

    total_semana = sum(d.total for d in resumen.ventas_7dias)
    assert total_semana == Decimal("630.00")


async def test_dashboard_api_requires_auth(client):
    response = await client.get("/api/dashboard/resumen")
    assert response.status_code == 401


async def test_dashboard_api_resumen(client, db_session):
    await _seed_metrics(db_session)
    admin_user = Usuario(
        id_usuario=1, id_rol=1, nombre_completo="Administrador",
        username="admin", password_hash="x", estado="Activo",
    )
    app.dependency_overrides[get_current_user] = lambda: admin_user

    response = await client.get("/api/dashboard/resumen")
    assert response.status_code == 200
    data = response.json()
    assert data["ventas_hoy"]["total"] == "100.00"
    assert data["ventas_hoy"]["cantidad"] == 1
    assert data["stock_critico"] == 1
    assert data["compras_mes"]["total"] == "310.00"
    assert data["compras_mes"]["cantidad"] == 2
    assert data["turnos_activos"] == 1
    assert len(data["ventas_7dias"]) == 7