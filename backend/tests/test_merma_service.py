"""
Pruebas unitarias para el Módulo de Mermas de Inventario (RF10, Proceso 2).
"""
import pytest
from decimal import Decimal
from datetime import datetime
from fastapi import HTTPException
from app.db.models import (
    Rol, Usuario, Sucursal, Categoria, Subcategoria, UnidadMedida,
    Producto, VarianteProducto, InventarioSucursal, MotivoMerma
)
from app.services.merma_service import ConcreteMermaService
from app.schemas import merma_schema


@pytest.fixture
def merma_service(uow):
    return ConcreteMermaService(uow)


async def _seed_merma_data(db):
    rol = Rol(id_rol=1, nombre="Bodeguero", estado="Activo")
    usuario = Usuario(id_usuario=1, id_rol=1, nombre_completo="Bodeguero 1", username="bodega1", password_hash="h", estado="Activo")
    sucursal = Sucursal(id_sucursal=1, nombre="Sucursal Central", direccion="D1", telefono="T1", estado="Activa")
    cat = Categoria(id_categoria=1, nombre="Papelería", estado="Activo")
    subcat = Subcategoria(id_subcategoria=1, id_categoria=1, nombre="Cuadernos")
    unidad = UnidadMedida(id_unidad=1, codigo="UND", descripcion="Unidad")
    motivo = MotivoMerma(id_motivo=1, descripcion="Dañado por humedad")

    db.add_all([rol, usuario, sucursal, cat, subcat, unidad, motivo])
    await db.flush()

    producto = Producto(id_producto=1, id_subcategoria=1, id_unidad=1, nombre="Cuaderno 100 Hojas", estado="Activo")
    db.add(producto)
    await db.flush()

    variante = VarianteProducto(
        id_variante=1,
        id_producto=1,
        precio_detalle=Decimal("15.00"),
        precio_mayoreo=Decimal("12.00"),
        costo_promedio=Decimal("8.00"),
    )
    db.add(variante)
    await db.flush()

    # Stock inicial de 20 unidades
    inventario = InventarioSucursal(
        id_inventario=1,
        id_variante=1,
        id_sucursal=1,
        stock_actual=20,
        stock_minimo=5,
    )
    db.add(inventario)
    await db.commit()


@pytest.mark.asyncio
async def test_registrar_merma_exitoso_descarga_stock(merma_service, db_session, uow):
    """RF10: Una merma debe restar existencias de inventario_sucursal de manera atómica."""
    await _seed_merma_data(db_session)

    payload = merma_schema.MermaCreate(
        id_sucursal=1,
        observaciones="Caja rota por lluvia",
        detalles=[
            merma_schema.DetalleMermaCreate(id_variante=1, id_motivo=1, cantidad=5)
        ],
    )
    merma = await merma_service.registrar_merma(payload, user_id=1)

    assert merma.id_merma is not None
    assert len(merma.detalles) == 1
    assert merma.detalles[0].cantidad == 5
    assert merma.detalles[0].costo_perdida == Decimal("40.00")  # 5 * Q8.00

    # Verificar descargo atómico en BD: 20 iniciales - 5 mermadas = 15
    inv = await uow.mermas.get_inventario(1, 1)
    assert inv.stock_actual == 15


@pytest.mark.asyncio
async def test_registrar_merma_stock_insuficiente_falla(merma_service, db_session):
    """RF10: Intentar mermar más unidades de las disponibles en stock debe ser rechazado."""
    await _seed_merma_data(db_session)

    # Solicitar 25 unidades cuando solo hay 20
    payload = merma_schema.MermaCreate(
        id_sucursal=1,
        detalles=[
            merma_schema.DetalleMermaCreate(id_variante=1, id_motivo=1, cantidad=25)
        ],
    )

    with pytest.raises(HTTPException) as exc_info:
        await merma_service.registrar_merma(payload, user_id=1)

    assert exc_info.value.status_code == 400
    assert "Stock insuficiente" in exc_info.value.detail

