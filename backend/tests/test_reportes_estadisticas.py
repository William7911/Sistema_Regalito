import pytest
from datetime import date, datetime
from decimal import Decimal
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.db.database import get_db
from app.core import security
from app.db.models import (
    Categoria,
    Cliente,
    Compra,
    DetalleMerma,
    DetalleVenta,
    InventarioSucursal,
    Merma,
    MotivoMerma,
    Permiso,
    Producto,
    Proveedor,
    Rol,
    RolPermiso,
    Subcategoria,
    Sucursal,
    TipoCliente,
    TurnoCaja,
    UnidadMedida,
    Usuario,
    VarianteProducto,
    Venta,
    Caja,
)
from app.services.reporte_service import ReportesService


async def _seed_estadisticas(db_session):
    """Crea el grafo de dependencias + datos para las estadísticas.

    Rango objetivo de la prueba: 2026-10-23 (fecha local de Guatemala).
    Las ventas nocturnas se guardan en UTC el 24/10 (02:39 y 03:40), lo que
    equivale a las 20:39 y 21:40 del 23/10 en hora local.
    """
    sucursal = Sucursal(id_sucursal=50, nombre="Sucursal Stats", direccion="Dir 50", telefono="555", estado="Activo")
    caja = Caja(id_caja=50, id_sucursal=50, descripcion="Caja Stats", estado="Activo")
    rol = Rol(id_rol=50, nombre="Administradora", descripcion="Admin", estado="Activo")
    perm = Permiso(id_permiso=150, modulo="Reportes", codigo="REPORTE_VER", descripcion="Ver reportes")
    db_session.add_all([sucursal, caja, rol, perm])
    await db_session.flush()
    db_session.add(RolPermiso(id_rol=50, id_permiso=150))
    await db_session.flush()

    usuario = Usuario(
        id_usuario=50,
        id_rol=50,
        nombre_completo="Doña Admin Stats",
        username="admin_stats",
        password_hash=security.get_password_hash("pass123"),
        estado="Activo",
    )
    db_session.add(usuario)
    await db_session.flush()

    turno = TurnoCaja(
        id_turno=50,
        id_caja=50,
        id_usuario=50,
        monto_apertura=Decimal("500.00"),
        fecha_apertura=datetime(2026, 10, 23, 14, 0, 0),
        estado="Abierto",
    )
    db_session.add(turno)
    await db_session.flush()

    tipo_cli = TipoCliente(id_tipo_cliente=50, nombre="General", estado="Activo")
    db_session.add(tipo_cli)
    await db_session.flush()

    cli_a = Cliente(id_cliente=50, id_tipo_cliente=50, nit="C1", nombre_comercial="Cliente Alfa", estado="Activo")
    cli_b = Cliente(id_cliente=51, id_tipo_cliente=50, nit="C2", nombre_comercial="Cliente Beta", estado="Activo")
    db_session.add_all([cli_a, cli_b])
    await db_session.flush()

    cat = Categoria(id_categoria=50, nombre="Bebidas", estado="Activo")
    subcat = Subcategoria(id_subcategoria=50, id_categoria=50, nombre="Gaseosas")
    unidad = UnidadMedida(id_unidad=50, codigo="UND", descripcion="Unidad")
    motivo = MotivoMerma(id_motivo=50, descripcion="Expirado")
    db_session.add_all([cat, subcat, unidad, motivo])
    await db_session.flush()

    prod_vendido = Producto(id_producto=50, id_subcategoria=50, id_unidad=50, nombre="Coca Cola", estado="Activo")
    prod_estancado = Producto(id_producto=51, id_subcategoria=50, id_unidad=50, nombre="Pan Francés", estado="Activo")
    db_session.add_all([prod_vendido, prod_estancado])
    await db_session.flush()

    var_vendido = VarianteProducto(
        id_variante=50, id_producto=50,
        precio_detalle=Decimal("35.00"), precio_mayoreo=Decimal("30.00"), costo_promedio=Decimal("20.00"),
    )
    var_estancado = VarianteProducto(
        id_variante=51, id_producto=51,
        precio_detalle=Decimal("5.00"), precio_mayoreo=Decimal("4.00"), costo_promedio=Decimal("4.00"),
    )
    db_session.add_all([var_vendido, var_estancado])
    await db_session.flush()

    # Inventario: la variante vendida tiene stock, la estancada no se vendió.
    inv_vendido = InventarioSucursal(id_variante=50, id_sucursal=50, stock_actual=8, stock_minimo=2)
    inv_estancado = InventarioSucursal(id_variante=51, id_sucursal=50, stock_actual=5, stock_minimo=1)
    db_session.add_all([inv_vendido, inv_estancado])
    await db_session.flush()

    # Ventas NOCTURNAS (UTC del 24/10 = local 23/10 por UTC-6).
    v1 = Venta(
        id_venta=501, id_turno=50, id_usuario=50, id_cliente=50,
        fecha_venta=datetime(2026, 10, 24, 2, 39, 24),
        subtotal=Decimal("290.00"), descuento_total=Decimal("0.00"), total_venta=Decimal("290.00"),
        estado="Completada",
    )
    v2 = Venta(
        id_venta=502, id_turno=50, id_usuario=50, id_cliente=51,
        fecha_venta=datetime(2026, 10, 24, 3, 40, 12),
        subtotal=Decimal("340.00"), descuento_total=Decimal("0.00"), total_venta=Decimal("340.00"),
        estado="Completada",
    )
    # Ventas ANULADA del mismo rango (no debe sumar a ingresos) y fuera del rango.
    v_anulada = Venta(
        id_venta=503, id_turno=50, id_usuario=50, id_cliente=50,
        fecha_venta=datetime(2026, 10, 23, 17, 0, 0),
        subtotal=Decimal("500.00"), descuento_total=Decimal("0.00"), total_venta=Decimal("500.00"),
        estado="Anulada",
    )
    v_fuera = Venta(
        id_venta=504, id_turno=50, id_usuario=50, id_cliente=50,
        fecha_venta=datetime(2026, 10, 22, 18, 0, 0),
        subtotal=Decimal("100.00"), descuento_total=Decimal("0.00"), total_venta=Decimal("100.00"),
        estado="Completada",
    )
    db_session.add_all([v1, v2, v_anulada, v_fuera])
    await db_session.flush()

    db_session.add_all([
        DetalleVenta(id_detalle_venta=5010, id_venta=501, id_variante=50, cantidad=10, precio_unitario=Decimal("29.00"), descuento_item=Decimal("0.00"), subtotal=Decimal("290.00")),
        DetalleVenta(id_detalle_venta=5020, id_venta=502, id_variante=50, cantidad=10, precio_unitario=Decimal("34.00"), descuento_item=Decimal("0.00"), subtotal=Decimal("340.00")),
    ])
    await db_session.flush()

    # Merma del rango (2 detalles) + merma fuera del rango (no debe contar).
    merma = Merma(id_merma=50, id_sucursal=50, id_usuario=50, fecha_merma=datetime(2026, 10, 23, 18, 0, 0))
    merma_fuera = Merma(id_merma=51, id_sucursal=50, id_usuario=50, fecha_merma=datetime(2026, 10, 22, 15, 0, 0))
    db_session.add_all([merma, merma_fuera])
    await db_session.flush()

    db_session.add_all([
        DetalleMerma(id_detalle_merma=5001, id_merma=50, id_variante=50, id_motivo=50, cantidad=2, costo_perdida=Decimal("15.50")),
        DetalleMerma(id_detalle_merma=5002, id_merma=50, id_variante=50, id_motivo=50, cantidad=1, costo_perdida=Decimal("10.00")),
        DetalleMerma(id_detalle_merma=5003, id_merma=51, id_variante=50, id_motivo=50, cantidad=1, costo_perdida=Decimal("99.00")),
    ])
    await db_session.flush()

    prov1 = Proveedor(id_proveedor=50, nombre_contacto="Pedro", distribuidora="Distribuidora Uno", telefono="111", estado="Activo")
    prov2 = Proveedor(id_proveedor=51, nombre_contacto="Luis", distribuidora="Distribuidora Dos", telefono="222", estado="Activo")
    db_session.add_all([prov1, prov2])
    await db_session.flush()

    compra = Compra(
        id_compra=50, id_proveedor=50, id_usuario=50, numero_factura_proveedor="F-1",
        fecha_ingreso=date(2026, 10, 23),
        subtotal_mercaderia=Decimal("1100.00"), gasto_flete=Decimal("50.00"), gasto_cargadores=Decimal("50.00"),
        total_compra=Decimal("1200.00"),
    )
    compra_fuera = Compra(
        id_compra=51, id_proveedor=51, id_usuario=50, numero_factura_proveedor="F-2",
        fecha_ingreso=date(2026, 10, 21),
        subtotal_mercaderia=Decimal("999.00"), gasto_flete=Decimal("0.00"), gasto_cargadores=Decimal("0.00"),
        total_compra=Decimal("999.00"),
    )
    db_session.add_all([compra, compra_fuera])
    await db_session.commit()


@pytest.mark.asyncio
async def test_kpi_totales_sum_y_filtrado_del_rango(db_session, uow):
    """Verifica los totales SUM de KPIs estrictamente dentro del rango local:
    se ignoran ventas anuladas, mermas y compras fuera del período, y el
    conteo de mermas usa DISTINCT(id_merma)."""
    await _seed_estadisticas(db_session)
    service = ReportesService(uow)

    kpi = await service.obtener_kpi(date(2026, 10, 23), date(2026, 10, 23), user_id=50)

    assert kpi.ventas == Decimal("630.00")          # 290 + 340 (anulada y 22/10 excluidas)
    assert kpi.count_ventas == 2
    assert kpi.mermas == Decimal("25.50")            # 15.50 + 10.00
    assert kpi.count_mermas == 1                    # una sola merma (DISTINCT)
    assert kpi.compras == Decimal("1200.00")
    assert kpi.count_compras == 1


@pytest.mark.asyncio
async def test_grafica_tendencia_agrupa_por_dia_local(db_session, uow):
    """La tendencia agrupa en el día calendario de Guatemala (UTC-6): las
    ventas nocturnas guardadas en UTC del 24/10 aparecen como 2026-10-23."""
    await _seed_estadisticas(db_session)
    service = ReportesService(uow)

    grafica = await service.obtener_grafica("tendencia", date(2026, 10, 23), date(2026, 10, 23), user_id=50)

    assert grafica.tipo == "tendencia"
    assert grafica.etiquetas == ["2026-10-23"]
    assert grafica.valores == [Decimal("630.00")]


@pytest.mark.asyncio
async def test_grafica_categoria_dona_agrupa_ingresos(db_session, uow):
    await _seed_estadisticas(db_session)
    service = ReportesService(uow)

    grafica = await service.obtener_grafica("categoria", date(2026, 10, 23), date(2026, 10, 23), user_id=50)

    assert grafica.tipo == "categoria"
    assert grafica.etiquetas == ["Bebidas"]
    assert grafica.valores == [Decimal("630.00")]


@pytest.mark.asyncio
async def test_grafica_hora_cuenta_transacciones_por_hora_local(db_session, uow):
    """Conteo por franja horaria local: las ventas a las 02:39/03:40 UTC son
    las 20:39/21:40 en Guatemala. Las horas vacías se rellenan con 0."""
    await _seed_estadisticas(db_session)
    service = ReportesService(uow)

    grafica = await service.obtener_grafica("hora", date(2026, 10, 23), date(2026, 10, 23), user_id=50)

    assert grafica.tipo == "hora"
    assert len(grafica.etiquetas) == 24
    assert grafica.valores[20] == Decimal("1")
    assert grafica.valores[21] == Decimal("1")
    assert grafica.valores[11] == Decimal("0")  # la anulada no cuenta


@pytest.mark.asyncio
async def test_ranking_productos_orden_monto_desc_y_limite(db_session, uow):
    await _seed_estadisticas(db_session)
    service = ReportesService(uow)

    ranking = await service.obtener_ranking("productos", date(2026, 10, 23), date(2026, 10, 23), 5, user_id=50)

    assert ranking.tipo == "productos"
    assert len(ranking.items) == 1
    assert ranking.items[0].nombre == "Coca Cola"
    assert ranking.items[0].valor == Decimal("630.00")
    assert ranking.items[0].cantidad == 20


@pytest.mark.asyncio
async def test_ranking_clientes_orden_total_desc_y_limite(db_session, uow):
    await _seed_estadisticas(db_session)
    service = ReportesService(uow)

    ranking = await service.obtener_ranking("clientes", date(2026, 10, 23), date(2026, 10, 23), 1, user_id=50)

    assert ranking.tipo == "clientes"
    assert len(ranking.items) == 1
    assert ranking.items[0].nombre == "Cliente Beta"   # 340 > 290
    assert ranking.items[0].valor == Decimal("340.00")
    assert ranking.items[0].cantidad == 1


@pytest.mark.asyncio
async def test_ranking_estancados_productos_sin_ventas(db_session, uow):
    """Solo aparecen productos SIN ventas en el rango, valorizando el stock
    parado (stock_actual * costo_promedio)."""
    await _seed_estadisticas(db_session)
    service = ReportesService(uow)

    ranking = await service.obtener_ranking("estancados", date(2026, 10, 23), date(2026, 10, 23), 5, user_id=50)

    nombres = [item.nombre for item in ranking.items]
    assert "Pan Francés" in nombres
    assert "Coca Cola" not in nombres        # sí vendió dentro del rango
    pan = ranking.items[0]
    assert pan.valor == Decimal("20.00")       # 5 unidades * Q4.00
    assert pan.cantidad == 5


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
async def test_api_estadisticas_status_200(client, db_session):
    """Verifica que los 3 nuevos endpoints respondan 200 con el contrato JSON
    que consume el frontend (KPI, gráfica y rankings)."""
    await _seed_estadisticas(db_session)
    token = security.create_access_token({"sub": "admin_stats"})
    headers = {"Authorization": f"Bearer {token}"}
    qs = "fecha_inicio=2026-10-01&fecha_fin=2026-10-24"

    r_kpi = await client.get(f"/api/reportes/kpi?{qs}", headers=headers)
    assert r_kpi.status_code == 200
    kpi = r_kpi.json()
    assert set(kpi) == {"ventas", "count_ventas", "mermas", "count_mermas", "compras", "count_compras"}

    for tipo in ("tendencia", "categoria", "hora"):
        r_grafica = await client.get(f"/api/reportes/grafica?tipo={tipo}&{qs}", headers=headers)
        assert r_grafica.status_code == 200
        body = r_grafica.json()
        assert body["tipo"] == tipo
        assert isinstance(body["etiquetas"], list)
        assert isinstance(body["valores"], list)

    r_rank = await client.get(f"/api/reportes/ranking?tipo_reporte=productos&limite=10&{qs}", headers=headers)
    assert r_rank.status_code == 200
    rank = r_rank.json()
    assert rank["tipo"] == "productos"
    assert isinstance(rank["items"], list)
    if rank["items"]:
        assert set(rank["items"][0]) == {"nombre", "valor", "cantidad"}
