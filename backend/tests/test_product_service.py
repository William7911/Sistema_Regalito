from decimal import Decimal
import pytest
from fastapi import HTTPException
from app.repositories.category_repository import CategoryRepositoryImpl
from app.repositories.product_repository import ProductRepositoryImpl
from app.services.product_service import ConcreteProductService
from app.schemas import schemas


def build_service(db_session):
    product_repository = ProductRepositoryImpl(db_session)
    category_repository = CategoryRepositoryImpl(db_session)
    return ConcreteProductService(product_repository, category_repository)


async def create_category(db_session, name="Bebidas"):
    repo = CategoryRepositoryImpl(db_session)
    from app.db.models import Category
    category = Category(name=name)
    return await repo.create(category)


def make_product(category_id, barcode="7501000000001", name="Refresco"):
    return schemas.ProductCreate(
        name=name,
        sku=f"SKU-{barcode}",
        barcode=barcode,
        category_id=category_id,
        price=Decimal("18.50"),
        current_stock=10,
        min_stock=3,
    )


async def test_create_product_requires_valid_category(db_session):
    service = build_service(db_session)
    # La categoría no existe en BD
    with pytest.raises(HTTPException) as exc:
        await service.create_product(make_product(category_id=999))
    assert exc.value.status_code == 400


async def test_create_product_ok(db_session):
    category = await create_category(db_session)
    service = build_service(db_session)

    product = await service.create_product(make_product(category.id))
    assert product.id is not None
    assert product.name == "Refresco"
    assert product.is_active is True
    assert product.category is not None


async def test_duplicate_barcode_rejected(db_session):
    category = await create_category(db_session)
    service = build_service(db_session)

    await service.create_product(make_product(category.id, barcode="7501000000001"))
    with pytest.raises(HTTPException) as exc:
        await service.create_product(make_product(category.id, barcode="7501000000001"))
    assert exc.value.status_code == 400


async def test_get_product_by_barcode_inactive_400(db_session):
    category = await create_category(db_session)
    service = build_service(db_session)

    product = await service.create_product(make_product(category.id, barcode="7501000000002"))
    await service.deactivate_product(product.id)

    with pytest.raises(HTTPException) as exc:
        await service.get_by_barcode("7501000000002")
    assert exc.value.status_code == 400


async def test_update_product_changes_category_from_db(db_session):
    cat_a = await create_category(db_session, name="Bebidas")
    cat_b = await create_category(db_session, name="Jugos")
    service = build_service(db_session)

    product = await service.create_product(make_product(cat_a.id, barcode="7501000000003"))

    updated = await service.update_product(product.id, schemas.ProductUpdate(category_id=cat_b.id, price=Decimal("25.00")))
    assert updated.category_id == cat_b.id
    assert updated.price == Decimal("25.00")

    # Categoría inexistente debe rechazarse
    with pytest.raises(HTTPException) as exc:
        await service.update_product(product.id, schemas.ProductUpdate(category_id=555))
    assert exc.value.status_code == 400


async def test_soft_delete_product(db_session):
    category = await create_category(db_session)
    service = build_service(db_session)

    product = await service.create_product(make_product(category.id, barcode="7501000000004"))
    await service.deactivate_product(product.id)

    deactivated = await service.get_product(product.id)
    assert deactivated.is_active is False


async def test_list_products_filters(db_session):
    category = await create_category(db_session)
    service = build_service(db_session)

    p1 = await service.create_product(make_product(category.id, barcode="7501000000005", name="Refresco Cola"))
    p2 = await service.create_product(make_product(category.id, barcode="7501000000006", name="Refresco Naranja"))
    p3 = await service.create_product(make_product(category.id, barcode="7501000000007", name="Papas Fritas"))

    filters = schemas.ProductFilter(name="Refresco")
    results = await service.list_products(filters)
    assert {p.name for p in results} == {"Refresco Cola", "Refresco Naranja"}

    # Filtro por categoría
    filters_cat = schemas.ProductFilter(category_id=category.id)
    assert len(await service.list_products(filters_cat)) == 3

    # Filtro por estado activo/inactivo
    await service.deactivate_product(p1.id)
    active = await service.list_products(schemas.ProductFilter(is_active=True))
    assert all(p.is_active for p in active)
    inactive = await service.list_products(schemas.ProductFilter(is_active=False))
    assert p1.id in {p.id for p in inactive}

    # Filtro por SKU
    by_sku = await service.list_products(schemas.ProductFilter(sku="SKU-7501000000006"))
    assert [p.id for p in by_sku] == [p2.id]

    # Conteo
    assert await service.count_products(schemas.ProductFilter(name="Refresco")) == 2