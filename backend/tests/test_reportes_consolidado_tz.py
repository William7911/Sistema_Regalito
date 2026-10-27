import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.db.database import get_db
from app.core import security
from app.db.models import (
    Rol,
    Usuario,
    Permiso,
    RolPermiso,
    Sucursal,
    Caja,
    TurnoCaja,
    Venta,
    Merma,
    DetalleMerma,
    Compra,
    Proveedor,
    Categoria,
    Subcategoria,
    UnidadMedida,
    Producto,
    VarianteProducto,
    MotivoMerma,
)
from app.services.reporte_service import ReportesService


@pytest.fixture
async def client(db_session):
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_consolidado_tz_guatemala_ventas_nocturnas_y_totales(db_session, uow):
    """
    Verifica que:
    1. Una venta registrada en la noche de Guatemala (ej. 23/10 a las 20:39 GT = 24/10 02:39 UTC)
       sea encontrada al filtrar fecha_inicio=23/10 y fecha_fin=23/10.
    2. No se lance MissingGreenlet al acceder a v.usuario (vendedor) gracias a selectinload.
    3. El DTO incluya totales calculados correctamente para ventas.
    """
    # 1. Configuración de dependencias
    sucursal = Sucursal(id_sucursal=10, nombre="Sucursal Central", direccion="Calle 1", telefono="123", estado="Activo")
    caja = Caja(id_caja=10, id_sucursal=10, descripcion="Caja 1", estado="Activo")
    rol = Rol(id_rol=10, nombre="Administradora", descripcion="Admin", estado="Activo")
    perm = Permiso(id_permiso=101, modulo="Reportes", codigo="REPORTE_VER", descripcion="Ver reportes")
    db_session.add_all([sucursal, caja, rol, perm])
    await db_session.flush()

    db_session.add(RolPermiso(id_rol=10, id_permiso=101))
    await db_session.flush()

    usuario = Usuario(
        id_usuario=10,
        id_rol=10,
        nombre_completo="Doña Martha Vendedora",
        username="martha_admin",
        password_hash=security.get_password_hash("pass123"),
        estado="Activo",
    )
    db_session.add(usuario)
    await db_session.flush()

    turno = TurnoCaja(
        id_turno=10,
        id_caja=10,
        id_usuario=10,
        monto_apertura=Decimal("100.00"),
        fecha_apertura=datetime(2026, 10, 23, 14, 0, 0),
        estado="Abierto",
    )
    db_session.add(turno)
    await db_session.flush()

    # Venta creada a las 20:39 hora Guatemala (UTC-6) -> 02:39 UTC del día siguiente
    fecha_utc_nocturna = datetime(2026, 10, 24, 2, 39, 24)
    v1 = Venta(
        id_venta=101,
        id_turno=10,
        id_usuario=10,
        fecha_venta=fecha_utc_nocturna,
        subtotal=Decimal("290.00"),
        descuento_total=Decimal("0.00"),
        total_venta=Decimal("290.00"),
        estado="Completada",
    )
    v2 = Venta(
        id_venta=102,
        id_turno=10,
        id_usuario=10,
        fecha_venta=datetime(2026, 10, 24, 2, 40, 12),
        subtotal=Decimal("340.00"),
        descuento_total=Decimal("0.00"),
        total_venta=Decimal("340.00"),
        estado="Completada",
    )
    db_session.add_all([v1, v2])
    await db_session.commit()

    service = ReportesService(uow)

    # Filtrar estrictamente por fecha local de Guatemala 2026-10-23
    f_inicio = date(2026, 10, 23)
    f_fin = date(2026, 10, 23)

    reporte = await service.obtener_consolidado(f_inicio, f_fin, user_id=10)

    # Ambas ventas deben entrar en el rango local de Guatemala del 23 de octubre
    assert len(reporte.ventas) == 2
    assert reporte.totales.ventas == Decimal("630.00")

    # Verificar mapeo defensivo de campos requeridos por el frontend
    v_item = reporte.ventas[0]
    assert v_item.vendedor == "Doña Martha Vendedora"
    assert v_item.total == Decimal("340.00")
    assert v_item.subtotal == Decimal("340.00")
    assert v_item.descuento == Decimal("0.00")
    assert v_item.estado == "Completada"
    assert v_item.fecha is not None


@pytest.mark.asyncio
async def test_consolidado_mermas_detalles_sin_missing_greenlet(db_session, uow):
    """
    Verifica que mermas con detalles no lancen MissingGreenlet y que el total
    se calcule a partir de los detalles.
    """
    sucursal = Sucursal(id_sucursal=20, nombre="Sucursal 2", direccion="Dir 2", telefono="456", estado="Activo")
    rol = Rol(id_rol=20, nombre="Admin Merma", descripcion="Admin", estado="Activo")
    perm = Permiso(id_permiso=102, modulo="Reportes", codigo="REPORTE_VER", descripcion="Ver reportes")
    db_session.add_all([sucursal, rol, perm])
    await db_session.flush()

    db_session.add(RolPermiso(id_rol=20, id_permiso=102))
    await db_session.flush()

    usuario = Usuario(
        id_usuario=20,
        id_rol=20,
        nombre_completo="Bodeguero Pepe",
        username="pepe_rep",
        password_hash=security.get_password_hash("pass123"),
        estado="Activo",
    )
    db_session.add(usuario)
    await db_session.flush()

    cat = Categoria(id_categoria=20, nombre="Cat", estado="Activo")
    subcat = Subcategoria(id_subcategoria=20, id_categoria=20, nombre="Subcat")
    unidad = UnidadMedida(id_unidad=20, codigo="UND", descripcion="Unidad")
    motivo = MotivoMerma(id_motivo=20, descripcion="Expirado")
    db_session.add_all([cat, subcat, unidad, motivo])
    await db_session.flush()

    prod = Producto(id_producto=20, id_subcategoria=20, id_unidad=20, nombre="Prod 20", estado="Activo")
    db_session.add(prod)
    await db_session.flush()

    var = VarianteProducto(
        id_variante=20,
        id_producto=20,
        precio_detalle=Decimal("15.00"),
        precio_mayoreo=Decimal("12.00"),
        costo_promedio=Decimal("10.00"),
    )
    db_session.add(var)
    await db_session.flush()

    # Merma en UTC
    merma = Merma(
        id_merma=20,
        id_sucursal=20,
        id_usuario=20,
        fecha_merma=datetime(2026, 10, 23, 18, 0, 0),
        observaciones="Productos dañados",
    )
    db_session.add(merma)
    await db_session.flush()

    det1 = DetalleMerma(id_detalle_merma=201, id_merma=20, id_variante=20, id_motivo=20, cantidad=2, costo_perdida=Decimal("15.50"))
    det2 = DetalleMerma(id_detalle_merma=202, id_merma=20, id_variante=20, id_motivo=20, cantidad=1, costo_perdida=Decimal("10.00"))
    db_session.add_all([det1, det2])
    await db_session.commit()

    service = ReportesService(uow)
    reporte = await service.obtener_consolidado(date(2026, 10, 23), date(2026, 10, 23), user_id=20)

    assert len(reporte.mermas) == 1
    assert reporte.totales.mermas == Decimal("25.50")
    assert reporte.mermas[0].total == Decimal("25.50")
    assert reporte.mermas[0].observaciones == "Productos dañados"


@pytest.mark.asyncio
async def test_api_reportes_vista_previa_status_200_con_totales(client, db_session):
    """
    Verifica que el endpoint HTTP /api/reportes/ responda 200 OK
    con el payload esperado por el frontend (totales, ventas con subtotal, total, etc.).
    """
    rol = Rol(id_rol=30, nombre="Admin API", estado="Activo")
    perm = Permiso(id_permiso=103, modulo="Reportes", codigo="REPORTE_VER", descripcion="Ver reportes")
    db_session.add_all([rol, perm])
    await db_session.flush()

    db_session.add(RolPermiso(id_rol=30, id_permiso=103))
    await db_session.flush()

    usuario = Usuario(
        id_usuario=30,
        id_rol=30,
        nombre_completo="Administradora General",
        username="admin_consolidado_api",
        password_hash=security.get_password_hash("pass123"),
        estado="Activo",
    )
    db_session.add(usuario)
    await db_session.commit()

    token = security.create_access_token({"sub": "admin_consolidado_api"})
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/reportes/?fecha_inicio=2026-10-01&fecha_fin=2026-10-24", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert "totales" in data
    assert "ventas" in data["totales"]
    assert "mermas" in data["totales"]
    assert "compras" in data["totales"]
    assert isinstance(data["ventas"], list)
    assert isinstance(data["mermas"], list)
    assert isinstance(data["compras"], list)
