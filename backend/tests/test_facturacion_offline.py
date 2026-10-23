import pytest
import uuid
from decimal import Decimal
from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    Usuario, Rol, Sucursal, Caja, TurnoCaja, Producto, VarianteProducto, InventarioSucursal,
    Venta, SyncQueue
)
from app.services.facturacion_offline_service import FacturacionOfflineService
from app.api.deps import UnitOfWork

pytestmark = pytest.mark.asyncio

async def _seed_data(db_session: AsyncSession):
    # 1. Rol y Usuario
    rol = Rol(id_rol=1, nombre="Cajero", descripcion="Caja", estado="Activo")
    db_session.add(rol)
    await db_session.flush()

    user = Usuario(id_usuario=1, id_rol=1, nombre_completo="Test User", username="testuser", password_hash="hash", estado="Activo")
    db_session.add(user)
    await db_session.flush()

    # 2. Sucursal, Caja y Turno
    sucursal = Sucursal(id_sucursal=1, nombre="Principal", direccion="Zona 1", telefono="123", estado="Activo")
    db_session.add(sucursal)
    await db_session.flush()

    caja = Caja(id_caja=1, id_sucursal=1, descripcion="Caja 1", estado="Activo")
    db_session.add(caja)
    await db_session.flush()

    turno = TurnoCaja(id_turno=1, id_caja=1, id_usuario=1, monto_apertura=Decimal("100.00"), fecha_apertura=datetime.utcnow(), estado="Abierto")
    db_session.add(turno)
    await db_session.flush()

    producto = Producto(id_producto=1, id_subcategoria=1, id_unidad=1, nombre="Regalo A", descripcion="Regalo", estado="Activo")
    db_session.add(producto)
    await db_session.flush()

    variante = VarianteProducto(id_variante=1, id_producto=1, codigo_barras="123", precio_detalle=Decimal("50.00"), precio_mayoreo=Decimal("40.00"), costo_promedio=Decimal("30.00"))
    db_session.add(variante)
    await db_session.flush()

    # Stock suficiente (10)
    inv = InventarioSucursal(id_inventario=1, id_variante=1, id_sucursal=1, stock_actual=10, stock_minimo=5)
    # Stock insuficiente (2) para otra variante
    variante2 = VarianteProducto(id_variante=2, id_producto=1, codigo_barras="456", precio_detalle=Decimal("50.00"), precio_mayoreo=Decimal("40.00"), costo_promedio=Decimal("30.00"))
    db_session.add(variante2)
    await db_session.flush()
    inv2 = InventarioSucursal(id_inventario=2, id_variante=2, id_sucursal=1, stock_actual=2, stock_minimo=5)
    
    db_session.add_all([inv, inv2])
    await db_session.commit()

async def test_venta_offline_genera_sync_queue(db_session: AsyncSession):
    """Prueba que una venta offline genera entrada en sync_queue con estado PENDIENTE."""
    await _seed_data(db_session)
    uow = UnitOfWork(db_session)
    service = FacturacionOfflineService(uow)

    # Simular venta offline
    venta_data = {
        "id_turno": 1,
        "id_usuario": 1,
        "subtotal": Decimal("50.00"),
        "descuento_total": Decimal("0.00"),
        "total_venta": Decimal("50.00"),
        "detalles": [
            {"id_variante": 1, "cantidad": 1, "precio_unitario": Decimal("50.00"), "subtotal": Decimal("50.00")}
        ]
    }

    # Procesar con flag offline
    venta = await service.procesar_venta(venta_data, is_online=False)

    # Verificar que se creó la venta
    assert venta.id_venta is not None
    assert venta.estado == "Completada"

    # Verificar que el inventario bajó de 10 a 9
    result_inv = await db_session.execute(select(InventarioSucursal).where(InventarioSucursal.id_variante == 1))
    inv = result_inv.scalar_one()
    assert inv.stock_actual == 9

    # Verificar que se insertó en sync_queue
    result_sync = await db_session.execute(select(SyncQueue).where(SyncQueue.entidad_id == venta.id_venta))
    sync_item = result_sync.scalar_one()

    assert sync_item.estado == "PENDIENTE"
    assert sync_item.entidad == "venta"
    assert sync_item.idempotency_key is not None
    assert len(str(sync_item.idempotency_key)) > 10  # is a UUID

async def test_sync_engine_procesa_cola(db_session: AsyncSession):
    """Prueba que la sincronización cambia el estado a SINCRONIZADO."""
    await _seed_data(db_session)
    uow = UnitOfWork(db_session)
    service = FacturacionOfflineService(uow)

    # Generar venta offline
    venta_data = {
        "id_turno": 1,
        "id_usuario": 1,
        "subtotal": Decimal("50.00"),
        "descuento_total": Decimal("0.00"),
        "total_venta": Decimal("50.00"),
        "detalles": [
            {"id_variante": 1, "cantidad": 1, "precio_unitario": Decimal("50.00"), "subtotal": Decimal("50.00")}
        ]
    }
    venta = await service.procesar_venta(venta_data, is_online=False)
    
    result_sync = await db_session.execute(select(SyncQueue).where(SyncQueue.entidad_id == venta.id_venta))
    sync_item = result_sync.scalar_one()
    assert sync_item.estado == "PENDIENTE"

    # Ejecutar sync_engine simulando que volvió la red
    await service.sync_pending_transactions()

    # Refrescar y validar
    await db_session.refresh(sync_item)
    assert sync_item.estado == "SINCRONIZADO"

async def test_venta_offline_rechazada_por_stock(db_session: AsyncSession):
    """Prueba estricta que rechaza la venta offline si no hay stock suficiente, usando bloqueo pesimista."""
    await _seed_data(db_session)
    uow = UnitOfWork(db_session)
    service = FacturacionOfflineService(uow)

    # Intentar comprar 5 unidades de la variante 2 (stock actual: 2)
    venta_data = {
        "id_turno": 1,
        "id_usuario": 1,
        "subtotal": Decimal("250.00"),
        "descuento_total": Decimal("0.00"),
        "total_venta": Decimal("250.00"),
        "detalles": [
            {"id_variante": 2, "cantidad": 5, "precio_unitario": Decimal("50.00"), "subtotal": Decimal("250.00")}
        ]
    }

    with pytest.raises(HTTPException) as excinfo:
        await service.procesar_venta(venta_data, is_online=False)

    await db_session.rollback()
    
    assert excinfo.value.status_code == 400
    assert "Stock insuficiente" in str(excinfo.value.detail)

    # Validar que no se creó venta ni entrada en sync_queue
    result_ventas = await db_session.execute(select(Venta))
    assert len(result_ventas.scalars().all()) == 0

    result_sync = await db_session.execute(select(SyncQueue))
    assert len(result_sync.scalars().all()) == 0
