import pytest
from datetime import datetime
from decimal import Decimal
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from app.main import app
from app.db.database import get_db
from app.core import security
from app.db.models import (
    Rol, Usuario, Categoria, Subcategoria, UnidadMedida, Producto, VarianteProducto,
    HistorialPrecio,
)


@pytest.fixture
async def client(db_session):
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c
    app.dependency_overrides.clear()


async def seed_admin_auth(db_session, username="admin_hist"):
    rol = Rol(nombre="Administradora", estado="Activo")
    db_session.add(rol)
    await db_session.flush()
    user = Usuario(
        id_rol=rol.id_rol, nombre_completo="Admin Historial", username=username,
        password_hash=security.get_password_hash("pass123"), estado="Activo",
    )
    db_session.add(user)
    await db_session.commit()
    token = security.create_access_token(data={"sub": user.username, "role": "Administradora", "permissions": []})
    return {"Authorization": f"Bearer {token}"}


async def seed_non_admin_auth(db_session, role_name="Cajera", username="cajera_hist"):
    rol = Rol(nombre=role_name, estado="Activo")
    db_session.add(rol)
    await db_session.flush()
    user = Usuario(
        id_rol=rol.id_rol, nombre_completo=f"{role_name} Historial", username=username,
        password_hash=security.get_password_hash("pass123"), estado="Activo",
    )
    db_session.add(user)
    await db_session.commit()
    token = security.create_access_token(data={"sub": user.username, "role": role_name, "permissions": []})
    return {"Authorization": f"Bearer {token}"}


async def seed_producto_con_historial(db_session, actor):
    cat = Categoria(nombre="Cat Historial", estado="Activo")
    db_session.add(cat)
    await db_session.flush()
    sub = Subcategoria(id_categoria=cat.id_categoria, nombre="Sub Historial", estado="Activo")
    db_session.add(sub)
    await db_session.flush()
    uni = UnidadMedida(codigo="HT", descripcion="Unidad Historial", estado="Activo")
    db_session.add(uni)
    await db_session.flush()
    prod = Producto(id_subcategoria=sub.id_subcategoria, id_unidad=uni.id_unidad,
                    nombre="Producto Historial", estado="Activo")
    db_session.add(prod)
    await db_session.flush()
    var = VarianteProducto(id_producto=prod.id_producto, codigo_barras="HIST-001",
                           precio_detalle=Decimal("50"), precio_mayoreo=Decimal("45"),
                           costo_promedio=Decimal("30"))
    db_session.add(var)
    await db_session.flush()
    db_session.add_all([
        HistorialPrecio(id_variante=var.id_variante, id_usuario=actor.id_usuario,
                        precio_anterior=Decimal("50"), precio_nuevo=Decimal("55"),
                        fecha_modificacion=datetime(2026, 10, 10, 8, 0, 0)),
        HistorialPrecio(id_variante=var.id_variante, id_usuario=actor.id_usuario,
                        precio_anterior=Decimal("55"), precio_nuevo=Decimal("60"),
                        fecha_modificacion=datetime(2026, 10, 12, 9, 30, 0)),
    ])
    await db_session.commit()
    return {"id_producto": prod.id_producto, "id_variante": var.id_variante}


@pytest.mark.asyncio
async def test_historial_precio_api_403_sin_permiso(client, db_session):
    headers = await seed_non_admin_auth(db_session)
    res = await client.get("/api/historial-precios", headers=headers)
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_historial_precio_api_filtra_por_producto(client, db_session):
    headers = await seed_admin_auth(db_session)
    admin = (await db_session.execute(select(Usuario).where(Usuario.username == "admin_hist"))).scalar_one()
    data = await seed_producto_con_historial(db_session, admin)

    # Sin filtros: debe devolver los registros sembrados
    res = await client.get("/api/historial-precios", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert body["total"] == 2
    assert body["items"][0]["producto_nombre"] == "Producto Historial"
    assert body["items"][0]["variante_codigo_barras"] == "HIST-001"
    assert body["items"][0]["usuario_nombre"] == "Admin Historial"

    # Filtrar por producto
    res = await client.get("/api/historial-precios", headers=headers, params={"id_producto": data["id_producto"]})
    body = res.json()
    assert body["total"] == 2

    # Filtrar por variante
    res = await client.get("/api/historial-precios", headers=headers, params={"id_variante": data["id_variante"]})
    body = res.json()
    assert body["total"] == 2

    # Rango de fechas que sólo cubra el segundo registro
    res = await client.get(
        "/api/historial-precios", headers=headers,
        params={"fecha_desde": "2026-10-11", "fecha_hasta": "2026-10-31"},
    )
    body = res.json()
    assert body["total"] == 1
    assert body["items"][0]["precio_nuevo"] == "60.00"


@pytest.mark.asyncio
async def test_historial_precio_registrado_al_actualizar_producto(client, db_session):
    """El servicio de producto debe insertar en historial_precio al cambiar precios."""
    from app.repositories.product_repository import ProductRepositoryImpl
    from app.services.product_service import ConcreteProductService
    from app.schemas import schemas

    user = Usuario(id_rol=1, nombre_completo="Actor", username="actor_hist",
                   password_hash="x", estado="Activo")
    db_session.add(user)
    await db_session.commit()

    cat = Categoria(nombre="Cat Prod", estado="Activo")
    db_session.add(cat)
    await db_session.flush()
    sub = Subcategoria(id_categoria=cat.id_categoria, nombre="Sub Prod", estado="Activo")
    db_session.add(sub)
    await db_session.flush()
    uni = UnidadMedida(codigo="UP", descripcion="Unidad Prod", estado="Activo")
    db_session.add(uni)
    await db_session.flush()
    suc = __import__("app.db.models", fromlist=["Sucursal"]).Sucursal(
        nombre="Suc", direccion="Zona 1", estado="Activo")
    db_session.add(suc)
    await db_session.commit()

    svc = ConcreteProductService(ProductRepositoryImpl(db_session))
    creado = await svc.create_product(
        schemas.ProductoCreate(
            id_subcategoria=sub.id_subcategoria, id_unidad=uni.id_unidad, nombre="Prod Historial",
            variante=schemas.VarianteCreate(
                codigo_barras="HP-1", precio_detalle=Decimal("100"), precio_mayoreo=Decimal("90"),
                costo_promedio=Decimal("60")),
            inventario=schemas.InventarioCreate(id_sucursal=suc.id_sucursal, stock_actual=5, stock_minimo=1),
        ),
        actor_id=user.id_usuario,
    )

    # Cambio de precio de detalle
    await svc.update_product(
        creado.id_producto,
        schemas.ProductoUpdate(variante=schemas.VarianteUpdate(precio_detalle=Decimal("120"))),
        actor_id=user.id_usuario,
    )

    historiales = (await db_session.execute(select(HistorialPrecio))).scalars().all()
    assert len(historiales) == 1
    assert float(historiales[0].precio_anterior) == 100.0
    assert float(historiales[0].precio_nuevo) == 120.0
