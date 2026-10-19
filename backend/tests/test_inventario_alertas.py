"""
Pruebas del endpoint GET /api/inventario/alertas (campanita de notificaciones):
  1. Sin token -> 401.
  2. Autenticado -> 200 con SOLO alertas estado 'Pendiente' enriquecidas con el
     nombre del producto (JOIN alerta_stock → inventario_sucursal →
     variante_producto → producto).
"""
import pytest
from datetime import datetime
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.db.database import get_db
from app.api.deps import get_current_user
from app.db.models import (
    Usuario,
    Categoria,
    Subcategoria,
    UnidadMedida,
    Producto,
    VarianteProducto,
    InventarioSucursal,
    AlertaStock,
)

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def client(db_session):
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c
    app.dependency_overrides.clear()


async def _seed_alertas(db):
    cat = Categoria(id_categoria=1, nombre="Cat1", estado="Activo")
    db.add(cat)
    await db.flush()

    subcat = Subcategoria(id_subcategoria=1, id_categoria=1, nombre="SubCat1")
    db.add(subcat)
    await db.flush()

    unidad = UnidadMedida(id_unidad=1, codigo="U", descripcion="Unidad")
    db.add(unidad)
    await db.flush()

    producto = Producto(id_producto=1, id_subcategoria=1, id_unidad=1, nombre="Producto A", estado="Activo")
    db.add(producto)
    await db.flush()

    variante = VarianteProducto(id_variante=1, id_producto=1, codigo_barras="123", precio_detalle=10, precio_mayoreo=8, costo_promedio=5)
    db.add(variante)
    await db.flush()

    inv = InventarioSucursal(id_inventario=1, id_variante=1, id_sucursal=1, stock_actual=4, stock_minimo=5)
    db.add(inv)
    await db.flush()

    db.add(AlertaStock(id_inventario=1, mensaje="Producto A por debajo del stock mínimo", fecha_generacion=datetime.utcnow(), estado="Pendiente"))
    db.add(AlertaStock(id_inventario=1, mensaje="Producto A por debajo del stock mínimo", fecha_generacion=datetime.utcnow(), estado="Atendida"))
    await db.commit()


async def test_inventario_alertas_requires_auth(client):
    response = await client.get("/api/inventario/alertas")
    assert response.status_code == 401


async def test_inventario_alertas_devuelve_solo_pendientes(client, db_session):
    await _seed_alertas(db_session)
    admin_user = Usuario(
        id_usuario=1, id_rol=1, nombre_completo="Administrador",
        username="admin", password_hash="x", estado="Activo",
    )
    app.dependency_overrides[get_current_user] = lambda: admin_user

    response = await client.get("/api/inventario/alertas")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["estado"] == "Pendiente"
    assert data[0]["producto_nombre"] == "Producto A"
    assert data[0]["variante_sku"] == "123"
    assert data[0]["stock_actual"] == 4
    assert data[0]["stock_minimo"] == 5