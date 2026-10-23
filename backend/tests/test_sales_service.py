"""
Pruebas unitarias estrictas para el Servicio de Ventas.
Auditoría QA: Verificación de caminos felices, reglas de mayoreo, 
y aserciones estrictas de integridad de base de datos (rollback) ante fallas.
"""
import pytest
from decimal import Decimal
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy import select, func
from app.db.models import (
    Rol, Usuario, Sucursal, Categoria, Subcategoria, UnidadMedida,
    Producto, VarianteProducto, InventarioSucursal, Caja, TurnoCaja,
    MetodoPago, TipoCliente, Cliente, Venta
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
    """Venta con cantidad < 6 aplica precio detalle regular y persiste la venta."""
    turno = await _seed_sale_data(db_session)

    payload = sale_schema.SaleCreate(
        id_sucursal=1,
        items=[sale_schema.SaleItemCreate(id_variante=1, cantidad=2)],
        pagos=[sale_schema.PaymentCreate(id_metodo_pago=1, monto_recibido=Decimal("20.00"))],
    )
    sale = await sale_service.registrar_venta(payload, user_id=1, active_shift=turno)

    # Verificación de lógica de negocio (Totales)
    assert sale.subtotal == Decimal("20.00")
    assert sale.descuento_total == Decimal("0.00")
    assert sale.total_venta == Decimal("20.00")
    assert sale.cambio == Decimal("0.00")

    # Aserción ESTRICTA de BD: Inventario descontado
    inv = await uow.sales.get_inventario(1, 1)
    assert inv.stock_actual == 48

    # Aserción ESTRICTA de BD: Venta persistida
    ventas_creadas = (await db_session.execute(select(func.count(Venta.id_venta)))).scalar()
    assert ventas_creadas == 1


@pytest.mark.asyncio
async def test_venta_mayoreo_descuento_automatico(sale_service, db_session, uow):
    """RF05: Venta con cantidad >= 6 aplica automáticamente precio_mayoreo (Q8.00 en vez de Q10.00)."""
    turno = await _seed_sale_data(db_session)

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

    inv = await uow.sales.get_inventario(1, 1)
    assert inv.stock_actual == 44


@pytest.mark.asyncio
async def test_bloqueo_pos_sin_turno_abierto(sale_service, db_session, uow):
    """RF01: Turno inactivo bloquea la venta. Aserción de que NO mutó la BD."""
    turno = await _seed_sale_data(db_session)
    turno.estado = "Cerrado"

    payload = sale_schema.SaleCreate(
        id_sucursal=1,
        items=[sale_schema.SaleItemCreate(id_variante=1, cantidad=1)],
        pagos=[sale_schema.PaymentCreate(id_metodo_pago=1, monto_recibido=Decimal("10.00"))],
    )

    with pytest.raises(HTTPException) as exc_info:
        await sale_service.registrar_venta(payload, user_id=1, active_shift=turno)

    await db_session.rollback()

    assert exc_info.value.status_code == 403
    
    # ASERCIÓN ESTRICTA: El inventario no debió tocarse (sigue en 50)
    inv = await uow.sales.get_inventario(1, 1)
    assert inv.stock_actual == 50
    # ASERCIÓN ESTRICTA: No se guardó ninguna venta
    ventas = (await db_session.execute(select(func.count(Venta.id_venta)))).scalar()
    assert ventas == 0


@pytest.mark.asyncio
async def test_venta_pago_insuficiente_falla(sale_service, db_session, uow):
    """El pago insuficiente arroja 400. Asegurar que haya rollback en BD."""
    turno = await _seed_sale_data(db_session)

    payload = sale_schema.SaleCreate(
        id_sucursal=1,
        items=[sale_schema.SaleItemCreate(id_variante=1, cantidad=2)], # Q20.00
        pagos=[sale_schema.PaymentCreate(id_metodo_pago=1, monto_recibido=Decimal("15.00"))],
    )

    with pytest.raises(HTTPException) as exc_info:
        await sale_service.registrar_venta(payload, user_id=1, active_shift=turno)

    await db_session.rollback()

    assert exc_info.value.status_code == 400
    assert "insuficiente" in exc_info.value.detail.lower()

    # ASERCIÓN ESTRICTA: El inventario sigue intacto tras fallar validación de pago
    inv = await uow.sales.get_inventario(1, 1)
    assert inv.stock_actual == 50


@pytest.mark.asyncio
async def test_venta_falla_por_inventario_insuficiente(sale_service, db_session, uow):
    """Intentar vender más stock del que existe provoca HTTP 400 y no altera BD."""
    turno = await _seed_sale_data(db_session)

    payload = sale_schema.SaleCreate(
        id_sucursal=1,
        items=[sale_schema.SaleItemCreate(id_variante=1, cantidad=55)], # Stock es 50
        pagos=[sale_schema.PaymentCreate(id_metodo_pago=1, monto_recibido=Decimal("600.00"))],
    )

    with pytest.raises(HTTPException) as exc_info:
        await sale_service.registrar_venta(payload, user_id=1, active_shift=turno)

    await db_session.rollback()

    assert exc_info.value.status_code == 400
    assert "Stock insuficiente" in exc_info.value.detail
    
    # ASERCIÓN ESTRICTA: El inventario no quedó negativo, la transacción se deshizo
    inv = await uow.sales.get_inventario(1, 1)
    assert inv.stock_actual == 50


@pytest.mark.asyncio
async def test_venta_falla_por_variante_inexistente(sale_service, db_session, uow):
    """Variante fantasma devuelve 404 Not Found."""
    turno = await _seed_sale_data(db_session)

    payload = sale_schema.SaleCreate(
        id_sucursal=1,
        items=[sale_schema.SaleItemCreate(id_variante=999, cantidad=1)], 
        pagos=[sale_schema.PaymentCreate(id_metodo_pago=1, monto_recibido=Decimal("100.00"))],
    )

    with pytest.raises(HTTPException) as exc_info:
        await sale_service.registrar_venta(payload, user_id=1, active_shift=turno)

    # Simular el fin del request que aborta la transacción
    await db_session.rollback()

    assert exc_info.value.status_code == 404
    assert "variante" in exc_info.value.detail.lower() and "no existe" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_venta_cliente_inactivo_rechazada(sale_service, db_session, uow):
    """Punto 3: Un cliente inactivo no puede asignarse a una venta (HTTP 400)."""
    turno = await _seed_sale_data(db_session)

    # Crear cliente inactivo
    cliente_inactivo = Cliente(
        id_cliente=10,
        id_tipo_cliente=1,
        nit="123456-7",
        nombre_comercial="Cliente Desactivado",
        estado="Inactivo",
    )
    db_session.add(cliente_inactivo)
    await db_session.commit()

    payload = sale_schema.SaleCreate(
        id_sucursal=1,
        id_cliente=10,
        items=[sale_schema.SaleItemCreate(id_variante=1, cantidad=1)],
        pagos=[sale_schema.PaymentCreate(id_metodo_pago=1, monto_recibido=Decimal("10.00"))],
    )

    with pytest.raises(HTTPException) as exc_info:
        await sale_service.registrar_venta(payload, user_id=1, active_shift=turno)

    assert exc_info.value.status_code == 400
    assert "inactivo" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_venta_cliente_mayorista_aplica_precio_mayoreo(sale_service, db_session, uow):
    """Punto 4: Un cliente de tipo Mayorista recibe precio de mayoreo y descuento automático incluso con cantidad < 6."""
    turno = await _seed_sale_data(db_session)

    # Crear tipo Mayorista y cliente asociado
    tipo_mayoreo = TipoCliente(id_tipo_cliente=3, nombre="Mayorista", estado="Activo")
    db_session.add(tipo_mayoreo)
    await db_session.flush()

    cliente_mayorista = Cliente(
        id_cliente=20,
        id_tipo_cliente=3,
        nit="998877-6",
        nombre_comercial="Distribuidora El Éxito",
        estado="Activo",
    )
    db_session.add(cliente_mayorista)
    await db_session.commit()

    # Venta de solo 2 unidades (menor a 6, precio detalle = Q10.00, precio mayoreo = Q8.00)
    payload = sale_schema.SaleCreate(
        id_sucursal=1,
        id_cliente=20,
        items=[sale_schema.SaleItemCreate(id_variante=1, cantidad=2)],
        pagos=[sale_schema.PaymentCreate(id_metodo_pago=1, monto_recibido=Decimal("20.00"))],
    )

    sale = await sale_service.registrar_venta(payload, user_id=1, active_shift=turno)

    # Subtotal bruto = 2 * 10 = 20.00
    assert sale.subtotal == Decimal("20.00")
    # Descuento = 2 * (10 - 8) = 4.00
    assert sale.descuento_total == Decimal("4.00")
    # Total a pagar = 2 * 8 = 16.00
    assert sale.total_venta == Decimal("16.00")
    # Cambio = 20 - 16 = 4.00
    assert sale.cambio == Decimal("4.00")


