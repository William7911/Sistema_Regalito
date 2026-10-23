from decimal import Decimal
import pytest
from fastapi import HTTPException
from app.db.models import Categoria, Subcategoria, UnidadMedida, Sucursal
from app.repositories.product_repository import ProductRepositoryImpl
from app.services.product_service import ConcreteProductService
from app.schemas import schemas


def build_service(db_session):
    product_repository = ProductRepositoryImpl(db_session)
    return ConcreteProductService(product_repository)


async def seed_dependencies(db_session):
    cat = Categoria(nombre="Ropa", estado="Activo")
    db_session.add(cat)
    await db_session.flush()

    subcat = Subcategoria(id_categoria=cat.id_categoria, nombre="Pantalones", estado="Activo")
    db_session.add(subcat)

    unidad = UnidadMedida(codigo="PZA", descripcion="Pieza", estado="Activo")
    db_session.add(unidad)

    sucursal = Sucursal(nombre="Sucursal Central", direccion="Zona 1", estado="Activo")
    db_session.add(sucursal)
    await db_session.flush()

    return subcat.id_subcategoria, unidad.id_unidad, sucursal.id_sucursal


def make_product(id_subcategoria, id_unidad, id_sucursal, barcode="740100000001", nombre="Pantalón Jeans"):
    return schemas.ProductoCreate(
        id_subcategoria=id_subcategoria,
        id_unidad=id_unidad,
        nombre=nombre,
        descripcion="Pantalón casual",
        variante=schemas.VarianteCreate(
            codigo_barras=barcode,
            talla="32",
            color="Azul",
            precio_detalle=Decimal("150.00"),
            precio_mayoreo=Decimal("130.00"),
            costo_promedio=Decimal("80.00"),
        ),
        inventario=schemas.InventarioCreate(
            id_sucursal=id_sucursal,
            stock_actual=10,
            stock_minimo=3,
        ),
    )


@pytest.mark.asyncio
async def test_crear_producto_requiere_subcategoria_valida(db_session):
    _, id_unidad, id_sucursal = await seed_dependencies(db_session)
    svc = build_service(db_session)
    with pytest.raises(HTTPException) as exc:
        await svc.create_product(make_product(9999, id_unidad, id_sucursal))
    assert exc.value.status_code == 400
    assert "subcategoría" in exc.value.detail.lower()


@pytest.mark.asyncio
async def test_crear_producto_exitoso(db_session):
    id_sub, id_uni, id_suc = await seed_dependencies(db_session)
    svc = build_service(db_session)
    creado = await svc.create_product(make_product(id_sub, id_uni, id_suc, barcode="740100000002"))
    assert creado.id_producto is not None
    assert creado.nombre == "Pantalón Jeans"
    assert creado.estado == "Activo"
    assert len(creado.variantes) == 1
    assert creado.variantes[0].codigo_barras == "740100000002"


@pytest.mark.asyncio
async def test_codigo_barras_duplicado_rechazado(db_session):
    id_sub, id_uni, id_suc = await seed_dependencies(db_session)
    svc = build_service(db_session)
    await svc.create_product(make_product(id_sub, id_uni, id_suc, barcode="740100000003"))
    with pytest.raises(HTTPException) as exc:
        await svc.create_product(make_product(id_sub, id_uni, id_suc, barcode="740100000003"))
    assert exc.value.status_code == 400
    assert "código de barras" in exc.value.detail.lower()


@pytest.mark.asyncio
async def test_obtener_producto_por_id(db_session):
    id_sub, id_uni, id_suc = await seed_dependencies(db_session)
    svc = build_service(db_session)
    creado = await svc.create_product(make_product(id_sub, id_uni, id_suc, barcode="740100000004"))
    obtenido = await svc.get_product(creado.id_producto)
    assert obtenido.id_producto == creado.id_producto
    assert obtenido.nombre == creado.nombre


@pytest.mark.asyncio
async def test_obtener_producto_por_codigo_barras(db_session):
    id_sub, id_uni, id_suc = await seed_dependencies(db_session)
    svc = build_service(db_session)
    creado = await svc.create_product(make_product(id_sub, id_uni, id_suc, barcode="740100000005"))
    obtenido = await svc.get_by_barcode("740100000005")
    assert obtenido.id_producto == creado.id_producto


@pytest.mark.asyncio
async def test_desactivar_producto_soft_delete(db_session):
    id_sub, id_uni, id_suc = await seed_dependencies(db_session)
    svc = build_service(db_session)
    creado = await svc.create_product(make_product(id_sub, id_uni, id_suc, barcode="740100000006"))
    desactivado = await svc.deactivate_product(creado.id_producto)
    assert desactivado.estado == "Inactivo"

    with pytest.raises(HTTPException) as exc:
        await svc.get_by_barcode("740100000006")
    assert exc.value.status_code == 400
    assert "inactivo" in exc.value.detail.lower()

