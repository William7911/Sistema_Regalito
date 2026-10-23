"""Pruebas del Servicio de Facturación Electrónica FEL.

Escenarios:
  - Éxito: el certificador responde y la factura queda "Certificada".
  - Rechazo fiscal (HTTP 400): no se registra factura (la venta se revierte vía UoW).
  - Timeout / caída de red: la venta NO se revierte y la factura queda en contingencia.
  - Validaciones locales: totales <= 0 y bloqueo de NIT "CF" en ventas > Q2,500.00.

El API del certificador se simula con httpx.MockTransport (sin red real).
"""
import pytest
import httpx
from decimal import Decimal
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy import select

from app.db.models import (
    Rol, Usuario, Sucursal, Caja, TurnoCaja, Venta, FacturaFel,
    Categoria, Subcategoria, UnidadMedida, Producto, VarianteProducto,
    InventarioSucursal, MetodoPago,
)
from app.services.fel_service import ConcreteFelService
from app.services.sale_service import ConcreteSaleService
from app.api.deps import UnitOfWork
from app.schemas import sale_schema

pytestmark = pytest.mark.asyncio


async def _seed_venta(db_session):
    rol = Rol(id_rol=1, nombre="Cajero", estado="Activo")
    usuario = Usuario(
        id_usuario=1, id_rol=1, nombre_completo="Cajero 1",
        username="cajero1", password_hash="h", estado="Activo",
    )
    sucursal = Sucursal(id_sucursal=1, nombre="Central", direccion="D1", telefono="T1", estado="Activa")
    caja = Caja(id_caja=1, id_sucursal=1, descripcion="Caja 1", estado="Activa")
    db_session.add_all([rol, usuario, sucursal, caja])
    await db_session.flush()

    turno = TurnoCaja(
        id_turno=1, id_caja=1, id_usuario=1, monto_apertura=Decimal("100.00"),
        fecha_apertura=datetime.now(), estado="Abierto",
    )
    db_session.add(turno)
    await db_session.flush()

    venta = Venta(
        id_venta=1, id_turno=1, id_usuario=1, fecha_venta=datetime.now(),
        subtotal=Decimal("100.00"), descuento_total=Decimal("0.00"),
        total_venta=Decimal("100.00"), estado="Completada",
    )
    db_session.add(venta)
    await db_session.commit()


def _make_service(uow, handler=None):
    if handler is None:
        return ConcreteFelService(uow), None
    transport = httpx.MockTransport(handler)
    client = httpx.AsyncClient(transport=transport)
    return ConcreteFelService(uow, client=client), client


async def test_emision_exitosa_guarda_dte_certificado(db_session, uow):
    """FEL con conexión: el certificador responde 200 y la factura queda Certificada."""
    await _seed_venta(db_session)

    def handler(request):
        return httpx.Response(
            200,
            json={"uuid": "60a1b2c3-0000-0000-0000-abc123def456", "serie": "FEL", "numero": "001", "fecha": "2026-10-13T10:00:00"},
        )

    service, client = _make_service(uow, handler)
    try:
        factura = await service.emitir_factura(
            id_venta=1,
            total=Decimal("100.00"),
            nit_receptor="123456-7",
            nombre_receptor="Maria Lopez",
        )
    finally:
        await client.aclose()

    assert factura.estado == "Certificada"
    assert factura.numero_autorizacion_sat == "60a1b2c3-0000-0000-0000-abc123def456"
    assert factura.numero_dte == "FEL-001"
    assert str(factura.total_facturado) == "100.00"
    assert factura.nit_receptor == "123456-7"

    # Confirmar persistencia en BD
    registro = (await db_session.execute(select(FacturaFel).where(FacturaFel.id_venta == 1))).scalar_one()
    assert registro.estado == "Certificada"


async def test_rechazo_fiscal_del_certificador_no_registra(db_session, uow):
    """Certificador responde 400: HTTPException 400 y NO hay registro en factura_fel."""
    await _seed_venta(db_session)

    def handler(request):
        return httpx.Response(400, json={"detail": "NIT del receptor inválido en SAT"})

    service, client = _make_service(uow, handler)
    try:
        with pytest.raises(HTTPException) as exc_info:
            await service.emitir_factura(
                id_venta=1,
                total=Decimal("100.00"),
                nit_receptor="999999-1",
                nombre_receptor="Receptor Fantasma",
            )
    finally:
        await client.aclose()

    assert exc_info.value.status_code == 400
    assert "Rechazado" in str(exc_info.value.detail)
    assert "NIT" in str(exc_info.value.detail)

    # No debe existir factura (ni siquiera en contingencia)
    result = await db_session.execute(select(FacturaFel))
    assert len(result.scalars().all()) == 0


async def test_timeout_genera_contingencia_sin_revertir_venta(db_session, uow):
    """Timeout del certificador: la venta NO se revierte y la factura queda Contingencia."""
    await _seed_venta(db_session)

    def handler(request):
        raise httpx.TimeoutException("simulated timeout", request=request)

    service, client = _make_service(uow, handler)
    try:
        factura = await service.emitir_factura(
            id_venta=1,
            total=Decimal("100.00"),
            nit_receptor="CF",
            nombre_receptor="Consumidor Final",
        )
    finally:
        await client.aclose()

    assert factura.estado == "Contingencia"
    assert factura.numero_autorizacion_sat is None
    assert factura.numero_dte is None

    # Persistida en BD para reintentar después
    registro = (await db_session.execute(select(FacturaFel).where(FacturaFel.id_venta == 1))).scalar_one()
    assert registro.estado == "Contingencia"


async def test_sin_certificador_configurado_genera_contingencia(db_session, uow):
    """Sin FEL_API_URL: la emisión no falla, se guarda como Contingencia (offline)."""
    await _seed_venta(db_session)
    service, _ = _make_service(uow, handler=None)

    factura = await service.emitir_factura(
        id_venta=1,
        total=Decimal("100.00"),
        nit_receptor="123456-7",
        nombre_receptor="Maria Lopez",
    )

    assert factura.estado == "Contingencia"
    registro = (await db_session.execute(select(FacturaFel).where(FacturaFel.id_venta == 1))).scalar_one()
    assert registro.estado == "Contingencia"


async def test_bloqueo_nit_cf_por_monto_mayor_2500(db_session, uow):
    """Regla SAT: CF prohibido para ventas > Q2,500.00. Detiene antes de contactar al certificador."""
    await _seed_venta(db_session)
    service, client = _make_service(uow, handler=lambda r: pytest.fail("No debe contactar al certificador"))

    try:
        with pytest.raises(HTTPException) as exc_info:
            await service.emitir_factura(
                id_venta=1,
                total=Decimal("3000.00"),
                nit_receptor="CF",
                nombre_receptor="",
            )
    finally:
        await client.aclose()

    assert exc_info.value.status_code == 400
    assert "Q2,500.00" in str(exc_info.value.detail)
    result = await db_session.execute(select(FacturaFel))
    assert len(result.scalars().all()) == 0


async def test_bloqueo_totales_invalidos(db_session, uow):
    """Total 0.00 bloqueado antes del certificador."""
    await _seed_venta(db_session)
    service, client = _make_service(uow, handler=lambda r: pytest.fail("No debe contactar al certificador"))

    try:
        with pytest.raises(HTTPException) as exc_info:
            await service.emitir_factura(
                id_venta=1,
                total=Decimal("0.00"),
                nit_receptor="123456-7",
                nombre_receptor="Maria Lopez",
            )
    finally:
        await client.aclose()

    assert exc_info.value.status_code == 400
    assert "mayores a cero" in str(exc_info.value.detail)
    result = await db_session.execute(select(FacturaFel))
    assert len(result.scalars().all()) == 0


async def test_reintento_de_contingencia_se_certifica(db_session, uow):
    """Una factura en contingencia puede reintentarse y quedar Certificada."""
    await _seed_venta(db_session)

    # Primera emisión: sin certificador -> contingencia
    service, _ = _make_service(uow, handler=None)
    factura = await service.emitir_factura(
        id_venta=1, total=Decimal("100.00"), nit_receptor="123456-7", nombre_receptor="Maria Lopez",
    )
    assert factura.estado == "Contingencia"

    # Reintento con certificador OK -> certificación
    def handler(request):
        return httpx.Response(200, json={"uuid": "abc-123", "serie": "FEL", "numero": "002"})

    service2, client = _make_service(uow, handler)
    try:
        certificada = await service2.reintentar_certificacion(1)
    finally:
        await client.aclose()

    assert certificada.estado == "Certificada"
    assert certificada.numero_autorizacion_sat == "abc-123"
    assert certificada.numero_dte == "FEL-002"


async def _seed_venta_con_inventario(db_session):
    rol = Rol(id_rol=1, nombre="Cajero", estado="Activo")
    usuario = Usuario(
        id_usuario=1, id_rol=1, nombre_completo="Cajero 1",
        username="cajero1", password_hash="h", estado="Activo",
    )
    sucursal = Sucursal(id_sucursal=1, nombre="Central", direccion="D1", telefono="T1", estado="Activa")
    caja = Caja(id_caja=1, id_sucursal=1, descripcion="Caja 1", estado="Activa")
    cat = Categoria(id_categoria=1, nombre="General", estado="Activo")
    subcat = Subcategoria(id_subcategoria=1, id_categoria=1, nombre="Subgen")
    unidad = UnidadMedida(id_unidad=1, codigo="UND", descripcion="Unidad")
    metodo = MetodoPago(id_metodo_pago=1, nombre="Efectivo")
    db_session.add_all([rol, usuario, sucursal, caja, cat, subcat, unidad, metodo])
    await db_session.flush()

    producto = Producto(id_producto=1, id_subcategoria=1, id_unidad=1, nombre="Regalo", estado="Activo")
    db_session.add(producto)
    await db_session.flush()

    variante = VarianteProducto(
        id_variante=1, id_producto=1, precio_detalle=Decimal("10.00"),
        precio_mayoreo=Decimal("8.00"), costo_promedio=Decimal("5.00"),
    )
    db_session.add(variante)
    await db_session.flush()

    inventario = InventarioSucursal(
        id_inventario=1, id_variante=1, id_sucursal=1, stock_actual=50, stock_minimo=5,
    )
    db_session.add(inventario)

    turno = TurnoCaja(
        id_turno=1, id_caja=1, id_usuario=1, monto_apertura=Decimal("100.00"),
        fecha_apertura=datetime.now(), estado="Abierto",
    )
    db_session.add(turno)
    await db_session.commit()
    return turno


async def test_integracion_venta_con_fel_caido_no_revierte_venta(db_session, uow):
    """Integración sale_service + FEL: si el certificador cae, la venta se confirma,
    el stock se descuenta y factura_fel queda en Contingencia (misma transacción)."""
    turno = await _seed_venta_con_inventario(db_session)

    payload = sale_schema.SaleCreate(
        id_sucursal=1,
        nit_receptor="123456-7",
        nombre_receptor="Maria Lopez",
        items=[sale_schema.SaleItemCreate(id_variante=1, cantidad=2)],
        pagos=[sale_schema.PaymentCreate(id_metodo_pago=1, monto_recibido=Decimal("20.00"))],
    )
    service = ConcreteSaleService(uow)
    sale = await service.registrar_venta(payload, user_id=1, active_shift=turno)

    # La venta se confirmó
    assert sale.total_venta == Decimal("20.00")

    # Factura registrada en contingencia bajo la MISMA transacción
    registro = (await db_session.execute(select(FacturaFel))).scalar_one()
    assert registro.id_venta == sale.id_venta
    assert registro.estado == "Contingencia"

    # Stock descontado (50 -> 48), la venta NO se revierte
    inv = await uow.sales.get_inventario(1, 1)
    assert inv.stock_actual == 48
