"""
Pruebas unitarias para el Servicio de Ventas (RF01 Bloqueo de POS, RF05 Mayoreo, Vuelto y Stock).
"""
import pytest
from decimal import Decimal
from datetime import datetime
from fastapi import HTTPException
from app.db.models import (
    Rol, Usuario, Sucursal, Categoria, Subcategoria, UnidadMedida,
    Producto, VarianteProducto, InventarioSucursal, Caja, TurnoCaja,
    MetodoPago, TipoCliente, Cliente
)
from app.services.sale_service import ConcreteSaleService
from app.schemas import sale_schema


@pytest.fixture
def sale_service(uow):
    return ConcreteSaleService(uow)


async def _seed_sale_data(db):
    rol = Rol(id_rol=1, nombre="Cajero", estado="Activo")
    usuario = Usuario(id_usuario=1, id_rol=1, nombre_completo="Cajero 1", username="cajero1", password_hash="h", estado="Activo")
    sucursal = Sucursal(id_sucursal=1, nombre="Central", direccion="D1", telefono="T1", estado="Activa")
    cat = Categoria(id_categoria=1, nombre="General", estado="Activo")
    subcat = Subcategoria(id_subcategoria=1, id_categoria=1, nombre="Subgen")
    unidad = UnidadMedida(id_unidad=1, codigo="UND", descripcion="Unidad")
    caja = Caja(id_caja=1, id_sucursal=1, descripcion="Caja 1", estado="Activa")
    metodo = MetodoPago(id_metodo_pago=1, nombre="Efectivo")
    tipo_cliente = TipoCliente(id_tipo_cliente=1, nombre="Minorista")

    db.add_all([rol, usuario, sucursal, cat, subcat, unidad, caja, metodo, tipo_cliente])
    await db.flush()

    producto = Producto(id_producto=1, id_subcategoria=1, id_unidad=1, nombre="Pelota Antiestrés", estado="Activo")
    db.add(producto)
    await db.flush()

    # Precio Detalle: Q10.00, Precio Mayoreo: Q8.00
    variante = VarianteProducto(
        id_variante=1,
        id_producto=1,
        precio_detalle=Decimal("10.00"),
        precio_mayoreo=Decimal("8.00"),
        costo_promedio=Decimal("5.00"),
    )
    db.add(variante)
    await db.flush()

    # Stock inicial = 50
    inventario = InventarioSucursal(
        id_inventario=1,
        id_variante=1,
        id_sucursal=1,
        stock_actual=50,
        stock_minimo=5,
    )
    db.add(inventario)

    # Turno abierto
    turno = TurnoCaja(
        id_turno=1,
        id_caja=1,
        id_usuario=1,
        monto_apertura=Decimal("100.00"),
        fecha_apertura=datetime.now(),
        estado="Abierto",
    )
    db.add(turno)
    await db.commit()
    return turno


@pytest.mark.asyncio
async def test_venta_minorista_precio_detalle(sale_service, db_session, uow):
    """Venta con cantidad < 6 aplica precio detalle regular."""
    turno = await _seed_sale_data(db_session)

    # Vender 2 unidades a Q10.00 = Q20.00. Paga Q20.00
    payload = sale_schema.SaleCreate(
        id_sucursal=1,
        items=[sale_schema.SaleItemCreate(id_variante=1, cantidad=2)],
        pagos=[sale_schema.PaymentCreate(id_metodo_pago=1, monto_recibido=Decimal("20.00"))],
    )
    sale = await sale_service.registrar_venta(payload, user_id=1, active_shift=turno)

    assert sale.subtotal == Decimal("20.00")
    assert sale.descuento_total == Decimal("0.00")
    assert sale.total_venta == Decimal("20.00")
    assert sale.cambio == Decimal("0.00")

    # Stock: 50 - 2 = 48
    inv = await uow.sales.get_inventario(1, 1)
    assert inv.stock_actual == 48


@pytest.mark.asyncio
async def test_venta_mayoreo_descuento_automatico(sale_service, db_session, uow):
    """RF05: Venta con cantidad >= 6 aplica automáticamente precio_mayoreo (Q8.00 en vez de Q10.00)."""
    turno = await _seed_sale_data(db_session)

    # Vender 6 unidades:
    # Subtotal bruto: 6 * Q10 = Q60.00
    # Descuento: 6 * (Q10 - Q8) = Q12.00
    # Total venta: 6 * Q8 = Q48.00
    # Paga con Q50.00 -> Vuelto: Q2.00
    payload = sale_schema.SaleCreate(
        id_sucursal=1,
        items=[sale_schema.SaleItemCreate(id_variante=1, cantidad=6)],
        pagos=[sale_schema.PaymentCreate(id_metodo_pago=1, monto_recibido=Decimal("50.00"))],
    )
    sale = await sale_service.registrar_venta(payload, user_id=1, active_shift=turno)

    assert sale.subtotal == Decimal("60.00")
    assert sale.descuento_total == Decimal("12.00")
    assert sale.total_venta == Decimal("48.00")
    assert sale.cambio == Decimal("2.00")

    # Stock: 50 - 6 = 44
    inv = await uow.sales.get_inventario(1, 1)
    assert inv.stock_actual == 44


@pytest.mark.asyncio
async def test_bloqueo_pos_sin_turno_abierto(sale_service, db_session):
    """RF01: No se puede vender si el turno de caja no está en estado 'Abierto'."""
    turno = await _seed_sale_data(db_session)
    turno.estado = "Cerrado"

    payload = sale_schema.SaleCreate(
        id_sucursal=1,
        items=[sale_schema.SaleItemCreate(id_variante=1, cantidad=1)],
        pagos=[sale_schema.PaymentCreate(id_metodo_pago=1, monto_recibido=Decimal("10.00"))],
    )

    with pytest.raises(HTTPException) as exc_info:
        await sale_service.registrar_venta(payload, user_id=1, active_shift=turno)

    assert exc_info.value.status_code == 403
    assert "Debe registrar el fondo inicial antes de vender" in exc_info.value.detail


@pytest.mark.asyncio
async def test_venta_pago_insuficiente_falla(sale_service, db_session):
    """El monto recibido debe cubrir el total de la venta."""
    turno = await _seed_sale_data(db_session)

    # Venta de Q20.00 pero cliente paga solo Q15.00
    payload = sale_schema.SaleCreate(
        id_sucursal=1,
        items=[sale_schema.SaleItemCreate(id_variante=1, cantidad=2)],
        pagos=[sale_schema.PaymentCreate(id_metodo_pago=1, monto_recibido=Decimal("15.00"))],
    )

    with pytest.raises(HTTPException) as exc_info:
        await sale_service.registrar_venta(payload, user_id=1, active_shift=turno)

    assert exc_info.value.status_code == 400
    assert "Monto de pago insuficiente" in exc_info.value.detail

