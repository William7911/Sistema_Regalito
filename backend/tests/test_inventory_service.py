import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from sqlalchemy import select

from app.db.models import Usuario, Rol, Sucursal, Categoria, Subcategoria, UnidadMedida, Producto, VarianteProducto, InventarioSucursal, BitacoraAuditoria, AlertaStock
from app.services.inventory_service import ConcreteInventoryService
from app.api.deps import UnitOfWork
from app.schemas.inventory_schema import InventoryUpdate, StockAdjustment

pytestmark = pytest.mark.asyncio

async def _seed_inventory_data(db_session: AsyncSession):
    # 1. Rol y Usuario
    rol_bodeguero = Rol(id_rol=1, nombre="Bodeguero", descripcion="Bodeguero", estado="Activo")
    db_session.add(rol_bodeguero)
    await db_session.flush()

    user = Usuario(id_usuario=1, id_rol=1, nombre_completo="Test User", username="bodeguero", password_hash="hash", estado="Activo")
    db_session.add(user)
    await db_session.flush()

    # 2. Sucursal y Catálogo
    sucursal = Sucursal(id_sucursal=1, nombre="Principal", direccion="Zona 1", estado="Activo")
    db_session.add(sucursal)
    await db_session.flush()

    cat = Categoria(id_categoria=1, nombre="Cat1", estado="Activo")
    db_session.add(cat)
    await db_session.flush()

    subcat = Subcategoria(id_subcategoria=1, id_categoria=1, nombre="SubCat1")
    db_session.add(subcat)
    await db_session.flush()

    unidad = UnidadMedida(id_unidad=1, codigo="U", descripcion="Unidad")
    db_session.add(unidad)
    await db_session.flush()

    producto = Producto(id_producto=1, id_subcategoria=1, id_unidad=1, nombre="Producto A", estado="Activo")
    db_session.add(producto)
    await db_session.flush()

    variante = VarianteProducto(id_variante=1, id_producto=1, codigo_barras="123", precio_detalle=10, precio_mayoreo=8, costo_promedio=5)
    db_session.add(variante)
    await db_session.flush()

    # 3. Inventario
    inv = InventarioSucursal(id_inventario=1, id_variante=1, id_sucursal=1, stock_actual=20, stock_minimo=5)
    db_session.add(inv)
    await db_session.commit()

async def test_update_inventory_stock_minimo(db_session: AsyncSession):
    await _seed_inventory_data(db_session)
    uow = UnitOfWork(db_session)
    service = ConcreteInventoryService(uow)
    user = await db_session.get(Usuario, 1)

    update_data = InventoryUpdate(stock_minimo=15)
    result = await service.update_inventory(1, update_data, user)

    assert result.stock_minimo == 15

    # Verificar BD
    db_item = await db_session.get(InventarioSucursal, 1)
    assert db_item.stock_minimo == 15

    # Verificar Auditoría
    auditoria = (await db_session.execute(select(BitacoraAuditoria))).scalars().all()
    assert len(auditoria) == 1
    assert auditoria[0].accion == "EDITAR"

async def test_adjust_stock_success_with_alert(db_session: AsyncSession):
    await _seed_inventory_data(db_session)
    uow = UnitOfWork(db_session)
    service = ConcreteInventoryService(uow)
    user = await db_session.get(Usuario, 1)

    # Restar 16 para que quede en 4 (por debajo de stock_minimo = 5)
    adj_data = StockAdjustment(cantidad=-16, motivo="Merma reportada")
    result = await service.adjust_stock(1, adj_data, user)

    assert result.stock_actual == 4

    # Verificar BD
    db_item = await db_session.get(InventarioSucursal, 1)
    assert db_item.stock_actual == 4

    # Verificar Alerta
    alertas = (await db_session.execute(select(AlertaStock))).scalars().all()
    assert len(alertas) == 1
    assert "Stock bajo" in alertas[0].mensaje
    assert alertas[0].estado == "Pendiente"

    # Verificar Auditoría
    auditoria = (await db_session.execute(select(BitacoraAuditoria))).scalars().all()
    assert len(auditoria) == 1
    assert "Merma reportada" in auditoria[0].descripcion

async def test_get_alerts_solo_pendientes_enriquecidas(db_session: AsyncSession):
    await _seed_inventory_data(db_session)

    alerta_pendiente = AlertaStock(
        id_alerta=1, id_inventario=1,
        mensaje="Producto A por debajo del stock mínimo",
        fecha_generacion=datetime.utcnow(),
        estado="Pendiente",
    )
    alerta_atendida = AlertaStock(
        id_alerta=2, id_inventario=1,
        mensaje="Producto A por debajo del stock mínimo",
        fecha_generacion=datetime.utcnow(),
        estado="Atendida",
    )
    db_session.add_all([alerta_pendiente, alerta_atendida])
    await db_session.commit()

    uow = UnitOfWork(db_session)
    service = ConcreteInventoryService(uow)

    alertas = await service.get_alerts()
    assert len(alertas) == 1
    assert alertas[0].estado == "Pendiente"
    assert alertas[0].producto_nombre == "Producto A"
    assert alertas[0].variante_sku == "123"
    assert alertas[0].stock_actual == 20
    assert alertas[0].stock_minimo == 5

async def test_adjust_stock_negative_triggers_rollback(db_session: AsyncSession):
    await _seed_inventory_data(db_session)
    uow = UnitOfWork(db_session)
    service = ConcreteInventoryService(uow)
    user = await db_session.get(Usuario, 1)

    # Restar 25 para provocar stock negativo
    adj_data = StockAdjustment(cantidad=-25, motivo="Ajuste error")

    with pytest.raises(HTTPException) as excinfo:
        await service.adjust_stock(1, adj_data, user)
    
    assert excinfo.value.status_code == 400
    assert "resultaría en stock negativo" in str(excinfo.value.detail)

    # ASERCIÓN DURA DE ROLLBACK: El stock no debe haber cambiado
    await db_session.rollback() # Limpiar estado actual de la sesión transaccional del test
    db_item = await db_session.get(InventarioSucursal, 1)
    assert db_item.stock_actual == 20  # El valor original

    # Auditoría no debe existir debido al rollback
    auditoria = (await db_session.execute(select(BitacoraAuditoria))).scalars().all()
    assert len(auditoria) == 0
