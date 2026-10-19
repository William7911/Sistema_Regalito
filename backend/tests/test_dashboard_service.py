"""
Pruebas del Panel Principal (Dashboard):
  1. Repositorio: métricas agregadas reales sobre aiosqlite (ventas del día,
     stock crítico, compras del mes, turnos activos) y estados vacíos.
  2. Servicio: ensambla el resumen DTO con los valores de la BD.
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
)
from app.repositories.dashboard_repository import DashboardRepositoryImpl
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
    """Población controlada para validar cada métrica del dashboard."""
    hoy = datetime.now()
    turno_activo = TurnoCaja(
        id_caja=1, id_usuario=1, monto_apertura=Decimal("100.00"),
        fecha_apertura=hoy, estado="Abierto",
    )
    turno_cerrado = TurnoCaja(
        id_caja=2, id_usuario=2, monto_apertura=Decimal("50.00"),
        fecha_apertura=hoy, estado="Cerrado",
    )
    db.add_all([turno_activo, turno_cerrado])

    venta_hoy = Venta(
        id_turno=1, id_usuario=1, fecha_venta=hoy,
        subtotal=Decimal("100.00"), descuento_total=Decimal("0.00"),
        total_venta=Decimal("100.00"), estado="Completada",
    )
    venta_ayer = Venta(
        id_turno=1, id_usuario=1, fecha_venta=hoy - timedelta(days=1),
        subtotal=Decimal("50.00"), descuento_total=Decimal("0.00"),
        total_venta=Decimal("50.00"), estado="Completada",
    )
    venta_cancelada_hoy = Venta(
        id_turno=1, id_usuario=1, fecha_venta=hoy,
        subtotal=Decimal("999.00"), descuento_total=Decimal("0.00"),
        total_venta=Decimal("999.00"), estado="Cancelada",
    )
    db.add_all([venta_hoy, venta_ayer, venta_cancelada_hoy])

    inv_bajo = InventarioSucursal(
        id_variante=1, id_sucursal=1, stock_actual=3, stock_minimo=10,
        fecha_actualizacion=hoy,
    )
    inv_ok = InventarioSucursal(
        id_variante=2, id_sucursal=1, stock_actual=50, stock_minimo=10,
        fecha_actualizacion=hoy,
    )
    db.add_all([inv_bajo, inv_ok])

    compra_mes_1 = Compra(
        id_proveedor=1, id_usuario=1, numero_factura_proveedor="F2001",
        fecha_ingreso=date.today().replace(day=1),
        subtotal_mercaderia=Decimal("200.00"), gasto_flete=Decimal("10.00"),
        gasto_cargadores=Decimal("0.00"), total_compra=Decimal("210.00"),
    )
    compra_mes_2 = Compra(
        id_proveedor=1, id_usuario=1, numero_factura_proveedor="F2002",
        fecha_ingreso=date.today(),
        subtotal_mercaderia=Decimal("100.00"), gasto_flete=Decimal("0.00"),
        gasto_cargadores=Decimal("0.00"), total_compra=Decimal("100.00"),
    )
    db.add_all([compra_mes_1, compra_mes_2])
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

    resumen = await service.get_resumen()
    assert resumen.ventas_hoy.total == Decimal("100.00")
    assert resumen.ventas_hoy.cantidad == 1
    assert resumen.stock_critico == 1
    assert resumen.compras_mes.total == Decimal("310.00")
    assert resumen.compras_mes.cantidad == 2
    assert resumen.turnos_activos == 1


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